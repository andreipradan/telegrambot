import requests

from commands import parsers
from core import constants


def histogram(**kwargs):
    response = requests.get(constants.URLS['romania'])
    response.raise_for_status()

    stats = response.json()

    age_histogram = stats['ageHistogram']['histogram']
    gender_stats = {
        'barbati': stats['genderStats']['percentageOfMen'],
        'femei': stats['genderStats']['percentageOfWomen'],
        'copii': stats['genderStats']['percentageOfChildren'],
    }
    totals = stats['quickStats']['totals']
    totals.pop('date')
    totals.pop('date_string')

    if 'json' in kwargs:
        return stats

    return parsers.parse_global(
        title=f'🦠 Romania',
        stats=totals,
        items={
            'Dupa varsta': age_histogram,
            'Dupa gen (%)': gender_stats,
        },
        footer="\nLast updated: "
               f"{stats['lastDataUpdateDetails']['last_updated_on_string']}"
    )


def history(**kwargs):
    def parse_date_stats(date_stats):
        date_stats.pop('date')
        return date_stats

    response = requests.get(constants.URLS['romania'])
    response.raise_for_status()

    stats = response.json()
    if 'json' in kwargs:
        return stats

    history_stats = stats['quickStats']['history']

    return parsers.parse_global(
        title=f'🦠 Romania istoric',
        stats={'Last updated': stats['quickStats']['last_updated_on_string']},
        items={
            date_stats.pop('date_string').capitalize():
                parse_date_stats(date_stats)
            for date_stats in history_stats
        },
        footer="\nLast updated: "
               f"{stats['lastDataUpdateDetails']['last_updated_on_string']}",
        emoji='📅',
    )
