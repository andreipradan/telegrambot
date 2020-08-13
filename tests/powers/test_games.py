from unittest import mock

from powers.games import Games
from scrapers.formatters import parse_global


class TestGames:
    @classmethod
    def setup_class(cls):
        cls.game = Games("foo_chat_id", "foo_game_name")

    def get_does_not_exist_result(self):
        return [
            f"Game 'Foo_game_name' not found ",
            f"Type '/games foo_game_name new' to create a new game",
        ]

    @mock.patch("core.database.get_stats")
    def test_fetch_game_calls_database_get_stats(self, get_stats_mock):
        get_stats_mock.return_value = "stats_result"
        assert self.game._fetch_game() == "stats_result"
        get_stats_mock.assert_called_with(
            "games", chat_id="foo_chat_id", name="foo_game_name"
        )

    @mock.patch("core.database.set_stats")
    def test_set_games_stats_calls_database_set_stats(self, set_stats_mock):
        set_stats_mock.return_value = "set_stats_result"
        assert (
            self.game._set_games_stats({"foo": "bar"}, cux="baz")
            == "set_stats_result"
        )
        set_stats_mock.assert_called_with(
            stats={"foo": "bar"},
            collection="games",
            chat_id="foo_chat_id",
            name="foo_game_name",
            cux="baz",
        )

    @mock.patch("powers.games.Games.respond", return_value="resp")
    def test_does_not_exist_calls_game_respond(self, respond_mock):
        assert self.game.does_not_exist == "resp"
        respond_mock.assert_called_once_with(self.get_does_not_exist_result())

    @mock.patch("powers.games.Games._fetch_game", return_value=None)
    @mock.patch("powers.games.Games.respond", return_value="resp")
    def test_get_with_no_stats(self, respond_mock, fetch_mock):
        assert self.game.get() == "resp"
        fetch_mock.asssert_called_once_with()
        respond_mock.assert_called_once_with(["No available players"])

    @mock.patch("powers.games.Games._fetch_game")
    @mock.patch("powers.games.Games.respond", return_value="resp")
    def test_get_with_stats_pops_name_chat_id(self, respond_mock, fetch_mock):
        fetch_mock.return_value = {"name": "n", "chat_id": "i", "foo": "bar"}
        assert self.game.get() == "resp"
        fetch_mock.asssert_called_once_with()
        respond_mock.assert_called_once_with({"foo": "bar"})

    @mock.patch("core.database.get_many", return_value="get_many_resp")
    def test_get_list_calls_database_get_many(self, get_many_mock):
        assert self.game.get_list("foo_id") == "get_many_resp"
        get_many_mock.assert_called_once_with(
            "games", order_by="name", how=1, chat_id="foo_id"
        )

    @mock.patch("powers.games.Games.respond", return_value="resp")
    @mock.patch("powers.games.Games._fetch_game", return_value={"foo": "bar"})
    def test_new_game_already_exists(self, fetch_mock, respond_mock):
        assert self.game.new_game() == "resp"
        fetch_mock.asssert_called_once_with()
        respond_mock.assert_called_once_with(
            ["Already exists"], title="Foo_game_name"
        )

    @mock.patch("powers.games.Games._set_games_stats", return_value="set")
    @mock.patch("powers.games.Games._fetch_game", return_value=None)
    def test_new_game_calls_set_stats(self, fetch_mock, set_stats_mock):
        assert self.game.new_game() == "Created new game: Foo_game_name"
        fetch_mock.asssert_called_once_with()
        set_stats_mock.assert_called_once_with({"name": "foo_game_name"})

    @mock.patch("powers.games.Games._set_games_stats", return_value="set")
    @mock.patch("powers.games.Games._fetch_game", return_value=None)
    def test_new_player_no_game_creates_both(self, fetch_mock, set_stats_mock):
        assert self.game.new_player("foo") == "New player: Foo"
        fetch_mock.asssert_called_once_with()
        set_stats_mock.assert_called_once_with({"foo": 0})

    @mock.patch("powers.games.Games.respond", return_value="resp")
    @mock.patch("powers.games.Games._fetch_game", return_value={"foo": 1})
    def test_new_player_already_exists(self, fetch_mock, respond_mock):
        assert self.game.new_player("foo") == "resp"
        fetch_mock.asssert_called_once_with()
        respond_mock.assert_called_once_with(
            ["Player Foo already exists"], title="Foo_game_name"
        )

    @mock.patch("powers.games.parse_global", return_value="parse")
    def test_respond_calls_parse_global(self, parse_mock):
        assert self.game.respond({"foo": "bar"}, title="cux") == "parse"
        parse_mock.assert_called_once_with(
            title="cux", stats={"foo": "bar"}, items={}
        )

    def test_respond_with_no_stats_calls_does_not_exists(self):
        assert self.game.respond({}, title="cux") == parse_global(
            stats=self.get_does_not_exist_result(),
            items={},
            title="Foo_game_name",
        )

    @mock.patch("powers.games.Games.respond", return_value="resp")
    def test_update_with_reserved_name_field(self, respond_mock):
        assert self.game.update(None, "name") == "resp"
        respond_mock.assert_called_once_with(["Can't use the name 'name'"])

    @mock.patch("powers.games.Games.respond", return_value="resp")
    def test_update_with_invalid_operation(self, respond_mock):
        assert self.game.update("bad_op", "foo") == "resp"
        respond_mock.assert_called_once_with(
            ["new_player", "new", "+", "-"], title="Allowed operations:"
        )

    @mock.patch("powers.games.Games.new_game", return_value="new")
    def test_update_operation_calls_new_game(self, new_game_mock):
        assert self.game.update("new", "foo") == "new"
        new_game_mock.assert_called_once_with()

    @mock.patch("powers.games.Games.new_player", return_value="new_player")
    def test_update_operation_calls_new_player(self, new_player_mock):
        assert self.game.update("new_player", "foo") == "new_player"
        new_player_mock.assert_called_once_with("foo")

    @mock.patch("powers.games.Games._fetch_game", return_value=None)
    def test_update_with_no_game(self, fetch_mock):
        assert self.game.update("+", "foo") == parse_global(
            stats=self.get_does_not_exist_result(),
            items={},
            title="Foo_game_name",
        )
        fetch_mock.asssert_called_once_with()

    @mock.patch("powers.games.Games.respond", return_value="resp")
    @mock.patch("powers.games.Games._fetch_game", return_value={"foo": 1})
    def test_update_with_no_player(self, fetch_mock, respond_mock):
        assert self.game.update("+", "bar") == "resp"
        fetch_mock.asssert_called_once_with()
        respond_mock.assert_called_once_with(
            [
                f"Player 'Bar' does not exist. ",
                "Type '/games <game_name> new_player <player_name>' to "
                "add a new player",
            ]
        )

    @mock.patch("powers.games.Games._set_games_stats")
    @mock.patch("powers.games.Games._fetch_game", return_value={"foo": 1})
    def test_update_increments_player_stats(self, fetch_mock, set_stats_mock):
        assert self.game.update("+", "foo") == "Updated Foo's score to: 2 (+1)"
        fetch_mock.asssert_called_once_with()
        set_stats_mock.assert_called_once_with({"foo": 2})

    @mock.patch("powers.games.Games._set_games_stats")
    @mock.patch("powers.games.Games._fetch_game", return_value={"foo": 1})
    def test_update_decrements_player_stats(self, fetch_mock, set_stats_mock):
        assert self.game.update("-", "foo") == "Updated Foo's score to: 0 (-1)"
        fetch_mock.asssert_called_once_with()
        set_stats_mock.assert_called_once_with({"foo": 0})
