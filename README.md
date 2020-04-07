# Run in linux
## Requirements:
* Python3
* Postgresql

## Setup
* Get a bot token from @BotFather
* Install requirements (using a virtualenv is recommended): `pip install -r requirements.txt`
* Required enviroment variables:
  * MODE=polling
  * DATABASE_URL=(The database URI for your postgres database)
  * TOKEN=(Your bot token)
  * OWNER_ID=(Your telegram ID)
* Run the bot with `python3 bot.py`
* Use /setgroup in a group to set the working group

# Deploy on Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ramos-adrian/storebot)
* Leave the MODE variable on default ("heroku")
* Complete the form with your bot API, your Application name, and the Telegram ID of the owner account.
