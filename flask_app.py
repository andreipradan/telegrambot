import os

from flask import Flask
from flask import abort
from flask import jsonify
from flask import redirect
from flask import request
import telegram
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from core.database import update_or_create
from core.database import get_collection
from core.handlers import ALLOWED_COMMANDS
from core.handlers import COMMANDS_WITH_TEXT
from core.handlers import COMMANDS_WITH_UPDATE
from core.handlers import parse_result
from core.handlers import validate_components


if not os.getenv('FLASK_DEBUG', False):
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[FlaskIntegration()]
    )
token = os.environ['TOKEN']

app = Flask(__name__)


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

        command_text, status_code = validate_components(update.message)

        chat_id = update.message.chat_id

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
                f'Restrict results (e.g. /{command_text} 3'
                if 'Message is too long' in str(err)
                else str(err)
            )
            bot.sendMessage(chat_id=chat_id, text=text)
        return 'completed'
    return f"Unexpected method {request.method}"


@app.route('/countries/add')
def add():
    if not request.args:
        return 'Invalid data. Retry using URL parameters'
    update_or_create(**request.args.to_dict())
    return redirect('/collections')


@app.route('/countries/')
def collections():
    url_params = request.args.to_dict()
    limit = url_params.get('limit', 10)
    results = list(map(parse_result, get_collection().find()[:limit]))
    # get_collection('top_stats').create_index('id', unique=True)
    return jsonify(results)


@app.route('/countries/<slug>/')
def country(slug):
    result = get_collection().find_one({'slug': slug})
    if result:
        return jsonify(parse_result(result))
    return abort(404)


if __name__ == "__main__":
    app.run(
        debug=os.getenv('DEBUG', False),
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080))
    )
