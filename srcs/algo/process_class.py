import cv2
import os
import time
import numpy as np
import pathlib
from typing import Optional, Union
from algo import utils
from .video_class import VideoClass
from p2m import p2m_path
from p2m.p2m_types import *
from algo.process_video import process_video_func
from algo.process_video import draw_keys as draw_keys_with_dpf
from algo.wait_and_find_keys import draw_keys as draw_keys_raw
from algo.locate_black_and_white import locate_keys_like, classify_keys
from algo.get_watch_cords import get_watch_cords_dict
from algo.dpf_to_midi import dpf_data_to_midi
from p2m.p2m_exception import *
from p2m import p2m_constants
import mido
import json
from threading import Thread
from functools import wraps
from typing import Callable, Dict


class ProcessStates:
    NOT_STARTED = "Not Started"
    FINDING_KEYS = "Finding Keys"
    FAILED_TO_FIND_KEYS = "Failed to find keys"
    PROCESSING_VIDEO = "Processing video"
    GENERATING_MIDI = "Generating midi"
    COMPLETED = "Completed"
    ERROR = "Error"
    UNKNOWN = "Unknown"


def step_method(dependency: Optional[dict[str, Callable]] = None,
                start_state: Optional[str] = None,
                error_state: str = ProcessStates.ERROR):
    if dependency is None:
        dependency = {}
    state_varname = "_state"

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, __is_parent=True, **kwargs):
            if start_state is not None:
                setattr(self, state_varname, start_state)
            try:
                for attr, func in dependency.items():
                    if not getattr(self, attr):
                        func(self, __is_parent=False)
                ret = method(self, *args, **kwargs)
            except BaseException as exc:
                setattr(self, state_varname, error_state)
                raise exc
            if __is_parent:
                setattr(self, state_varname, ProcessStates.COMPLETED)
            return ret
        return wrapper
    return decorator


class ProcessingClass:
    def __init__(self, path: str, save_as_path: str):
        self.video_path: str = path
        self.save_as_path: str = save_as_path
        self.video: Optional[VideoClass] = None
        self.fps: Optional[float] = None
        self._state = ProcessStates.NOT_STARTED

        self._unconfirmed_keys: list[RectType] = []
        self.white_keys: list[RectType] = []
        self.black_keys: list[RectType] = []
        self.watch_cords_dict: dict[RectType, list[CordType]] = {}
        self.watch_cords_list: list[RectType] = []
        self.watch_cords_values: list[list[CordType]] = []
        self._dpf_raw: list[np.ndarray] = []
        self.diff_per_frame: list[list[int]] = []
        self.midi: Optional[mido.MidiFile] = None

        self._thread: Optional[Thread] = None

    @property
    def state(self):
        return self._state
    
    def is_completed(self):
        return self._state in (ProcessStates.COMPLETED, ProcessStates.ERROR, ProcessStates.FAILED_TO_FIND_KEYS)

    def get_dpf_filepath(self):
        return os.path.join(p2m_path.data, f'dpf/{self.video_path}.dpf.json')

    @step_method()
    def get_video(self):
        self.video = VideoClass(self.video_path)

    @step_method({
        "video": get_video
    })
    def get_fps(self):
        self.fps = self.video.fps

    @step_method({
        "video": get_video
    }, start_state=ProcessStates.FINDING_KEYS, error_state=ProcessStates.FAILED_TO_FIND_KEYS)
    def find_black_and_white_keys(self):
        while self.video.read_next():
            self._unconfirmed_keys[:] = locate_keys_like(self.video.current_frame)
            classified_keys = classify_keys(self._unconfirmed_keys)
            if classified_keys is None:
                continue
            self.white_keys[:], self.black_keys[:] = classified_keys
            # print("found keys", self.white_keys, self.black_keys)
            return
        raise KeysNotFoundError(self.video_path)

    @step_method({
        "video": get_video,
        'white_keys': find_black_and_white_keys,
        'black_keys': find_black_and_white_keys,
    }, start_state=ProcessStates.PROCESSING_VIDEO)
    def generate_dpf_data(self):
        self.watch_cords_dict.update(get_watch_cords_dict(self.white_keys, self.black_keys))
        self.watch_cords_list[:] = list(self.watch_cords_dict.keys())
        self.watch_cords_values[:] = list(self.watch_cords_dict.values())
        self._dpf_raw[:] = [np.full(len(self.watch_cords_dict), 0)]
        process_video_func(self.video, self.watch_cords_dict, self.black_keys, self._dpf_raw)
        self.diff_per_frame[:] = np.diff(np.array(self._dpf_raw), axis=0).astype(int).tolist()

    def read_dpf_from_history(self):
        with open(self.get_dpf_filepath(), "r") as f:
            data = json.load(f)
        self.fps = data['fps']
        self.diff_per_frame = data['dpf']

    @step_method({
        'diff_per_frame': generate_dpf_data,
        "fps": get_fps,
    })
    def generate_midi(self):
        self.midi = dpf_data_to_midi(self.fps, self.diff_per_frame)

    @step_method({
        'diff_per_frame': generate_dpf_data,
        "fps": get_fps,
    })
    def save_dpf_data(self):
        filepath = self.get_dpf_filepath()
        pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w+') as f:
            data_dict = {"fps": self.fps, "dpf": self.diff_per_frame}
            json.dump(data_dict, f)

    @step_method({
        "midi": generate_midi
    })
    def save_as(self, abs_path):
        self.midi.save(abs_path)

    def run(self):
        self.find_black_and_white_keys()
        self.generate_dpf_data()
        self.save_dpf_data()
        self.generate_midi()
        self.save_as(self.save_as_path)
        self._state = ProcessStates.COMPLETED
    #
    # def _thread_func(self, complete_callback: Optional[Callable]):
    #     self.run()
    #     if complete_callback:
    #         complete_callback()
    #
    # def run_in_thread(self, complete_callback: Optional[Callable] = None):
    #     self._thread = Thread(target=self._thread_func, args=(complete_callback,))
    #     self._thread.start()
    #
    # def join_completed_thread(self):
    #     if self._thread:
    #         self._thread.join()
    #     self._thread = None

    def get_displayed_frame(self):
        if self.video is None:
            return None
        img = self.video.current_frame
        if img is None:
            return None
        img = img.copy()
        if self.watch_cords_list and self._dpf_raw:
            return draw_keys_with_dpf(img, self._dpf_raw[-1], self.watch_cords_list)
        return draw_keys_raw(img, self.white_keys, self.black_keys, self._unconfirmed_keys)

    def get_progress(self) -> float:
        """

        :return: progress 0.0 - 1.0
        """
        if self.video and self._state is ProcessStates.FINDING_KEYS:
            return self.video.get_progress()
        if self.video and self._state is ProcessStates.PROCESSING_VIDEO:
            return self.video.get_progress()
        if self._state is ProcessStates.COMPLETED:
            return 1.0
        return 0.0


def test():
    video_path = "../../../assets/amygdala_piano.mp4"
    save_path = "../../../data/test.mid"

    p = ProcessingClass(video_path, save_path)

    print("starting thread")
    t = Thread(target=p.generate_midi)
    t.start()
    # while p.state != ProcessStates.COMPLETED:
    #     print(p.state)
    # return
    print("started")

    while not p.is_completed():
        frame = p.get_displayed_frame()
        if frame is not None:
            cv2.imshow("test", frame)
            cv2.waitKey(1)
        print(p.state)

    t.join()
    print("ended")


if __name__ == '__main__':
    test()
