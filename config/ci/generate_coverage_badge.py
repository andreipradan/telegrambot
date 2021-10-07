import logging
from coverage import coverage


COVERAGE_COLOURS = [
    (90, "#4c1"),
    (80, "#97ca00"),
    (70, "#a4a61d"),
    (60, "#dfb317"),
    (50, "#fe7d37"),
    (20, "#e05d44"),
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - "
    "%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_coverage():
    cov = coverage()
    cov.load()
    return int(cov.report())


def get_colour(total):
    for baseline, colour in COVERAGE_COLOURS:
        if total >= baseline:
            return colour
    return "red"


if __name__ == "__main__":
    badge_coverage = get_coverage()
    badge_colour = get_colour(badge_coverage)

    with open(
        "config/ci/coverage-template.svg", "r"
    ) as coverage_template, open("/app/coverage.svg", "w+") as coverage_file:
        coverage_file.write(
            coverage_template.read()
            .replace(
                "%total_coverage_goes_here%",
                f"{badge_coverage}%",
            )
            .replace("%coverage_colour_goes_here%", badge_colour)
        )
    logger.info("Completed")
