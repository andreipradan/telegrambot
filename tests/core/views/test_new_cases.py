from unittest import mock

from core.views import new_cases


class BaseNewCasesMixin:
    db_stats_kwargs = NotImplemented
    func = NotImplemented
    mock_func = NotImplemented
    mock_func_return_value = NotImplemented
    mock_return_value = NotImplemented
    parse_mock_return_value = NotImplemented

    @staticmethod
    def get_histogram_response(**kwargs):
        return

    @mock.patch("core.database.get_stats")
    def test_stats_already_in_db(self, db_stats_mock):
        db_stats_mock.return_value = {"foo": 1}

        with mock.patch(self.mock_func) as func_mock:
            func_mock.return_value = self.mock_return_value
            results = getattr(new_cases, self.func)()

        func_mock.assert_called_once_with(json=True)
        db_stats_mock.assert_called_once_with(**self.db_stats_kwargs)
        assert results is None

    @mock.patch("core.database.set_stats")
    @mock.patch("core.database.get_stats")
    @mock.patch("core.utils.parse_diff")
    @mock.patch("scrapers.formatters.parse_global")
    def test_set_stats_if_not_in_db(
        self, parse_mock, diff_mock, get_db_stats_mock, set_db_stats_mock,
    ):
        diff_mock.return_value = "diff_mock"
        get_db_stats_mock.return_value = {"foo": 1}
        parse_mock.return_value = "parse_global_result"

        with mock.patch(self.mock_func) as func_mock:
            func_mock.return_value = self.mock_func_return_value
            results = getattr(new_cases, self.func)()

        func_mock.assert_called_once_with(json=True)
        get_db_stats_mock.assert_called_once_with(**self.db_stats_kwargs)
        set_db_stats_mock.assert_called_once_with(
            {"foo": 1, "bar": 2}, **self.db_stats_kwargs
        )
        parse_mock.assert_called_once_with(**self.parse_mock_return_value)
        assert results == "parse_global_result"


class TestGetHistogram(BaseNewCasesMixin):
    db_stats_kwargs = {}
    func = "get_quick_stats"
    mock_func = "scrapers.histogram"
    mock_func_return_value = {"quickStats": {"totals": {"foo": 1, "bar": 2}}}
    mock_return_value = {"quickStats": {"totals": {"foo": 1}}}
    parse_mock_return_value = {
        "title": "🔴 Cazuri noi",
        "stats": "diff_mock",
        "items": {},
    }


class TestGetLatestNews(BaseNewCasesMixin):
    db_stats_kwargs = {"slug": "stiri-oficiale-slug"}
    func = "get_latest_news"
    mock_func = "scrapers.latest_article"
    mock_func_return_value = {
        "bar": 2,
        "descriere": "description",
        "foo": 1,
        "titlu": "titlu foo",
        "url": "http://foo.url",
    }
    mock_return_value = {"foo": 1}
    parse_mock_return_value = {
        "emoji": "❗",
        "items": {"description": ["http://foo.url"]},
        "stats": {"bar": 2, "foo": 1},
        "title": "🔵 titlu foo",
    }
