import os

# Путь к папке со штрих-кодами которые отдаются пользователю
image_folder = "tgbot/trial_images/"


async def get_trial_image_filename():
    for root, _, files in os.walk(image_folder):
        for filename in sorted(files):
            image_filename = os.path.join(root, filename)
            yield image_filename
