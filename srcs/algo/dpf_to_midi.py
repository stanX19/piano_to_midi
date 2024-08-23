import mido
import statistics
from p2m import p2m_constants


class DpfToMidiConverter:
    def __init__(self, source_video_fps: float, difference_per_frame: list[list[int]]):
        self.source_video_fps = source_video_fps
        self.difference_per_frame = difference_per_frame
        self.midi = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.midi.tracks.append(self.track)
        self.note_on_velocity = 64
        self.note_off_velocity = 0
        self.time_bucket = 0.0
        self.note_on_record: dict[int, bool] = {}
        self.note_times: list[int] = []
        self.future_look_frames = 0

    def get_note_times(self):
        record = {}
        note_times = []

        for frame_idx, frame_diff in enumerate(self.difference_per_frame):
            for key in record:
                record[key] += 1
            for key_idx, brightness_diff in enumerate(frame_diff):
                if brightness_diff > p2m_constants.ON_THRESHOLD:
                    record[key_idx] = 0
                elif brightness_diff < -p2m_constants.OFF_THRESHOLD and key_idx in record:
                    note_times.append(record[key_idx])
                    del record[key_idx]

        return note_times

    def add_note_off(self, note: int):
        if not self.note_on_record.get(note, False):
            return
        self.track.append(mido.Message('note_off', note=note, velocity=self.note_off_velocity, time=int(self.time_bucket)))
        self.time_bucket -= int(self.time_bucket)
        self.note_on_record[note] = False

    def add_note_on(self, note: int):
        self.add_note_off(note)
        self.track.append(mido.Message('note_on', note=note, velocity=self.note_on_velocity, time=int(self.time_bucket)))
        self.time_bucket -= int(self.time_bucket)
        self.note_on_record[note] = True

    # deprecated
    def add_future_note_on(self, frame_idx, key_idx, note):
        for frame_diff in self.difference_per_frame[frame_idx: frame_idx + self.future_look_frames]:
            brightness_diff = frame_diff[key_idx]  # Adjust index for note range
            if brightness_diff > p2m_constants.ON_THRESHOLD:
                self.add_note_on(note)
                frame_diff[key_idx] = 0  # Prevent duplicate note-on events
                print("future note on triggered")
                return

    def convert_to_midi(self):
        note_times = sorted(self.get_note_times())

        dominant_note_length = statistics.multimode(note_times)[0]
        spf = 1 / self.source_video_fps
        seconds_per_beat = dominant_note_length * spf
        bpm = 60 / seconds_per_beat

        tempo = mido.bpm2tempo(bpm)
        self.track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        fps = self.source_video_fps
        time_per_frame = mido.second2tick(1 / fps, ticks_per_beat=self.midi.ticks_per_beat, tempo=tempo)

        # deprecated, it dont even activate
        self.future_look_frames = round(fps / 15)

        for frame_idx, frame_diff in enumerate(self.difference_per_frame):
            self.time_bucket += time_per_frame
            for key_idx, brightness_diff in enumerate(frame_diff):
                note = 24 + key_idx  # Low C (24) as the base note

                if brightness_diff > p2m_constants.ON_THRESHOLD:
                    self.add_note_on(note)
                elif brightness_diff < -p2m_constants.OFF_THRESHOLD:
                    self.add_note_off(note)
                    # self.add_future_note_on(frame_idx, key_idx, note)

        # Ensure the first event has zero time
        for msg in self.track:
            msg.time = 0
            if msg.type == 'note_on':
                break

        return self.midi


def dpf_data_to_midi(source_video_fps: float, difference_per_frame: list[list[int]]):
    converter = DpfToMidiConverter(source_video_fps, difference_per_frame)
    return converter.convert_to_midi()
