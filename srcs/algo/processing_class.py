import json
import os
import pathlib
from functools import wraps
from threading import Thread

import cv2
import numpy as np

from algo.dpf_to_midi import dpf_data_to_midi
from algo.get_watch_cords import get_watch_cords_dict
from algo.locate_black_and_white import locate_keys_like, classify_keys
from algo.process_video import draw_keys as draw_keys_with_dpf
from algo.process_video import process_video_func
from algo.utils import SettableCachedProperty
from algo import utils
from algo.video_class import VideoClass
from algo.download_videos import download_video, is_valid_url, get_video_title
from algo.wait_and_find_keys import draw_keys as draw_keys_raw
from p2m import p2m_path
from p2m.p2m_exception import *
from p2m.p2m_types import *


class ProcessStates:
    NOT_STARTED = "Not Started"
    RUNNING = "Loading"
    DOWNLOADING_VIDEO = "Downloading video"
    FINDING_KEYS = "Finding Piano Keys"
    FAILED_TO_FIND_KEYS = "Failed to find piano keys"
    PROCESSING_VIDEO = "Processing video"
    GENERATING_MIDI = "Generating midi"
    COMPLETED = "Completed"
    ERROR = "Error"
    UNKNOWN = "Unknown"


def state_method(start_state: Optional[str] = None):
    state_varname = "state"
    active_calls_varname = "_active_state_calls"

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            original_state = getattr(self, state_varname, ProcessStates.UNKNOWN)
            setattr(self, active_calls_varname, getattr(self, active_calls_varname, 0) + 1)

            if start_state is not None:
                setattr(self, state_varname, start_state)
            else:
                setattr(self, state_varname, ProcessStates.RUNNING)
            try:
                ret = method(self, *args, **kwargs)
            except KeysNotFoundError as exc:
                setattr(self, state_varname, ProcessStates.FAILED_TO_FIND_KEYS)
                raise exc
            except BaseException as exc:
                setattr(self, state_varname, ProcessStates.ERROR)
                raise exc
            finally:
                setattr(self, active_calls_varname, getattr(self, active_calls_varname) - 1)
            if getattr(self, active_calls_varname) == 0:
                setattr(self, state_varname, ProcessStates.COMPLETED)
            else:
                setattr(self, state_varname, original_state)
            return ret

        return wrapper

    return decorator


# Combination of state_method and SettableCachedProperty
def state_cached_property(start_state: Optional[str] = None):
    def combined_decorator(method):
        return SettableCachedProperty(state_method(start_state)(method))

    return combined_decorator


class HookHandler:
    def __init__(self, *hooks):
        self._hooked_functions: list[Callable] = list(hooks)

    def hook(self, func: Callable):
        self._hooked_functions.append(func)

    def call(self, *args, **kwargs):
        for func in self._hooked_functions:
            func(*args, **kwargs)


class ProcessingClass:
    def __init__(self, src_str: str):  #, title: Optional[str] = None):
        self.src_str: str = src_str
        self._state: str = ProcessStates.NOT_STARTED
        self.state_hooks: HookHandler = HookHandler()
        # if title:
        #     self.title = title

        # self.save_as_path: str = save_as_path
        # self.fps: Optional[float] = None
        self._video_ref: Optional[VideoClass] = None
        self._download_progress: float = 0.0
        self._unconfirmed_keys: list[RectType] = []
        self._white_keys: list[RectType] = []
        self._black_keys: list[RectType] = []
        self.watch_cords_dict: dict[RectType, list[CordType]] = {}
        self.watch_cords_list: list[RectType] = []
        self.watch_cords_values: list[list[CordType]] = []
        self._dpf_raw: list[np.ndarray] = []
        # self.diff_per_frame: list[list[int]] = []
        # self.midi: Optional[mido.MidiFile] = None

        self._task_queue: list[tuple[Callable, tuple, dict]] = []

    @SettableCachedProperty
    def title(self):
        path = pathlib.Path(self.src_str)
        if path.exists() and path.is_file():
            ret = path.stem
        elif is_valid_url(self.src_str):
            ret = get_video_title(self.src_str)
        else:
            ret = "Unnamed"
        return utils.clean_filename(ret)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
        self.state_hooks.call()

    def is_failed(self):
        return self._state in (ProcessStates.ERROR, ProcessStates.FAILED_TO_FIND_KEYS)

    def is_completed(self):
        return self._state is ProcessStates.COMPLETED

    def is_idle(self):
        return self.is_completed() or self.is_failed() or self._state is ProcessStates.NOT_STARTED

    def get_dpf_filepath(self):
        filename = self.title  # self.src_str.replace(":", "").replace("\\", "_").replace("/", "_")
        filename = utils.clean_filename(filename)
        return os.path.join(p2m_path.DPF_DIR, f'{filename}.dpf.json')

    @state_method(start_state=ProcessStates.DOWNLOADING_VIDEO)
    def _download_and_get_video_path(self) -> str:
        def update_progress(progress: float):
            self._download_progress = progress
        return download_video(self.src_str, p2m_path.VIDEOS_DIR, self.title, progress_hook_func=update_progress)

    @SettableCachedProperty
    def video_path(self):
        if os.path.exists(self.src_str):
            return self.src_str
        elif is_valid_url(self.src_str):
            return self._download_and_get_video_path()
        else:
            raise RuntimeError("unable to get video path")

    @SettableCachedProperty
    def video(self) -> VideoClass:
        vid = VideoClass(self.video_path)
        self._video_ref = vid
        return vid

    @SettableCachedProperty
    def fps(self):
        return self.video.fps

    @state_method(start_state=ProcessStates.FINDING_KEYS)
    def find_black_and_white_keys(self):
        while self.video.read_next():
            self._unconfirmed_keys[:] = locate_keys_like(self.video.current_frame)
            classified_keys = classify_keys(self._unconfirmed_keys)
            if classified_keys is None:
                continue
            self._white_keys[:], self._black_keys[:] = classified_keys
            # print("found keys", self.white_keys, self.black_keys)
            return
        raise KeysNotFoundError(self.src_str)

    @state_cached_property(start_state=ProcessStates.PROCESSING_VIDEO)
    def diff_per_frame(self):
        if not self._white_keys or not self._black_keys:
            self.find_black_and_white_keys()
        self.watch_cords_dict.update(get_watch_cords_dict(self._white_keys, self._black_keys))
        self.watch_cords_list[:] = list(self.watch_cords_dict.keys())
        self.watch_cords_values[:] = list(self.watch_cords_dict.values())
        self._dpf_raw[:] = [np.full(len(self.watch_cords_dict), 0)]
        process_video_func(self.video, self.watch_cords_dict, self._black_keys, self._dpf_raw)
        return np.diff(np.array(self._dpf_raw), axis=0).astype(int).tolist()

    @state_method()
    def read_dpf_from_history(self):
        with open(self.get_dpf_filepath(), "r") as f:
            data = json.load(f)
        self.fps = data['fps']
        self.diff_per_frame = data['dpf']

    @state_cached_property()
    def midi(self):
        return dpf_data_to_midi(self.fps, self.diff_per_frame)

    @state_method()
    def save_dpf_data(self):
        filepath = self.get_dpf_filepath()
        pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w+') as f:
            data_dict = {"fps": self.fps, "dpf": self.diff_per_frame}
            json.dump(data_dict, f)

    @state_method()
    def save_as(self, abs_path):
        pathlib.Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        self.save_dpf_data()
        self.midi.save(abs_path)

    def add_task(self, target: Callable, *args, **kwargs):
        self._task_queue.append((target, args, kwargs))

    @state_method()
    def do_tasks(self):
        while self._task_queue:
            func, args, kwargs = self._task_queue.pop(0)
            func(*args, **kwargs)

    def get_displayed_frame(self):
        if self._video_ref is None:
            return np.zeros((720, 1280, 3), dtype=np.uint8)
        img = self._video_ref.current_frame
        if img is None:
            return self._video_ref.get_thumbnail()
        img = img.copy()
        if self.watch_cords_list and self._dpf_raw:
            return draw_keys_with_dpf(img, self._dpf_raw[-1], self.watch_cords_list)
        return draw_keys_raw(img, self._white_keys, self._black_keys, self._unconfirmed_keys)

    def get_progress(self) -> float:
        """

        :return: progress 0.0 - 1.0
        """
        if self._video_ref and self._state is ProcessStates.FINDING_KEYS:
            return self._video_ref.get_progress()
        if self._video_ref and self._state is ProcessStates.PROCESSING_VIDEO:
            return self._video_ref.get_progress()
        if self._state is ProcessStates.DOWNLOADING_VIDEO:
            return self._download_progress
        if self._state is ProcessStates.COMPLETED:
            return 1.0
        return 0.0


def test():
    video_path = r"https://www.youtube.com/watch?v=0gsKxV3dmkU"
    save_path = p2m_path.DATA_DIR + "/test.mid"

    p = ProcessingClass(video_path)

    print("starting thread")
    t = Thread(target=p.save_as, args=(save_path, ))
    t.start()
    # while p.state != ProcessStates.COMPLETED:
    #     print(p.state)
    # return
    while p.is_idle():
        ...
    print("started")
    while not p.is_idle():
        frame = p.get_displayed_frame()
        if frame is not None:
            cv2.imshow("test", frame)
            cv2.waitKey(1)
        print(p.state)

    t.join()
    print("ended")


if __name__ == '__main__':
    test()
