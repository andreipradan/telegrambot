from core.constants import ALLOWED_COMMANDS


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
        for command in ALLOWED_COMMANDS:
            allowed_text += f'\n• /{command}'
        return (
            f'Unknown command: "{command_text}".\n'
            f'Available commands: {allowed_text}',
            400
        )

    return command_text, 'valid-command'
