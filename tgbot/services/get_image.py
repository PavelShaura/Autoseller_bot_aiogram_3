import os

# Путь к папке со штрих-кодами которые отдаются пользователю
image_folder = "tgbot/images_qr/"
# Путь к папке с файлами конфигурации которые отдаются пользователю
conf_folder = "tgbot/client_conf_files/"


async def get_next_image_filename():
    for root, _, files in os.walk(image_folder):
        for filename in sorted(files):
            image_filename = os.path.join(root, filename)
            yield image_filename


async def get_next_conf_filename():
    for root, _, files in os.walk(conf_folder):
        for filename in sorted(files):
            conf_filename = os.path.join(root, filename)
            yield conf_filename
