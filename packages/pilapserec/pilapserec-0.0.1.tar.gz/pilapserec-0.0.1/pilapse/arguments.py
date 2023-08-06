#!/usr/bin/env python3

"""piLapse - capture time lapse video on Raspberry Pi.

Usage:
    pilapse capture [-i <image-name>] [-s <save-dir>] [--no-time] [--verbose]
    pilapse record [-d <duration> | -c] [-f <frequency>] [-l <length>] [-w <width>] [-s <save-dir>] [-S <wait-time>] [--auto-compile] [-o <video-name>] [-F <fps>] [--no-time] [--preserve] [--verbose]
    pilapse compile [-s <save-dir>] [-o <video-name>] [-F <fps>] [--preserve] [--verbose]
    pilapse clean [-s <save-dir>]
    pilapse (-h | --help)
    pilapse --version

Actions:
capture     Take 1 image only.
record      Record a timelapse video.
compile     Compile labelled images into a video.

Options:
-h --help                   Show this screen.
-c --continuous             Set to continuously run mode.
-d --duration DURATION      Set recording duration (by seconds) [default: 600].
-f --frequency FREQUENCY    Set time interval between shots (by seconds) [default: 5].
-F --fps FPS                Set final video fps [default: 24].
-l --length LENGTH          Set image length dimension (by pixel) [default: 3280].
-w --width WIDTH            Set image width dimension (by pixel) [default: 2464].
-s --save-dir SAVINGDIR     Set working and saving directory [default: ~/Videos/pilapse].
-S --shutter-wait TIME      Set timer before start capturing (by seconds) [default: 0].
-i --image-name NAME        Set image name in capture mode [default: image.jpg].
-o --output-video NAME      Set output video name.
-a --auto-compile           Automatically compile images [default: True].
-p --preserve               Do not automatically clean up after recording.
-n --no-time                Do not add time in capture mode.
--verbose                   Set to verbose mode.
--version                   Show version.


"""
from docopt import docopt
from . import __version__

def handleRelativePath(path: str) -> str:
    if path[0] == '~':
        from pathlib import Path
        homeDir = str(Path.home())
        path = path.replace('~', homeDir, 1)
    return path

arguments = docopt(__doc__, version=__version__)
arguments['--save-dir'] = handleRelativePath(arguments['--save-dir'])