#!/usr/bin/env python3


class camera:
    def __init__(
        self, workdir="~/Videos/pilapse", length: int = 3280, width: int = 2464
    ):
        # Load the arguments
        from .arguments import arguments

        self.arguments = arguments

        # Set up logging
        from .logger import logging

        self.log = logging

        # Set up Pi Camera
        from picamera import PiCamera

        self.camera = PiCamera()
        self.camera.resolution = (length, width)

        # Set up working directory
        from os import chdir, getcwd

        self._setUpWorkingDir(workdir)
        chdir(workdir)
        self.log.info(f"Working directory: {getcwd()}")

        # camera warm-up time
        from time import sleep

        sleep(2)

        self.log.success(f"Successfully set up camera.")

    def _setUpWorkingDir(self, workdir: str):
        import os, shutil

        self.log.info(f"Checking path {workdir}...")

        if not os.path.exists(workdir):
            self.log.info("Specified save path not found. Creating one...")
            try:
                os.makedirs(workdir, exist_ok=True)
                self.log.info(f"Created {workdir}")
            except:
                self.log.error(f"Cannot create folder at {workdir}")
                exit()

        elif not os.listdir(workdir) == []:
            # prompt the user to ask if the specified directory
            # should be deleted
            self.log.warning(
                "The specified path seems to already contains files. Continue will overwrite all data in that directory."
            )
            if input("[prompt] Continue and overwrite all files? [y/n] ") == "y":
                shutil.rmtree(workdir)
                os.makedirs(workdir, exist_ok=True)

        else:
            self.log.info(f"{workdir} seems already initiated")

    def capture(self, imageName: str, addTime: bool = False) -> int:
        # Add current time to image
        if addTime:
            from datetime import datetime

            self.camera.annotate_text = str(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.camera.annotate_text_size = 120

        self.camera.capture(imageName)
        return 0

    def record(self, duration: int, frequency: int, continuous: bool = False):
        from time import sleep

        if continuous:
            """Continuous capturing mode"""
            for filename in self.camera.capture_continuous("img{counter:03d}.jpg"):
                self.log.info(f"Captured {filename}")
                sleep(frequency)
        else:
            from .interface import progressBar

            RANGE = progressBar(duration, frequency)

            for imgNumber in RANGE["iter"]:
                imgName = f"img{imgNumber // frequency}.jpg"
                self.capture(imageName=imgName, addTime=not self.arguments["--no-time"])

                # different logging options
                if RANGE["type"] == "range":
                    print(f"Captured: {imgName}", end="\r")
                elif RANGE["type"] == "tqdm.std.tqdm":
                    RANGE["iter"].set_description(
                        f"{imgNumber}/{duration}s, {(duration - imgNumber) // frequency} left"
                    )

                sleep(frequency)
