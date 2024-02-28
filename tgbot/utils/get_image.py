import os
from typing import Generator


async def get_image_filename(image_folder: str) -> Generator[str, None, None]:
    """
    Asynchronously generates the next image filename from the specified image_folder directory.

    Args:
        image_folder (str): Path to the folder with the images.

    Yields:
        str: The next image filename.
    """
    for root, _, files in os.walk(image_folder):
        for filename in sorted(files):
            image_filename = os.path.join(root, filename)
            yield image_filename
