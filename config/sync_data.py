import argparse
import inspect
import logging
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
    )
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - "
    "%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    from scrapers.clients.datelazi import DateLaZiClient
    from scrapers.clients.worldometers import WorldometersClient

    parser = argparse.ArgumentParser(description="Sync data from remotes")
    parser.add_argument("--all", action="store_true", help="Sync everything")
    parser.add_argument(
        "--romania",
        action="store_true",
        help="Sync today's data for romania",
    )
    parser.add_argument(
        "--romania-archive",
        action="store_true",
        help="Sync historical data for romania",
    )
    parser.add_argument(
        "--global-stats",
        action="store_true",
        help="Sync today's international stats",
    )
    parser.add_argument(
        "--global-stats-archive",
        action="store_true",
        help="Sync today's international countries stats",
    )
    parser.add_argument(
        "--news",
        action="store_true",
        help="Sync latest news in romania-collection",
    )
    args = parser.parse_args()
    logger.info("Starting sync...")
    if args.all:
        if any(
            (
                args.romania,
                args.romania_archive,
                args.global_stats,
                args.global_stats_archive,
                args.news,
            )
        ):
            raise ValueError("--all can't be used with other arguments")
        args.romania = True
        args.romania_archive = True
        args.global_stats = True
        args.global_stats_archive = True
        args.news = True

    ro_client = DateLaZiClient()
    if args.romania:
        ro_client.sync()
    if args.romania_archive:
        ro_client.sync_archive()

    client = WorldometersClient()
    if args.global_stats:
        client.sync()
    if args.global_stats_archive:
        client.sync_archive()

    if args.news:
        raise NotImplementedError
    logger.info("Done")
