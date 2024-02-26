# Bot auto sales of digital goods (subscription to VPN) using API Yoomoney and MongoDB. Added possibility to pay with cryptocurrency (bitcoin) powered by the Sellix API


<div id="header">
  <img src="https://github.com/PavelShaura/Autoseller_bot_aiogram_3/blob/master/img/bot_sample_gif.gif"/>
</div>

*Added ability to generate cryptocurrency invoices and track their confirmations before order fulfilment/
(Used SQLite3 to store and manage cryptocurrency payment data)*
## Link to bot:

https://t.me/instaViPN_bot

## New features:
1. Cryptocurrency invoice generation: Generate cryptocurrency invoices via Sellix API directly from the Telegram bot.
2. Confirmation Tracking: Wait for a predetermined number of confirmations before considering a payment complete.
3. Data Management: Use SQLite3 to efficiently store and manage transaction and invoice data.
4. Status and Cancellation: Commands to check the status of an order or cancel it.

## Installation
1. Install Python 3.x if it is not installed. [Python.org](https://www.python.org/downloads/)

2. Clone the repository:

   ```bash
   git clone https://github.com/PavelShaura/Autoseller_bot_aiogram_3
   
3. Navigate to the project catalog:

   ```bash
   cd Autoseller_bot_aiogram_3
   
4. Install the dependencies using pip:

   ```bash
   pip install -r requirements.txt
   
## Configuration

1. Create an .env configuration file in the root directory of the project using the .env.example template.(For notifications about bot actions to come to your Telegram channel - add the bot as an administrator to this group.)
2. Run the file yoomoney_auth.py and get your token to access the YOOMONEY API (You'll need YOOMONEY_CLIENT_ID and YOOMONEY_REDIRECT_URL). 
3. Follow all steps from the program.
4. Paste your token in YOOMONEY_TOKEN

Before you begin, ensure you have met the access to the Sellix API with your credentials https://sellix.io/

Here's what the alerts to the admin group look like:
![Иллюстрация к проекту](https://github.com/PavelShaura/Autoseller_bot_aiogram_3/blob/master/img/group_sample.png)

## Structure and storage logic of digital goods sold

1. QR code files and configuration files must be located in the static_files folder, pre-numbered starting from one. 
There are four folders in total (two folders with photo QR codes (trial and payment), and two folders with .conf configuration files (trial and payment).

2. In case of successful payment (or trial subscription) the file is sent to the user, then it is recorded in the database (photo_id) of this file in the table "files" for the possibility of repeated sending to the user, and then deleted from the folder.

3. The configuration .conf file is identified by and corresponds to the sequence number of the QR code photo shipped. That is - if the file "34.png" for example was sent to a user, then the file "34.conf" will be assigned to this user accordingly.
The ".conf" file is also written to the database (file_id) in the "files" table, then deleted from the folder.

![Иллюстрация к проекту](https://github.com/PavelShaura/Autoseller_bot_aiogram_3/blob/master/img/static_file_template.png)


<div id="header">
  <img src="https://media.giphy.com/media/3b6rWgdpjf0jrvvvZ6/giphy.gif" width="100"/>
</div>

Questions and suggestions: https://t.me/PavelShau

## Start

Start the bot, run the following command in the root directory of the project:

   ```bash 
   python bot.py
