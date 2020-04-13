import argparse

import telegram


def get_webhook(token):
    current_url = telegram.Bot(token=token).get_webhook_info()["url"]
    print(f'Current webhook url: {current_url or "is not set up"}')


def set_webhook(token, host):
    bot = telegram.Bot(token=token)
    print(f"Setting webhook... {bot.set_webhook(f'{host}/{token}')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple script to set the telegram bot webhook url"
    )
    parser.add_argument(
        "--token", required=True, type=str, help="Telegram bot TOKEN"
    )
    parser.add_argument("--host", type=str, help="https host")
    args = parser.parse_args()
    if not args.host:
        get_webhook(args.token)
    elif not args.host.startswith("https"):
        raise ValueError("https host required")
    else:
        set_webhook(token=args.token, host=args.host)
