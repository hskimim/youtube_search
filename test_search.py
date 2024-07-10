from youtube_search import YoutubeSearch

keyword = "AndrejKarpathy"


class TestSearch:
    def test_init_defaults(self):
        search = YoutubeSearch(keyword)
        assert search.max_results is None
        assert 1 <= len(search.videos)

    def test_init_max_results(self):
        search = YoutubeSearch(keyword, max_results=10)
        assert 10 == search.max_results
        assert 10 == len(search.videos)

    def test_dict(self):
        search = YoutubeSearch(keyword, max_results=10)
        assert isinstance(search.to_dict(), list)

    def test_json(self):
        search = YoutubeSearch(keyword, max_results=10)
        assert isinstance(search.to_json(), str)

    def test_clear_cache(self):
        search = YoutubeSearch(keyword, max_results=10)
        json_output = search.to_json(clear_cache=False)
        assert "" != search.videos

        dict_output = search.to_dict()
        assert "" == search.videos

    def test_init_defaults_channel(self):
        search = YoutubeSearch("@" + keyword)
        assert search.max_results is None
        assert 1 <= len(search.videos)

    def test_init_max_results_channel(self):
        search = YoutubeSearch("@" + keyword, max_results=10)
        assert 10 == search.max_results
        assert 10 == len(search.videos)

    def test_dict_channel(self):
        search = YoutubeSearch("@" + keyword, max_results=10)
        assert isinstance(search.to_dict(), list)

    def test_json_channel(self):
        search = YoutubeSearch("@" + keyword, max_results=10)
        assert isinstance(search.to_json(), str)

    def test_clear_cache_channel(self):
        search = YoutubeSearch("@" + keyword, max_results=10)
        json_output = search.to_json(clear_cache=False)
        assert "" != search.videos

        dict_output = search.to_dict()
        assert "" == search.videos


if __name__ == "__main__":
    TestSearch().test_init_defaults()
    TestSearch().test_init_max_results()
    TestSearch().test_dict()
    TestSearch().test_json()
    TestSearch().test_clear_cache()
    TestSearch().test_init_defaults_channel()
    TestSearch().test_init_max_results_channel()
    TestSearch().test_dict_channel()
    TestSearch().test_json_channel()
    TestSearch().test_clear_cache_channel()
    print("All tests passed!")
