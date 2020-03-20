from commands.gcloud_utils import analyze_sentiment
from commands.say_hi import say_hi
from commands.covid_stats import get_covid_county_details
from commands.covid_stats import get_covid_per_county
from commands.covid_stats import get_covid_stats


ALLOWED_COMMANDS = {
    'analyze_sentiment': analyze_sentiment,
    'covid': get_covid_stats,
    'covid_counties': get_covid_per_county,
    'covid_county_details': get_covid_county_details,
    'say_hi': say_hi,
}
COMMANDS_WITH_TEXT = [
    'analyze_sentiment',
    'covid_county_details',
]


def validate_components(message):

    chat_id = message.chat.id
    if not chat_id:
        return 'No chat ID', 400

    if not message:
        return 'No message', 400

    message_text = message.text
    if not message_text:
        return 'No message text', 400

    if not message_text.startswith('/'):
        return f'Not a command: "{message_text}". Commands start with "/".', 400

    command_text = message_text.split(' ')[0][1:]
    if command_text not in ALLOWED_COMMANDS:
        allowed_text = ''
        for command in ALLOWED_COMMANDS.keys():
            allowed_text += f'\n• /{command}'
        return f'Unrecognized command: "{command_text}".\n' \
               f'Try one of these: {allowed_text}', 400

    return command_text, 200
