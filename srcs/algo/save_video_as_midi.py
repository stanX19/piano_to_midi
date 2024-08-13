import os
import easygui
import json
import pathlib
from p2m import p2m_path
from p2m.p2m_types import *
from algo.process_video import get_dpf
from algo.classes import VideoClass
from algo.wait_and_find_keys import wait_and_find_keys
from algo.get_watch_cords import get_watch_cords_dict
from p2m.p2m_exception import *
from p2m import p2m_constants
import mido


def _input_with_default(prompt, default):
    user_input = input(f"{prompt} ({default}): ")
    if user_input == "":
        return default
    return user_input


def _basename(path: str) -> str:
    return pathlib.Path(path).stem


def generate_p2m_dpf_filepath(video_path: str):
    return os.path.join(p2m_path.data, f'dpf/{_basename(video_path)}.dpf.json')


def load_dpf_from_history(video_path: str):
    with open(generate_p2m_dpf_filepath(video_path), 'r') as f:
        data = json.load(f)

    return data["fps"], data["dpf"]


def video_to_dpf_data(video_path: str) -> tuple[float, DpfType]:
    video = VideoClass(video_path)
    keys = wait_and_find_keys(video)
    watch_cords_dict = get_watch_cords_dict(*keys)
    dpf = get_dpf(video, watch_cords_dict, keys, show_video=True)
    diff_per_frame_data = video.fps, dpf
    video.release()

    filepath = generate_p2m_dpf_filepath(video_path)
    pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w+') as f:
        data_dict = {"fps": diff_per_frame_data[0], "dpf": diff_per_frame_data[1]}
        json.dump(data_dict, f)

    return diff_per_frame_data


def save_dpf_data_as_midi(name: str, source_video_fps: int, difference_per_frame: list[list[int]], directory: str):
    dpf = difference_per_frame
    fps = source_video_fps
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)

    tempo = mido.bpm2tempo(240)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    note_on_velocity = 64
    note_off_velocity = 0

    time_per_frame = mido.second2tick(1/fps, ticks_per_beat=midi.ticks_per_beat, tempo=tempo)

    note_on_record = {}
    time_bucket = 0.0

    def add_note_off(_note: int):
        nonlocal time_bucket, note_on_record
        if note_on_record.get(_note, 0) == 0:
            return
        track.append(mido.Message('note_off', note=_note, velocity=note_off_velocity, time=int(time_bucket)))
        time_bucket -= int(time_bucket)
        note_on_record[_note] = 0

    def add_note_on(_note: int):
        nonlocal time_bucket, note_on_record
        if note_on_record.get(_note, 0) == 1:
            add_note_off(_note)
        track.append(mido.Message('note_on', note=_note, velocity=note_on_velocity, time=int(time_bucket)))
        time_bucket -= int(time_bucket)
        note_on_record[_note] = 1

    for frame_idx, frame_diff in enumerate(dpf[:-1]):
        time_bucket += time_per_frame
        for key_idx, brightness_diff in enumerate(frame_diff):
            note = 24 + key_idx  # Low C (24) as the base note

            if brightness_diff > p2m_constants.ON_THRESHOLD:
                add_note_on(note)
            elif brightness_diff < -p2m_constants.OFF_THRESHOLD:
                add_note_off(note)

    for msg in track:
        msg.time = 0
        if msg.type == 'note_on':
            break
    # Save the MIDI file
    filepath = f"{directory}/{name}.mid"
    midi.save(filepath)
    print(f"saved as {filepath}")


def _convert_one(video_path: str, name: str, use_history: bool, directory: str):
    print(f"Processing {name}")
    if use_history:
        fps, dpf = load_dpf_from_history(video_path)
    else:
        fps, dpf = video_to_dpf_data(video_path)
    save_dpf_data_as_midi(name, fps, dpf, directory)


def prompt_for_details(path: str) -> tuple[str, str, bool]:
    # Define the filepath for the existing processing record
    dpf_filepath = generate_p2m_dpf_filepath(path)

    # Check if the file exists and prompt the user accordingly
    if os.path.exists(dpf_filepath):
        msg = f"""History found for

    "{pathlib.Path(path).name}"

Skip video processing?"""
        choice = easygui.buttonbox(
            msg, title="Processing Record Found", choices=['cancel', 'no', 'yes'], cancel_choice='cancel'
        )
        if choice == 'cancel':
            raise OperationCancelledException()
        use_history = (choice == 'yes')
    else:
        use_history = False

    # Prompt for the name of the video with a default value
    name = easygui.enterbox(
        msg=f"Video path: \"{path}\"\n{'[ Use history: Yes ]' if use_history else ''}\nName: ",
        default=_basename(path)
    )
    if name is None:
        raise OperationCancelledException()
    name = name.strip()
    return path, name, use_history


def save_video_as_midi(dst_path: str, video_paths: Union[list[str], None] = None):
    if video_paths is None:
        video_paths = easygui.fileopenbox("select designated 720p mp4 file", "Select Video",
                                          "D:\\Downloads\\", filetypes=["*.mp4"], multiple=True)
    if video_paths is None:
        return
    if any(not p.endswith(".mp4") for p in video_paths):
        easygui.msgbox("Selected file must be in mp4 format", "Error")
        return
    queue: list[tuple[str, str, bool]] = []

    for path in video_paths:
        try:
            args = prompt_for_details(path)
        except OperationCancelledException:
            continue
        queue.append(args)

    if not queue:
        return

    success = 0
    for args in queue:
        try:
            _convert_one(*args, directory=dst_path)
            success += 1
        except Exception as exc:
            print("Error: ", exc)

    if success:
        easygui.msgbox(f"Files have been saved to {dst_path}", "Processing Complete")
    else:
        input("Press enter to exit")


if __name__ == '__main__':
    save_video_as_midi(p2m_path.data, [r"..\assets\amygdala_piano.mp4"])
    # save_video_as_midi(p2m_path.data)

