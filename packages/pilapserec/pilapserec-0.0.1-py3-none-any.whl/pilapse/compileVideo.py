#!/usr/bin/env python3
import os
from . import cleanup
from .logger import logging
from .arguments import arguments


def _naturalSort(sortingList: list[str]) -> list:
    import re

    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(sortingList, key=alphanum_key)


def compileVideo(workDir: str, videoName: str, fps: int = 24):
    if (
        os.uname()[4][:3] == "arm"
        and input(
            "[prompt] Raspberry Pi device detected. Compiling video on low-end Raspberry devices often results in SSH disconnection and system termination. Proceed? [y/n] "
        )
        != "y"
    ):
        return
    else:
        if not os.path.isdir(workDir):
            logging.error("No captured image found")

        import moviepy.video.io.ImageSequenceClip

        imageFiles = [
            os.path.join(workDir, img)
            for img in _naturalSort(os.listdir(workDir))
            if img.endswith(".jpg")
        ]

        if input("[prompt] Check compiling images? [y/n] ") == "y":
            logging.info(f"Images found: {imageFiles}")

        if input("[prompt] Proceed? [y/n] ") == "y":
            video = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
                imageFiles, fps=fps
            )
            video.write_videofile(os.path.join(workDir, videoName))

            logging.success("Video file created successfully.")

    if not arguments["--preserve"]:
        cleanup.clean()
