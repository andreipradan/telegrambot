import os

from flask import Flask
from flask import request
import git
import telegram

from commands.gcloud_utils import sample_analyze_sentiment
from commands.say_hi import say_hi
from commands.covid_stats import get_covid_county_details
from commands.covid_stats import get_covid_per_county
from commands.covid_stats import get_covid_stats


ALLOWED_COMMANDS = {
    'analyze_sentiment': sample_analyze_sentiment,
    'covid': get_covid_stats,
    'covid_counties': get_covid_per_county,
    'covid_county_details': get_covid_county_details,
    'say_hi': say_hi,
}


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
        bot = telegram.Bot(token=os.environ['TOKEN'])
        json = request.get_json()
        if not json:
            send_message(bot, f'No payload: {json}')
            return 'No payload'

        update = telegram.Update.de_json(json, bot)
        if not update.message:
            send_message(bot, f'No message: {json}')
            return 'No message'

        if not update.message.text:
            send_message(bot, f'No message text: {json}')
            return 'No message text'

        chat_id = update.message.chat.id
        if not chat_id:
            send_message(bot, f'No chat ID: {json}')
            return 'No chat ID'

        message_text = update.message.text
        if not message_text.startswith('/'):
            send_message(
                bot,
                f'Not a command: "{message_text}". Commands start with "/".'
            )
            return 'Not a command'

        command_text = message_text.split(' ')[0][1:]
        if command_text not in ALLOWED_COMMANDS:
            allowed_text = ''
            for command in ALLOWED_COMMANDS.keys():
                allowed_text += f'\n• /{command}'
            send_message(
                bot,
                f'Unrecognized command: "{command_text}".\nTry one of these: {allowed_text}',
                chat_id=chat_id
            )
            return 'Unrecognized command'

        results = ALLOWED_COMMANDS[command_text](update)
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


@app.route('/git-webhook/', methods=['POST'])
def git_webhook():
    repo = git.Repo(os.getenv('PATH_TO_GIT_FOLDER'))
    repo.remotes.origin.pull()
    return request.get_json()
