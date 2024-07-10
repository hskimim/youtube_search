# youtube_search

Python function for searching for youtube videos to avoid using their heavily rate-limited API

To avoid using the API, this uses the form on the youtube homepage and scrapes the resulting page.

```+) By accepting a parameter through the channel name, we made it possible to extract only information about the YouTube video of that channel.```

```+) If you search through channel_name, you can crawl video information sorted by {"latest", "popular", "oldest"}```

## Example Usage

For a basic search (and all of the current functionality), you can use the search tool as follows:

```you have to clone this repo for using it (no pip install version)```

```python
from youtube_search import YoutubeSearch

results = YoutubeSearch('AndrejKarpathy', max_results=10).to_json() # orgin repo's usage
print(results)

# returns a json string

########################################

results = YoutubeSearch('@AndrejKarpathy', video_sort_criteria='latest', max_results=10).to_json() # video only from channel
# there are sorting options {"latest", "popular", "oldest"}

print(results)
# returns a dictionary
```
