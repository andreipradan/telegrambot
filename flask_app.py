import os

from flask import Flask
from flask import request
import telegram

from handlers import ALLOWED_COMMANDS
from handlers import COMMANDS_WITH_TEXT
from handlers import COMMANDS_WITH_UPDATE
from handlers import validate_components


app = Flask(__name__)
token = os.environ['TOKEN']


def send_message(bot, text, chat_id=None):
    return bot.sendMessage(
        chat_id=chat_id or 412945234,
        text=text
    ).to_json()


@app.route(f'/{token}', methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        json = request.get_json()
        if not json:
            raise ValueError('No payload')

        bot = telegram.Bot(token=os.environ['TOKEN'])
        update = telegram.Update.de_json(json, bot)
        chat_id = update.message.chat_id

        command_text, status_code = validate_components(update.message)
        if status_code == 404:
            raise ValueError(command_text)
        elif status_code == 400:
            return send_message(bot, text=command_text, chat_id=chat_id)

        args = []
        if command_text in COMMANDS_WITH_TEXT:
            args.append(' '.join(update.message.text.split(' ')[1:]))
        elif command_text in COMMANDS_WITH_UPDATE:
            args.append(update)
        results = ALLOWED_COMMANDS[command_text](*args)

        try:
            bot.sendMessage(chat_id=chat_id, text=results)
        except telegram.error.BadRequest as err:
            text = (
                'Restrict results (limit=<count>)'
                if 'Message is too long' in str(err)
                else str(err)
            )
            bot.sendMessage(chat_id=chat_id, text=text)
        return 'completed'
    return f"Unexpected method {request.method}"


if __name__ == "__main__":
    app.run(
        debug=os.getenv('DEBUG', False),
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080))
    )
