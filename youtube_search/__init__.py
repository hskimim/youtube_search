import json
import urllib.parse
from typing import NamedTuple

import requests  # type: ignore

from youtube_search import constant


class Category(NamedTuple):
    click_param: str
    token: str


class Criteria(NamedTuple):
    client_id: str
    category: dict[str, Category]


def request_call(url, **kwargs) -> str:
    if kwargs.get("headers") is None:
        response = requests.get(url)
    else:
        response = requests.post(url, **kwargs)
    if response.status_code == 200:
        response = response.text
    else:
        msg = f"Failed to fetch data from {url} | status code : {response.status_code}"
        raise requests.exceptions.HTTPError(msg)
    return response


class YoutubeSearch:
    def __init__(
        self,
        search_terms: str,
        video_sort_criteria: str = "latest",
        max_results: int | None = None,
    ):
        self.search_terms = search_terms

        if video_sort_criteria not in constant.VIDEO_SORTING_CATEGORY:
            raise ValueError(
                f"Invalid sorting criteria. Choose from {constant.VIDEO_SORTING_CATEGORY}"
            )
        self.video_sort_criteria = video_sort_criteria

        self.max_results = max_results
        self.videos = self._search()

    def _parse_html2json(self, response, trim: bool = True):
        if trim:
            if "ytInitialData" not in response:
                raise ValueError("Invalid html response")

            start = response.index("ytInitialData") + len("ytInitialData") + 3
            end = response.index("};", start) + 1
            json_str = response[start:end]
        else:
            json_str = response

        data = json.loads(json_str)
        return data

    def _parse_for_tokens(self, response) -> Criteria:
        data = self._parse_html2json(response)
        client_id = data["responseContext"]["serviceTrackingParams"][4]["params"][0][
            "value"
        ]
        category = {}
        video_category_tags = data["contents"]["twoColumnBrowseResultsRenderer"][
            "tabs"
        ][1]["tabRenderer"]["content"]["richGridRenderer"]["header"][
            "feedFilterChipBarRenderer"
        ]["contents"]
        if len(video_category_tags) != 3:
            print("error in parsing video category tags")

        for idx, meta in enumerate(video_category_tags):
            click_param = meta["chipCloudChipRenderer"]["navigationEndpoint"][
                "clickTrackingParams"
            ]
            token = meta["chipCloudChipRenderer"]["navigationEndpoint"][
                "continuationCommand"
            ]["token"]

            category[constant.VIDEO_SORTING_CATEGORY[idx]] = Category(
                click_param=click_param, token=token
            )

        return Criteria(client_id=client_id, category=category)

    def _search(self):
        if self.search_terms.startswith("@"):
            return self._search_with_channel_name()
        elif self.search_terms is not None:
            return self._search_with_terms()

    def _search_with_terms(self) -> list[dict]:
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        url = f"{constant.BASE_URL}/results?search_query={encoded_search}"
        response = request_call(url)
        results = self._parse_html_with_terms(response)
        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]
        return results

    def _search_with_channel_name(self) -> list[dict]:
        url = f"{constant.BASE_URL}/{self.search_terms}/videos"
        response = request_call(url)
        criteria = self._parse_for_tokens(response)

        data = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": f"{criteria.client_id}.00.00",
                }
            },
            "continuation": criteria.category[self.video_sort_criteria].token,
            "clickTrackingParams": criteria.category[
                self.video_sort_criteria
            ].click_param,
        }
        response = request_call(
            constant.YOUTUBE_DEFAULT_URL, headers=constant.DEFAULT_HEADER, json=data
        )
        results = self._parse_html_with_channel_name(response)

        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]
        return results

    def _video_tag_parser(self, video) -> dict:
        res = {}
        video_data = video.get("videoRenderer", {})
        res["id"] = video_data.get("videoId", None)
        res["thumbnails"] = [
            thumb.get("url", None)
            for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])
        ]
        res["title"] = (
            video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
        )
        res["long_desc"] = (
            video_data.get("descriptionSnippet", {})
            .get("runs", [{}])[0]
            .get("text", None)
        )
        res["channel"] = (
            video_data.get("longBylineText", {}).get("runs", [{}])[0].get("text", None)
        )
        res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
        res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
        res["publish_time"] = video_data.get("publishedTimeText", {}).get(
            "simpleText", 0
        )
        res["url_suffix"] = (
            video_data.get("navigationEndpoint", {})
            .get("commandMetadata", {})
            .get("webCommandMetadata", {})
            .get("url", None)
        )
        return res

    def _parse_html_with_terms(self, response) -> list[dict]:
        results = []
        data = self._parse_html2json(response)

        for contents in data["contents"]["twoColumnSearchResultsRenderer"][
            "primaryContents"
        ]["sectionListRenderer"]["contents"]:
            for video in contents["itemSectionRenderer"]["contents"]:
                if "videoRenderer" in video.keys():
                    results.append(self._video_tag_parser(video))

            if results:
                return results
        return results

    def _parse_html_with_channel_name(self, response) -> list[dict]:
        results = []
        data = self._parse_html2json(response, trim=False)

        for contents in data["onResponseReceivedActions"][1][
            "reloadContinuationItemsCommand"
        ]["continuationItems"]:
            if "richItemRenderer" not in contents.keys():
                continue
            results.append(
                self._video_tag_parser(contents["richItemRenderer"]["content"])
            )
        if results:
            return results
        return results

    def to_dict(self, clear_cache=True) -> dict:
        result = self.videos
        if clear_cache:
            self.videos = ""
        return result

    def to_json(self, clear_cache=True) -> str:
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = ""
        return result
