import telegram

from commands.covid_stats import get_romania_stats

chat_id = '-382272798'
token = '832658943:AAFkKfGWXaMPOV12YmZTQ1Z6I04jBR_xEeY'

text = get_romania_stats()
bot = telegram.Bot(token=token)
bot.sendMessage(chat_id=chat_id, text=text)
