from base64 import urlsafe_b64decode
from dataclasses import dataclass
from bs4 import BeautifulSoup
from js2py import eval_js
from typing import Union
import requests
import os
import re


@dataclass
class DownloadSource:
    link: str
    file_name: str = None
    quality: Union[int, str] = None


@dataclass
class BaseClassStructure:
    link: str
    title: str = None
    poster_url: str = None
    rating: Union[int, str] = None
    soup: Union[BeautifulSoup, None] = None
    desc: str = None
    trailer: str = None

    def refresh_metadata(self, poster_only=False):
        title = self.title
        poster_url = self.poster_url
        rating = self.rating
        show_page_content = requests.get(self.link).text
        try:
            if not self.soup:
                self.soup = BeautifulSoup(show_page_content, features="html.parser")

            if not poster_only:
                name = self.soup.body.find(attrs={"itemprop": "name"})
                if name:
                    title = name.text

                rating_value = self.soup.body.find(attrs={"itemprop": "ratingValue"})
                if rating_value:
                    rating = rating_value.text

            img_class = self.soup.body.find(attrs={"class": "movie_img"})
            if img_class:
                img_tag = img_class.find("img")
                if img_tag:
                    poster_url = img_tag.get("src")

        finally:
            self.title = title
            self.poster_url = poster_url
            self.rating = rating

    def _get_class_children(self, find_atrr: str):
        return_list = []
        try:
            if not self.soup:
                page_content = requests.get(self.link).text
                self.soup = BeautifulSoup(page_content, features="html.parser")

                children = self.soup.body.find(attrs={'class': find_atrr}).findAll("a")
                for child in children:
                    child_link = child.get("href")

                    title_class = child.find(attrs={"class": "title"})
                    child_title = title_class and title_class.text

                    img_tag = child.find("img")
                    child_poster_url = img_tag and img_tag.get("src")

                    rating_class = child.find(attrs={"class": "i-fav rating"})
                    child_rating = rating_class and rating_class.text
                    if not self.desc:
                        try:
                            soup = BeautifulSoup(page_content, features="html.parser")
                            results_class = soup.findAll(attrs={'class': 'pda'})
                            for res in results_class:
                                if not ["pda"] == res["class"]:
                                    results_class.remove(res)

                            self.desc = results_class[1].contents[-1]
                        except Exception as e:
                            print(f"at desc {e}")

                    if not self.trailer:
                        try:
                            soup = BeautifulSoup(self.link, features="html.parser")
                            results_class = soup.findAll(attrs={'id': 'yt_trailer'})
                            self.trailer = results_class[0].next_element["url"]
                        except Exception as e:
                            print(f"at trailer fetch: {e}")

                    return_list.insert(0, BaseClassStructure(child_link, child_title, child_poster_url, child_rating, desc=self.desc, trailer=self.trailer))
        finally:
            return return_list


class Episode(BaseClassStructure):

    @staticmethod
    def __round_quality(original_qualiy) -> int:
        qualities = [2160, 1080, 720, 480, 360, 240]
        last_diffrence = abs(qualities[0] - original_qualiy)

        rounded_quality = qualities[0]
        for quality in qualities:
            difference = abs(quality - original_qualiy)
            if difference < last_diffrence:
                last_diffrence = difference
                rounded_quality = quality

        return rounded_quality

    def get_download_sources(self) -> list[DownloadSource]:
        download_links_list = []
        try:
            base_url = self.link.split("/")[0] + "//" + self.link.split("/")[2]

            session = requests.Session()

            if not self.soup:
                episode_page_content = requests.get(self.link).text
                self.soup = BeautifulSoup(episode_page_content, features="html.parser")

            episode_soup = self.soup

            vidstream_url = base_url + episode_soup.body.find("iframe", attrs={"class": "auto-size"}).get("src")

            vidstream_response_text = session.get(vidstream_url).text
            video_soup = BeautifulSoup(vidstream_response_text, features="html.parser")

            try:
                quality_links_file_url = base_url + video_soup.body.find("source").get("src")

            except AttributeError:
                jscode = str(video_soup.find_all("script")[1])

                verification_token = re.findall("\{'[0-9a-zA-Z_]*':'ok'\}", jscode)[0][2:-7]
                encoded_ad_link_var = re.findall("\([0-9a-zA-Z_]{2,12}\[Math", jscode)[0][1:-5]
                encoding_arrays_regex = re.findall(",[0-9a-zA-Z_]{2,12}=\[\]", jscode)
                first_encoding_array = encoding_arrays_regex[1][1:-3]
                second_encoding_array = encoding_arrays_regex[2][1:-3]

                jscode = re.sub("^<script type=\"text/javascript\">", "", jscode)
                jscode = re.sub("[;,]\$\('\*'\)(.*)$", ";", jscode)
                jscode = re.sub(",ismob=(.*)\(navigator\[(.*)\]\)[,;]", ";", jscode)
                jscode = re.sub("var a0b=function\(\)(.*)a0a\(\);", "", jscode)
                jscode += "var link = ''; for (var i = 0; i <= " + second_encoding_array + "['length']; i++) { link += " + first_encoding_array + "[" + second_encoding_array + "[i]] || ''; } return [link, " + encoded_ad_link_var + "[0]] }"

                js_code_return = eval_js(jscode)()
                verfication_path = js_code_return[0]
                encoded_ad_path = js_code_return[1]

                ad_link = base_url + "/" + str(urlsafe_b64decode(encoded_ad_path + "=" * (-len(encoded_ad_path) % 4)),
                                               "utf-8")
                session.get(ad_link)

                verification_link = base_url + "/tvc.php?verify=" + verfication_path
                session.post(verification_link, data={verification_token: "ok"})

                vidstream_response_text = session.get(vidstream_url).text
                video_soup = BeautifulSoup(vidstream_response_text, features="html.parser")

                quality_links_file_url = base_url + video_soup.body.find("source").get("src")

            quality_links = session.get(quality_links_file_url).text
            quality_links_array = quality_links.split("\n")[1::]

            for i in range(0, len(quality_links_array) - 2, 2):
                quality_info = quality_links_array[i]
                quality_regex = "[0-9]{3,4}x[0-9]{3,4}"
                quality = self.__round_quality(int(re.search(quality_regex, quality_info)[0].split("x")[1]))
                file_name = self.link.split("/")[4] + "-" + str(quality) + "p.mp4"
                media_link = requests.utils.quote(quality_links_array[i + 1], safe=":/").replace("_", "%5F").replace(
                    "/stream/", "/dl/").replace("/stream.m3u8", f"/{file_name}")

                download_links_list.append(DownloadSource(media_link, file_name, quality))

        finally:
            return download_links_list


class Season(BaseClassStructure):
    def get_episodes(self):
        episodes_list = []
        results = self._get_class_children("movies_small")
        for episode in results:
            episode = Episode(episode.link, episode.title, episode.poster_url, episode.rating, episode.soup, desc=episode.desc, trailer=episode.trailer)
            episodes_list.append(episode)
        return episodes_list


class Show(BaseClassStructure):
    def get_seasons(self):
        results = self._get_class_children("contents movies_small")
        seasons_list = []
        for res in results:
            season = Season(res.link, res.title, res.poster_url, soup=res.soup, desc=res.desc, trailer=res.trailer)
            seasons_list.append(season)
        return seasons_list


class EgyBest:
    def __init__(self, base_url: str = "https://lake.egybest.life"):
        self.base_url = base_url if "https://" in base_url else "https://" + base_url

    @staticmethod
    def __extract_info(url: str, look_for: str, include_movies: bool = False, include_shows: bool = False,
                       list_type: str = None) -> list[BaseClassStructure]:
        results_list = []

        try:
            search_response = requests.get(url)
            page_content = search_response.text
            soup = BeautifulSoup(page_content, features="html.parser")

            results_class = soup.body.find(attrs={"id": look_for, "class": look_for})

            search_results = results_class.findAll("a")
            for result in search_results:
                if " ".join(result.get("class")) == "auto load btn b":
                    continue

                link = result.get("href")
                title_class = result.find(attrs={'class': "title"})
                title = title_class and title_class.text

                img_tag = result.find('img')
                poster_url = img_tag and img_tag.get("src")

                rating_class = result.find(attrs={'class': 'i-fav rating'})
                rating = rating_class and rating_class.text
                trailer = None
                desc = None
                r = requests.get(link).text
                soup = BeautifulSoup(r, features="html.parser")
                try:
                    results_class = soup.findAll(attrs={'class': 'pda'})
                    for res in results_class:
                        if not ["pda"] == res["class"]:
                            results_class.remove(res)
                    desc = results_class[1].contents[-1]
                except Exception as e:
                    print(f"at desc {e}")

                try:
                    soup = BeautifulSoup(r, features="html.parser")
                    results_class = soup.findAll(attrs={'id': 'yt_trailer'})
                    trailer = results_class[0].next_element["url"]
                except Exception as e:
                    print(f"at trailer fetch: {e}")

                if link.split("/")[3] == "movie":
                    if list_type or include_movies:
                        results_list.append(Episode(link, title, poster_url, rating, trailer=trailer, desc=desc))
                elif link.split("/")[3] in ("series", "tv"):
                    if list_type or include_shows:
                        results_list.append(Show(link, title, poster_url, rating, trailer=trailer, desc=desc))
        finally:
            return results_list

    def search(self, qurey: str, include_shows: bool = True, include_movies: bool = True, ) -> Union[
        list[Show], list[BaseClassStructure]]:
        search_url = f"{self.base_url}/explore/?q={qurey}%20"
        return self.__extract_info(search_url, "movies", include_movies, include_shows)

    def __calculate_category(self, look_for: str, category: str, limit: int = 5) -> list:
        results_list = []
        try:
            results = None

            if category == "latest":
                results = self.__get_latest(list_type=look_for)

            if category == "top":
                results = self.__get_top(list_type=look_for)

            if category == "popular":
                results = self.__get_popular(list_type=look_for)

            limit = limit if limit <= len(results) else len(results)
            for i in range(limit):
                results_list.append(results[i])
        finally:
            return results_list

    def __get_latest(self, list_type: str) -> list[BaseClassStructure]:
        latest_url = f"{self.base_url}/{list_type}/latest/"
        results = self.__extract_info(latest_url, "movies", list_type=list_type)
        return results

    def get_latest_shows(self, limit: int = 5) -> list:
        return self.__calculate_category("tv", "latest", limit)

    def get_latest_movies(self, limit: int = 5) -> list:
        return self.__calculate_category("movies", "latest", limit)

    def __get_top(self, list_type: str) -> list[BaseClassStructure]:
        top_url = f"{self.base_url}/{list_type}/top/"
        results = self.__extract_info(top_url, "movies", list_type=list_type)
        return results

    def get_top_shows(self, limit: int = 5) -> list:
        return self.__calculate_category("tv", "top", limit)

    def get_top_movies(self, limit: int = 5) -> list:
        return self.__calculate_category("movies", "top", limit)

    def __get_popular(self, list_type: str) -> list[BaseClassStructure]:
        popular_url = f"{self.base_url}/{list_type}/popular/"
        return self.__extract_info(popular_url, "movies", list_type=list_type)

    def get_popular_shows(self, limit: int = 5) -> list:
        return self.__calculate_category("tv", "popular", limit)

    def get_popular_movies(self, limit: int = 5) -> list:
        return self.__calculate_category("movies", "popular", limit)
