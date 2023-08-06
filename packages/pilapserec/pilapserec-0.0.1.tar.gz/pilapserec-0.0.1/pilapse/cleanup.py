#!/usr/bin/env python3


def clean():
    import os
    from .arguments import arguments
    from .interface import print_statusline
    from .logger import logging

    imageFiles = [
        os.path.join(arguments["--save-dir"], img)
        for img in os.listdir(arguments["--save-dir"])
        if img.startswith("img") and img.endswith(".jpg")
    ]

    # Let users preview files going to be deleted
    if input("[prompt] Checking files going to be deleted? [y/n] ") != "n":
        print(imageFiles)
        if input("[prompt] Proceed? [y/n] ") != "y":
            exit()

    for filename in imageFiles:
        try:
            os.remove(filename)
            print_statusline(f"[progress] Removed: {filename}")
        except:
            logging.error(f"Cannot remove {filename}")
            logging.info("Please check the file's existence or permission")
            exit()

    logging.success("Successfully cleaned up")
