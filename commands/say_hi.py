def say_hi(update):
    return 'Hello {} {}!'.format(
        update.message.from_user.first_name,
        update.message.from_user.last_name
    )
