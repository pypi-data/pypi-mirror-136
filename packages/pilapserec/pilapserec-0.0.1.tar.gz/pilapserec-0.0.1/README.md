# pilapse
Python module to capture time lapse videos on Raspberry Pi

## Examples

## Installation
It's recommended to create a virtual environment:
```bash
python -m venv pilapse
cd pilapse
source bin/activate
```

You can simply install `pilapse` from PyPi:
```bash
pip install pilapserec
```

## Usage
To capture an image only (can be used to check the camera beforehand):
```bash
pilapse capture
```

To record a long video:
```bash
pilapse record
```

To make a video out of captured images:
```bash
pilapse compile
```

However, you are advised against video compiling directory on Raspberry Pi, as the system resource may run low and you are almost certainly to be kicked out of the SSH session. For the same reason, you are advised against using the `--auto-compile` switch. After record session, you can plug the microSD card into your main work station and compile them there.

For more options, refer to `--help` command:
```bash
(pilapse) aki@hakune:~/pilapse $ pilapse --help
piLapse - capture time lapse video on Raspberry Pi.

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
```

To keep the process running after log out of SSH, you can use [`screen` or `tmux`](https://askubuntu.com/questions/8653/how-to-keep-processes-running-after-ending-ssh-session):
```bash
sudo apt install tmux
tmux
pilapse record
```

If you encounter [`numpy` error while making videos on Raspberry Pi](https://numpy.org/devdocs/user/troubleshooting-importerror.html), run this command and try to compile again:
```bash
sudo apt install libatlas-base-dev ffmpeg
```

## Development
Any contribution is deeply appreciated.
