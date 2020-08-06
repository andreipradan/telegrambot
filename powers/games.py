from core import database
from scrapers.formatters import parse_global


class Games:
    COLLECTION = "games"

    def __init__(self, name="default_game"):
        self.name = name.lower()

    @property
    def does_not_exist(self):
        return self.respond(
            [
                f"Game '{self.name.title()}' does not exist.",
                f"Type '/games <game_name> new' to create a new game",
            ]
        )

    def get(self):
        stats = database.get_stats(collection=self.COLLECTION, name=self.name)
        stats.pop("name")
        return self.respond(stats)

    @classmethod
    def get_list(cls):
        games = [x["name"].title() for x in database.get_many(cls.COLLECTION)]
        return parse_global(
            title="Available games", stats=games or [], items={}
        )

    def new_game(self):
        if database.get_stats(collection=self.COLLECTION, name=self.name):
            return self.respond(["Already exists"], title=self.name.title())
        database.set_stats(
            {"name": self.name}, collection=self.COLLECTION, name=self.name,
        )
        return self.get()

    def new_player(self, player):
        stats = database.get_stats(collection=self.COLLECTION, name=self.name)
        if player in stats:
            return self.respond(
                [f"Player {player.title()} already exists"],
                title=self.name.title(),
            )

        database.set_stats(
            {player: 0}, collection=self.COLLECTION, name=self.name
        )
        return self.get()

    def respond(self, stats, title=None):
        return (
            parse_global(
                title=title or self.name.title(), stats=stats, items={},
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

        stats = database.get_stats(collection=self.COLLECTION, name=self.name)
        if not stats:
            return self.does_not_exist

        if player not in stats:
            return self.respond(
                [
                    f"Player '{player.title()}' does not exist. "
                    "Type '/games <game_name> new_player <player_name>' to add "
                    "a new player"
                ]
            )
        if operation == "+":
            stats[player] += 1
        else:
            stats[player] -= 1
        database.set_stats(
            stats, collection=self.COLLECTION, name=self.name,
        )
        return self.respond(stats=stats)
