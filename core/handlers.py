from commands.gcloud_utils import analyze_sentiment
from commands.say_hi import say_hi
from commands.covid_stats import get_county_details
from commands.covid_stats import get_covid_global
from commands.covid_stats import get_covid_counties
from commands.covid_stats import get_romania_stats


ALLOWED_COMMANDS = {
    'analyze_sentiment': analyze_sentiment,
    'covid': get_romania_stats,
    'covid_counties': get_covid_counties,
    'covid_county_details': get_county_details,
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


def validate_components(update):
    message = update.message
    if not message or not message.chat or not message.chat.id:
        if getattr(update, 'edited_message', None):
            return f'✂️', 1337
        raise ValueError(
            f'Missing message, chat or chat ID. Update: {update.to_dict()}'
        )

    message_text = message.text
    if not message_text:
        if getattr(message, 'left_chat_member', None):
            return '😢', 400
        if getattr(message, 'new_chat_title', None):
            return '🎉', 400
        if getattr(message, 'new_chat_members', None):
            new_members = [
                f'{user.first_name} {user.last_name}' or user.username
                for user in message.new_chat_members
            ]
            return f"Welcome {', '.join(new_members)}!", 400
        raise ValueError(f'No message text. Update: {update.to_dict()}')

    if not message_text.startswith('/'):
        return (
           f'Invalid command: "{message_text}".\nCommands start with "/".',
           'send-message'
        )

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

    return command_text, 'valid-command'

