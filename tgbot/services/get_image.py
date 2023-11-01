import os

# Путь к папке со штрих-кодами которые отдаются пользователю
image_folder = "tgbot/images_qr/"


async def get_next_image_filename():
    for root, _, files in os.walk(image_folder):
        for filename in sorted(files):
            image_filename = os.path.join(root, filename)
            yield image_filename
