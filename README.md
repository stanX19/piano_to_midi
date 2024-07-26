# piano to midi

A project designed to convert piano Synthesia videos into MIDI files.

## Installation

```commandline
git clone git@github.com:stanX19/piano_to_midi.git piano_to_midi
cd piano_to_midi
py -m pip install -r requirements.txt
```

## Usage

To run the program, execute:

```commandline
py srcs/main.py
```

The program will open a GUI for file selection, supporting multiple files.

## Description

This project uses cv2 to detect piano keys and track changes in BGR values across frames.

##### Key points:

- The program monitors pixel value changes frame-by-frame, so a higher frame rate will improve accuracy.
- The difference in BGR values per frame (DPF) is stored in `./data/dpf` as cache.
- After processing, the program converts the DPF data into a MIDI file, which is saved by default in the `./data` directory.
