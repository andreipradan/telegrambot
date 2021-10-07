import argparse
import logging

import requests
import telegram


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_webhook(token):
    current_url = telegram.Bot(token=token).get_webhook_info()["url"]
    logging.info(f'Current webhook url: {current_url or "is not set up"}')
    return current_url


def set_webhook(token, url):
    bot = telegram.Bot(token=token)
    if url:
        if not url.startswith("https://"):
            return logger.error(f"URL '{url}' is not https!")
        url = f"{url}/webhook/{token}"
        logger.info(f"Setting up custom URL : {url}")
        bot.set_webhook(url)
        return bot.get_webhook_info()

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

    url = f"{tunnel_url}/webhook/{token}"
    logger.info(f"Setting up local ngrok url: {url}")
    bot.set_webhook(url)
    return get_webhook(token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple script to set the telegram bot webhook url"
    )
    parser.add_argument(
        "--token", required=True, type=str, help="Telegram bot TOKEN"
    )
    parser.add_argument(
        "--set",
        const="local",
        help="Set HTTPS Host. Defaults to running ngrok tunnel",
        nargs="?",
        type=str,
    )
    args = parser.parse_args()
    if args.set:
        set_webhook(
            token=args.token, url=args.set if args.set != "local" else None
        )
    else:
        logger.info("Getting webhook url...")
        get_webhook(args.token)
    logging.info("Done")
