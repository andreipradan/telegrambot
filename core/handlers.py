from commands.gcloud_utils import analyze_sentiment
from commands.say_hi import say_hi
from commands.covid_stats import get_covid_county_details
from commands.covid_stats import get_covid_global
from commands.covid_stats import get_covid_counties
from commands.covid_stats import get_romania_stats


ALLOWED_COMMANDS = {
    'analyze_sentiment': analyze_sentiment,
    'covid': get_romania_stats,
    'covid_counties': get_covid_counties,
    'covid_county_details': get_covid_county_details,
    'covid_global': get_covid_global,
    'say_hi': say_hi,
}
COMMANDS_WITH_TEXT = [
    'analyze_sentiment',
    'covid_county_details',
    'covid_global',
]
COMMANDS_WITH_UPDATE = [
    'say_hi',
]


def validate_components(message):
    if not message:
        return 'No message', 404

    if not message.chat:
        return 'No chat', 404

    chat_id = message.chat.id
    if not chat_id:
        return 'No chat ID', 404

    message_text = message.text
    if not message_text:
        if getattr(message, 'left_chat_member', None):
            return '😢', 1337
        return 'No message text', 404

    if not message_text.startswith('/'):
        return f'Not a command: "{message_text}". Commands start with "/".', 400

    command_text = message_text.split(' ')[0][1:]
    if command_text not in ALLOWED_COMMANDS:
        allowed_text = ''
        for command in ALLOWED_COMMANDS.keys():
            allowed_text += f'\n• /{command}'
        return (
            f'Unknown command: "{command_text}".\n'
            f'Available commands: {allowed_text}',
            400
        )

    return command_text, 200


def parse_result(result):
    result['_id'] = str(result['_id'])
    return result
