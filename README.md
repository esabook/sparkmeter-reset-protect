
install python 3.x

pip install requirements.txt


Todo:

send to specific telegram's user account, or group.


This is single runtime process, so we can launch from supported python env. like:
- `python program.py`
- `py program.py`
- `cmd run.cmd`
- etc

But, make sure `settings.json` is setup properly:
- Telegram bot token from telegram https://telegram.me/BotFather `if wanted`
- Azure blob properties `if wanted`
- MSSQL connection string `if wanted`
- Sparkmeter thundercloud endpoint [`see example`](/settings.json)
