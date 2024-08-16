import mido

from p2m import p2m_constants


def dpf_data_to_midi(source_video_fps: float, difference_per_frame: list[list[int]]):
    dpf = difference_per_frame
    fps = source_video_fps
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)

    tempo = mido.bpm2tempo(240)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    note_on_velocity = 64
    note_off_velocity = 0

    time_per_frame = mido.second2tick(1 / fps, ticks_per_beat=midi.ticks_per_beat, tempo=tempo)

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

    return midi
