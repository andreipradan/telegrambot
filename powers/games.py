from core import database
from scrapers.formatters import parse_global


class Games:
    COLLECTION = "games"

    def __init__(self, chat_id, name):
        self.chat_id = chat_id
        self.name = name.lower()

    def _fetch_game(self):
        return database.get_stats(
            self.COLLECTION, chat_id=self.chat_id, name=self.name
        )

    def _set_games_stats(self, stats, **kwargs):
        return database.set_stats(
            stats=stats,
            collection=self.COLLECTION,
            chat_id=self.chat_id,
            name=self.name,
            **kwargs,
        )

    @property
    def does_not_exist(self):
        return self.respond(
            [
                f"Game '{self.name.capitalize()}' not found ",
                f"Type '/games {self.name} new' to create a new game",
            ]
        )

    def get(self):
        stats = self._fetch_game()
        if stats:
            stats.pop("name")
            stats.pop("chat_id")
        return self.respond(stats or ["No available players"])

    @classmethod
    def get_list(cls, chat_id):
        return database.get_many(
            cls.COLLECTION, order_by="name", how=1, chat_id=chat_id
        )

    def new_game(self):
        if self._fetch_game():
            return self.respond(
                ["Already exists"], title=self.name.capitalize()
            )
        self._set_games_stats({"name": self.name})
        return f"Created new game: {self.name.capitalize()}"

    def new_player(self, player):
        stats = self._fetch_game()
        if stats and player in stats:
            return self.respond(
                [f"Player {player.title()} already exists"],
                title=self.name.capitalize(),
            )
        self._set_games_stats({player: 0})
        return f"New player: {player.title()}"

    def respond(self, stats, title=None):
        return (
            parse_global(
                title=title or self.name.capitalize(), stats=stats, items={},
            )
            if stats
            else self.does_not_exist
        )

    def update(self, operation, player):
        if player.lower() == "name":
            return self.respond([f"Can't use the name '{player}'"])
        allowed_ops = ["new_player", "new", "+", "-"]
        if operation not in allowed_ops:
            return self.respond(allowed_ops, title="Allowed operations:")

        player = player.lower()
        if operation == "new":
            return self.new_game()
        if operation == "new_player":
            return self.new_player(player)

        stats = self._fetch_game()
        if not stats:
            return self.does_not_exist

        if player not in stats:
            return self.respond(
                [
                    f"Player '{player.title()}' does not exist. ",
                    "Type '/games <game_name> new_player <player_name>' to "
                    "add a new player",
                ]
            )
        if operation == "+":
            score = stats[player] + 1
            self._set_games_stats({player: score})
            return f"Updated {player.title()}'s score to: {score} (+1)"

        score = stats[player] - 1
        self._set_games_stats({player: score})
        return f"Updated {player.title()}'s score to: {score} (-1)"
