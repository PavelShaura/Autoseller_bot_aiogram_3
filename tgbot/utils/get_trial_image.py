import os
from typing import Generator


# Path to the folder with the trial QR codes that are given to the user
image_folder: str = "tgbot/static_files/trial_images/"


async def get_trial_image_filename() -> Generator[str, None, None]:
    """
    Asynchronously generates the next trial image filename from the image_folder directory.

    Yields:
        str: The next trial image filename.
    """
    for root, _, files in os.walk(image_folder):
        for filename in sorted(files):
            image_filename = os.path.join(root, filename)
            yield image_filename
