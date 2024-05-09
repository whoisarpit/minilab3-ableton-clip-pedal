# MiniLab 3 Sustain Pedal Script for Ableton Live

This Python script allows you to use a sustain pedal with your Arturia MiniLab 3 MIDI controller to trigger clips on Ableton Live.

## Prerequisites

[Python 3.10](https://www.python.org/downloads/) or higher is required to run the script.

## Installation

You can install the required dependencies using pip:

```bash
pip install rtmidi
```

## Usage

To use the script, you can run it from the command line with the following options:

```bash
python midi.py [-h] [-l LOG] [-s SOURCE] [-b LOOPBACK] [--min-track MIN_TRACK]
               [--max-track MAX_TRACK] [--min-track-note MIN_TRACK_NOTE]
               [--main-knob MAIN_KNOB] [--pedal PEDAL]
```

### Options:

- `-h`, `--help`: Show the help message and exit.
- `-l LOG`, `--log LOG`: Set log level (default: "INFO").
- `-s SOURCE`, `--source SOURCE`: Set source port name (default: "Minilab3 MIDI").
- `-b LOOPBACK`, `--loopback LOOPBACK`: Set loopback port name (default: "Arturia Loopback").
- `--min-track MIN_TRACK`: Set the minimum track number (default: 1).
- `--max-track MAX_TRACK`: Set the maximum track number (default: 8).
- `--min-track-note MIN_TRACK_NOTE`: Set the note number for the minimum track (default: 36).
- `--main-knob MAIN_KNOB`: Set the main knob control number (default: 29).
- `--pedal PEDAL`: Set the pedal control number (default: 127).

## Example

```bash
python midi.py --source "My MIDI Controller" --loopback "Loopback Device" --main-knob 29 --pedal 127
```

## Notes

- The script doesn't create a virtual MIDI port, so you need to use a separate tool like [LoopMIDI (Windows)](https://www.tobias-erichsen.de/software/loopmidi.html) or [IAC Driver (macOS)](https://help.ableton.com/hc/en-us/articles/209774225-How-to-setup-a-virtual-MIDI-bus)
