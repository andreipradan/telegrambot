import argparse
import logging

import requests
import telegram


logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_webhook(token):
    current_url = telegram.Bot(token=token).get_webhook_info()["url"]
    logging.info(f'Current webhook url: {current_url or "is not set up"}')


def set_webhook(token):
    try:
        json = requests.get("http://localhost:4040/api/tunnels").json()
    except requests.exceptions.ConnectionError:
        logging.info("Failed to get ngrok tunnels. Is ngrok running?")
        return

    tunnel_url = ""
    for tunnel in json["tunnels"]:
        if tunnel["public_url"].startswith("https://"):
            tunnel_url = tunnel["public_url"]

    assert tunnel_url, "No HTTPS URL found!"

    bot = telegram.Bot(token=token)
    bot.set_webhook(f"{tunnel_url}/webhook/{token}")
    get_webhook(token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple script to set the telegram bot webhook url"
    )
    parser.add_argument(
        "--token", required=True, type=str, help="Telegram bot TOKEN"
    )
    parser.add_argument(
        "--set",
        action="store_true",
        help="Set HTTPS Host from running ngrok tunnel",
    )
    args = parser.parse_args()
    if not args.set:
        get_webhook(args.token)
    else:
        set_webhook(token=args.token)
    logging.info("Complete.")
