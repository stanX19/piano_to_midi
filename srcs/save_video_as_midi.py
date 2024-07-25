import os
import easygui
import json
import pathlib
import my_path
from my_types import *
from process_video import get_dpf
from video_class import VideoClass
from wait_and_find_keys import wait_and_find_keys
from get_watch_cords import get_watch_cords_dict
import mido


def input_with_default(prompt, default):
    user_input = input(f"{prompt} ({default}): ")
    if user_input == "":
        return default
    return user_input


def basename(path: str) -> str:
    path = path.replace("\\", "/")
    return os.path.basename(os.path.splitext(path)[0])


def generate_dpf_filepath(video_path: str):
    return os.path.join(my_path.data, f'dpf/{basename(video_path)}.dpf.json')


def load_dpf_from_history(video_path: str):
    with open(generate_dpf_filepath(video_path), 'r') as f:
        data = json.load(f)

    return data["fps"], data["dpf"]


def video_to_dpf_data(video_path: str, start=1) -> tuple[float, DpfType]:
    video = VideoClass(video_path)
    keys = wait_and_find_keys(video)
    watch_cords_dict = get_watch_cords_dict(*keys)
    dpf = get_dpf(video, watch_cords_dict, keys)
    diff_per_frame_data = video.fps, dpf

    filepath = generate_dpf_filepath(video_path)
    pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w+') as f:
        data_dict = {"fps": diff_per_frame_data[0], "dpf": diff_per_frame_data[1]}
        json.dump(data_dict, f)

    return diff_per_frame_data


def save_dpf_data_as_midi(name: str, diff_per_frame_data: tuple[float, list[list[int]]], directory: str):
    fps, dpf = diff_per_frame_data

    # Create a new MIDI file and add a track
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)

    # Set the tempo (microseconds per beat)
    tempo = mido.bpm2tempo(128)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    threshold = 50
    note_on_velocity = 64  # Velocity for note on messages
    note_off_velocity = 64  # Velocity for note off messages

    time_per_frame = mido.second2tick(1/fps, ticks_per_beat=midi.ticks_per_beat, tempo=tempo)

    # Convert dpf data to MIDI events
    time_bucket = 0.0
    for frame_idx, frame_diff in enumerate(dpf[:-1]):
        next_frame_diff = dpf[frame_idx + 1]
        time_bucket += time_per_frame
        for key_idx, brightness_diff in enumerate(frame_diff):
            # Convert key_idx to MIDI note number (example: map to a range of notes)
            note = 24 + key_idx  # Low C (24) as the base note

            if brightness_diff > threshold:
                # Increase in brightness: Note on
                track.append(mido.Message('note_on', note=note, velocity=note_on_velocity, time=int(time_bucket)))
                time_bucket -= int(time_bucket)
            elif brightness_diff < -threshold:
                # Decrease in brightness: Note off
                track.append(mido.Message('note_off', note=note, velocity=note_off_velocity, time=int(time_bucket)))
                time_bucket -= int(time_bucket)

                # special case, no gap
                if next_frame_diff[key_idx] > threshold:
                    next_frame_diff[key_idx] = 0
                    track.append(mido.Message('note_on', note=note, velocity=note_on_velocity, time=int(time_bucket)))
                    time_bucket -= int(time_bucket)

    # Save the MIDI file
    midi.save(f"{directory}/{name}.mid")
    print(f"saved as {directory}/{name}.mid")


def _convert_one(video_path: str, name: str, use_history: bool, directory: str):
    print(f"Processing {name}")
    if use_history:
        dpf_data = load_dpf_from_history(video_path)
    else:
        dpf_data = video_to_dpf_data(video_path)
    save_dpf_data_as_midi(name, dpf_data, directory)


def prompt_for_details(path: str) -> list[str, str, bool]:
    if os.path.exists(generate_dpf_filepath(path)):
        enter = ""
        while enter not in ["y", "yes", "n", "no"]:
            enter = input("Previous processing record found, skip video processing? [Y/n]: ").lower().strip()
        use_history = enter in ["y", "yes"]
    else:
        use_history = 0

    name = input_with_default(f"Video path: {path}\nname?", default=basename(path)).strip()

    return [path, name, use_history]


def save_video_as_midi(dst_path: str, video_path: Union[list, None] = None):
    if video_path is None:
        video_path = easygui.fileopenbox("select designated 720p mp4 file", "Select Video",
                                         "D:\\Downloads\\", filetypes=["*.mp4"], multiple=True)
    if video_path is None:
        return
    if not any(p.endswith(".mp4") for p in video_path):
        print("Error: Selected file should be mp4 format")
        return
    queue: list[list[str, str, bool]] = []

    for path in video_path:
        args = prompt_for_details(path)
        queue.append(args)

    for args in queue:
        try:
            _convert_one(*args, directory=dst_path)
        except Exception as exc:
            print(exc)

    if not queue:
        print("???")


if __name__ == '__main__':
    save_video_as_midi(my_path.data, ["../assets/amygdala_piano.mp4"])
