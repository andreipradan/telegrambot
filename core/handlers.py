from core.constants import ALLOWED_COMMANDS
from core.constants import GAME_COMMANDS
from core.constants import GOOGLE_CLOUD_COMMANDS
from core.constants import GOOGLE_CLOUD_WHITELIST
from core.parsers import parse_name


def validate_components(update):
    if update.callback_query:
        return "inline", update.callback_query.data

    message = update.message
    if not message or not message.chat or not message.chat.id:
        if update.edited_message or update.channel_post:
            return "skip-debug", 1337
        raise ValueError(
            f"Missing message, chat or chat ID. Update: {update.to_dict()}"
        )

    message_text = message.text
    if not message_text:
        if message.left_chat_member:
            return "😢", 400
        if message.new_chat_title:
            return "🎉", 400
        if message.new_chat_members:
            new_members = [parse_name(u) for u in message.new_chat_members]
            return f"Welcome {', '.join(new_members)}!", 400
        if message.photo or message.pinned_message or message.new_chat_photo:
            return "skip-debug", 1337
        raise ValueError(f"No message text. Update: {update.to_dict()}")

    if message.reply_to_message:
        return "skip-debug", 1337

    if not message_text.startswith("/"):
        return (
            f'Invalid command: "{message_text}".\nCommands start with "/".',
            "send-message",
        )

    command_text = message_text.split(" ")[0][1:]
    if command_text not in ALLOWED_COMMANDS:
        allowed_text = ""
        for command in ALLOWED_COMMANDS:
            if (
                command in GOOGLE_CLOUD_COMMANDS + GAME_COMMANDS
                and str(message.chat_id)
                not in GOOGLE_CLOUD_WHITELIST[message.chat.type]
            ):
                continue
            allowed_text += f"\n• /{command}"
        return (
            f'Unknown command: "{command_text}".\n'
            f"Available commands: {allowed_text}",
            400,
        )

    return command_text, "valid-command"
