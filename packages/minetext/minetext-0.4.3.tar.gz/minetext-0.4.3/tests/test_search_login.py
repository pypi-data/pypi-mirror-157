import pytest
from requests import HTTPError
from minetext import EsRequest, Mine


class TestSearch:

    def test_search(self):
        """
        Test a simple search query.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)
        response = mine.search()
        assert response.took is not None

    def test_search_resource(self):
        """
        Test the search method on a specific resource
        """
        es_request = EsRequest(search_term='*', resources=['tda'])
        mine = Mine(es_request)
        response = mine.search()

        # Make sure that the response only from the tda index
        for hit in response:
            assert 'tda' in hit.meta.index

    def test_search_with_term_y_input(self, monkeypatch):
        """When user assures they signed in but did not.

        This test mocks an input of 'y'. When user types 'y'
        but is not logged in an HTTPError is raised.
        """
        es_request = EsRequest('Bingert')
        mine = Mine(es_request)

        # Mock user's input as y
        monkeypatch.setattr('builtins.input', lambda _: "y")
        with pytest.raises(HTTPError):
            mine.login()

    def test_search_with_term_n_input(self, monkeypatch):
        """When user assures they did not sign in.

        This test mocks an input of 'N'. When user types 'N'
        the login will not proceed and the search will be
        without restricted full text.
        """
        es_request = EsRequest('_exists_:content')
        mine = Mine(es_request)

        # Mock user's input as N
        monkeypatch.setattr('builtins.input', lambda _: "N")
        mine.login()

        # Search without authentication
        response = mine.search()
        assert response.success()

        # Make sure that it doesn't return the content
        for hit in response:
            assert not hasattr(hit, 'content')
