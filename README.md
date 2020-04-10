<h1 align="center">Welcome to telegrambot 👋</h1>
<p>
  <img alt="cloud build status" src="https://storage.googleapis.com/telegrambot/build-status.svg" />
  <a href="https://github.com/andreipradan/telegrambot/blob/master/LICENCE.md" target="_blank">
    <img alt="License: LICENCE.md" src="https://img.shields.io/badge/License-LICENCE.md-yellow.svg" />
  </a>
</p>


> A telegram bot to interactively check OFFICIAL COVID-19 stats for Romania and other countries.

<h3> 🤖 Interact with the bot
    <a href="https://telegrambot.pradan.dev/" target="_blank">here</a>
</h3>

<h3> ✨ See it in action in the
    <a href="https://t.me/covid_ro_updates">🇷🇴 Covid Updates</a> telegram channel
</h3>


## Usage

#### Prerequisites:

- Create a new telegram bot by typing `/newbot` to BotFather here: https://t.me/botfather

    - give it a `name`: e.g. MyExtraordinaryBot (does not need to end in "Bot")
    - give it a `username`: e.g. my_extraordinary_bot (this one does need to end in "bot")
    - write down your `token` that BotFather gives you at the end. You will need it later on

#### Basic setup
1. Start the Flask local server:
    ```sh
    $ TOKEN=<telegram_bot_token> python flask_app.py
    ```
2. [Ngrok](https://ngrok.com/)

    Ngrok is a great utility used for exposing your localhost to a publicly accessible https URL

    Telegram bot needs a https URL as a callback for sending events.
    e.g. received a message, received a command, a new user was added to the telegram group, etc.
    - sign up here https://dashboard.ngrok.com/signup
    - install `ngrok` and set it up using these four simple steps here: https://dashboard.ngrok.com/get-started
    - run it locally: `ngrok http 5000`
        - this will start a session and forward your localhost port 5000 to an online tunnel
        - copy the output of the https tunnel e.g. ![doc](docs/ngrok.png)
3. Set the webhook URL for your telegram bot using the  [config/webhook.py](config/webhook.py) script
    - e.g.
    ```sh
    $ python config/webhook.py --host=https://5efg4d21.ngrok.io --token=1234567890:ABCD-aBsadfASDFasfdb-v
    Setting webhook... True
    ```
    - replace the host and token with your own
    - your telegram bot should now be pointed to your newly created public URL that mirrors the localhost 5000 port


#### Advanced setup
1. Configure a MongoDB database
    - this will be used for storing the data collected by the bot
    - I use https://www.mongodb.com/cloud/atlas
    - set the MONGO_DB_HOST on the environment for the flask server to use
    - set the DATABASE_NAME on the environment as well


#### Troubleshooting:

1. Make sure you've set the correct TOKEN when starting the Flask server
    - the callback url contains your bot's token so if the TOKEN environment variable is not set correctly, when using the bot you will see a lot of 404s in the server console from the telegram bot trying to post callbacks (respond to commands) to an invalid URL

2. Make sure you've set the correct webhook URL.
    - you can double check the correct webhook URL by going into a python console and calling:
        - this should return your bot's webhook url (public https host + bot's token)
        ```shell script
        > python config/webhook.py --token=1234567890:ABCD-aBsadfASDFasfdb-v
        Current webhook url: https://5efg4d21.ngrok.io/1234567890:ABCD-aBsadfASDFasfdb-v
        ```

## Run tests

```sh
pytest tests
```

## Author

👤 **Andrei Prădan**

* Website: https://pradan.dev/
* Github: [andreipradan](https://github.com/andreipradan)
* LinkedIn: [andreipradan](https://linkedin.com/in/andreipradan)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/andreipradan/telegrambot/issues).

## Show your support

Give a ⭐️ if this project helped you!

<a href="https://www.buymeacoffee.com/andreipradan" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
