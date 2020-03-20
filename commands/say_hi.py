def say_hi(update):
    user = update.message.from_user
    name = f'{user.first_name} {user.last_name}' or user.username
    return f'Hello {name}!'
