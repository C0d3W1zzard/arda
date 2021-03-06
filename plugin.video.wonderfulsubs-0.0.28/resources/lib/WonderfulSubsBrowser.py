import urllib
import math
import itertools
import json
from ui import utils
from ui.BrowserBase import BrowserBase

class WonderfulSubsBrowser(BrowserBase):
    _BASE_URL = "https://www.wonderfulsubs.com"
    _RESULTS_PER_SEARCH_PAGE = 25

    def __init__(self, base_flavor):
        super(WonderfulSubsBrowser, self).__init__()
        self._FILTER_FLAVOR = self._filter_flavor_key(base_flavor)

    def _filter_flavor_key(self, base_flavor):
        flavor_key = {
            "Subs Only": "is_subbed",
            "Dubs Only": "is_dubbed",
            "None": None
            }

        return flavor_key[base_flavor]

    def _parse_anime_view(self, res):
        result = []
        image = res.get("poster_tall", None)
        if image:
            image = image.pop()['source']

        base = {
            "name": res["title"],
            "url": "animes/" + res["url"].replace("/watch/", ""),
            "image": image,
            "plot": res["description"],
        }

        if self._FILTER_FLAVOR:
            return self._parse_filtered_anime_view(res, base)

        if res.get("is_dubbed", None):
            result.append(utils.allocate_item("%s (Dub)" % base["name"],
                                              "%s/dub" % base["url"],
                                              True,
                                              base["image"],
                                              base["plot"]))
        if res.get("is_subbed", None):
            result.append(utils.allocate_item("%s (Sub)" % base["name"],
                                              "%s/sub" % base["url"],
                                              True,
                                              base["image"],
                                              base["plot"]))


        return result

    def _parse_filtered_anime_view(self, res, base):
        result = []

        if res.get(self._FILTER_FLAVOR, None):
            result.append(utils.allocate_item(base["name"],
                                              "%s/%s" % (base["url"], self._FILTER_FLAVOR[3:6]),
                                              True,
                                              base["image"],
                                              base["plot"]))

        return result

    def _parse_history_view(self, res):
        name = res
        return utils.allocate_item(name, "search/" + name + "/1", True)

    def _handle_paging(self, total_results, base_url, page):
        total_pages = int(math.ceil(total_results /
                                    float(self._RESULTS_PER_SEARCH_PAGE)))
        if page == total_pages:
            return []

        next_page = page + 1
        name = "Next Page (%d/%d)" % (next_page, total_pages)
        return [utils.allocate_item(name, base_url % next_page, True, None)]

    def _handle_watchlist_paging(self, results, base_url, page):
        pages_html = self._PAGES_WATCHLIST_TOTAL_RE.findall(str(results))
        # No Pages? empty list ;)
        if not len(pages_html):
            return []

        total_pages = int(self._PAGES_WATCHLIST_TOTAL_RE.findall(str(results))[-2])
        if page >= total_pages:
            return [] # Last page

        next_page = page + 1
        name = "Next Page (%d/%d)" % (next_page, total_pages)
        return [utils.allocate_item(name, base_url % next_page, True, None)]

    def _json_request(self, url, data):
        response = json.loads(self._get_request(url, data))
        if response["status"] != 200:
            raise Exception("Request %s returned with error code %d" % (url,
                                                                        response["status"]))

        return response["json"]


    def _process_anime_view(self, url, data, base_plugin_url, page):
        json_resp = self._json_request(url, data)
        results = json_resp["series"]
        total_results = json_resp["total_results"]

        all_results = map(self._parse_anime_view, results)
        all_results = list(itertools.chain(*all_results))

        all_results += self._handle_paging(total_results, base_plugin_url, page)
        return all_results

    def _format_episode(self, sname, anime_url, is_dubbed, ses_idx, einfo, kitsu_id):
        desc = None if not einfo.has_key("description") else einfo["description"]
        image = None
        if einfo.has_key("thumbnail") and len(einfo["thumbnail"]):
            image_idx = 0 if len(einfo["thumbnail"]) == 1 else 1
            image = einfo["thumbnail"].pop(image_idx).get("source", None)

        sources = self._format_sources(sname, is_dubbed, einfo)

        base = {}

        if einfo.has_key("ova_number"):
            base.update({
                "name": einfo["title"],
                "id": str(einfo["ova_number"]),
                "url": "play/%s/%s/%d/%s/%s" % (anime_url,
                                          "dub" if is_dubbed else "sub",
                                          ses_idx,
                                          str(einfo["ova_number"]),
                                          kitsu_id),
                "sources": sources,
                "image": image,
                "plot": desc,
            })

        else:
            base.update({
                "name": einfo["title"] if "Episode" in einfo["title"] else "Ep. %s (%s)" %(einfo["episode_number"], einfo["title"]), 
                "id": str(einfo["episode_number"]),
                "url": "play/%s/%s/%d/%s/%s" % (anime_url,
                                          "dub" if is_dubbed else "sub",
                                          ses_idx,
                                          str(einfo["episode_number"]),
                                          kitsu_id),
                "sources": sources,
                "image": image,
                "plot": desc,
            })
        return base

    def _format_sources(self, sname, is_dubbed, einfo): 
        sources = {}

        value = einfo.get("sources", None)
        if value is None:
            rlink = einfo["retrieve_url"]
            sources.update(self._format_link(sname, rlink))
            return sources

        source_obj = einfo["sources"]
        filter_sources = filter(lambda x: x["language"] == "dubs" if is_dubbed else x["language"] == "subs" , source_obj)

        for sindex, i in enumerate(filter_sources):
            if len(i) != 3:
                sname = "Server %d %s" %(sindex, (i.keys()[2]).capitalize())
            else:
                sname = "Server %d" %(sindex)

            rlink = i["retrieve_url"]
            sources.update(self._format_link(sname, rlink))

        return sources

    def _format_link(self, sname, rlink):
        if type(rlink) is list:
            rlink = rlink[0]

        video_data = {
            "code": rlink,
            "platform": "Kodi",
            }
        link = "%s?%s" % (self._to_url("api/media/stream"), urllib.urlencode(video_data))
        return {sname: link}

    def _get_anime_info_obj(self, anime_url):
        results = self._json_request(self._to_url("/api/media/series"), {
            "series": anime_url,
        })

        return results

    def _strip_seasons(self, server, is_dubbed):
        seasons = []
        seasons += server["media"]
        return seasons

    def _get_anime_info(self, anime_url, is_dubbed):
        obj = self._get_anime_info_obj(anime_url)
        image = obj.get("poster_tall", None)
        if image:
            image = image.pop()['source']

        seasons = {}
        ses_idx = 0
        for sindex, s in enumerate(obj["seasons"].values()):
            for season_col in self._strip_seasons(s, is_dubbed):
                ses_obj = {
                    "episodes": {},
                    "id": ses_idx,
                    "url": "animes/%s/%s/%d" % (
                        anime_url,
                        "dub" if is_dubbed else "sub",
                        ses_idx,
                    ),
                }

                if not season_col.has_key("title"):
                    if season_col["type"] == "specials":
                        ses_obj["name"] = "Special"
                    else:
                        ses_obj["name"] = "Episodes"
                else:
                    ses_obj["name"] = season_col["title"]

                ses_obj["image"] = "https://media.kitsu.io/anime/poster_images/%s/large.jpg" %(season_col.get("kitsu_id", ''))
                ses_obj["plot"] = season_col.get("description", None)

                # TODO: by ID, not name
                if seasons.has_key(ses_obj["name"]):
                    ses_obj = seasons[ses_obj["name"]]
                else:
                    seasons[ses_obj["name"]] = ses_obj
                    ses_idx += 1
                eps = ses_obj["episodes"]

                for einfo in season_col["episodes"]:
                    ep_flv_dubbed = einfo.get("is_dubbed", None)
                    if not ep_flv_dubbed and is_dubbed:
                        continue

                    ep_info = self._format_episode("Server %d" % sindex,
                                                   anime_url, is_dubbed,
                                                   ses_obj["id"], einfo,
                                                   season_col.get("kitsu_id", None))
                    if not eps.has_key(ep_info["id"]):
                        eps[ep_info["id"]] = ep_info
                        continue

                    old_ep_info = eps[ep_info["id"]]
                    if not old_ep_info["image"]:
                        old_ep_info["image"] = ep_info["image"]
                    if not old_ep_info["plot"]:
                        old_ep_info["name"] = ep_info["name"]
                        old_ep_info["plot"] = ep_info["plot"]
                    old_ep_info["sources"].update(ep_info["sources"])

        return {
            "name": obj["title"],
            "image": image,
            "plot": obj["description"],
            "url": "animes/%s/%s" % (anime_url, "dub" if is_dubbed else "sub"),
            "seasons": dict([(str(i['id']), i) for i in seasons.values()]),
        }

    def _get_anime_episodes(self, info, season, desc_order):
        season = info["seasons"][season]
        episodes = sorted(season["episodes"].values(), reverse=desc_order, key=lambda x:
                          float(x["id"]))
        return map(lambda x: utils.allocate_item(x['name'],
                                                 x['url'],
                                                 False,
                                                 x['image'],
                                                 x['plot']), episodes)

    def search_site(self, search_string, page=1):
        data = {
            "q": search_string,
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }

        url = self._to_url("api/media/search")
        return self._process_anime_view(url, data, "search/%s/%%d" % search_string, page)

    # TODO: Not sure i want this here..
    def search_history(self,search_array):
    	result = map(self._parse_history_view,search_array)
    	result.insert(0,utils.allocate_item("New Search", "search", True))
    	result.insert(len(result),utils.allocate_item("Clear..", "clear_history", True))
    	return result

    def get_by_letter(self, letter, page = 1):
        data = {
            "letter": letter.lower(),
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }
        url = self._to_url("api/media/all")
        return self._process_anime_view(url, data, "letter/%s/%%d" % letter, page)

    def get_all(self,  page=1):
        data = {
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }
        url = self._to_url("api/media/all")
        return self._process_anime_view(url, data, "all/%d", page)

    def get_popular(self,  page=1):
        data = {
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }
        url = self._to_url("api/media/popular")
        return self._process_anime_view(url, data, "popular/%d", page)

    def get_latest(self, page=1):
        data = {
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }
        url = self._to_url("api/media/latest")
        return self._process_anime_view(url, data, "latest/%d", page)

    def get_random(self, page=1):
        data = {
            "count": self._RESULTS_PER_SEARCH_PAGE,
            "index": (page-1) * self._RESULTS_PER_SEARCH_PAGE,
        }
        url = self._to_url("api/media/random")
        return self._process_anime_view(url, data, "random/%d", page)

    def get_anime_metadata(self, anime_url, is_dubbed):
        info = self._get_anime_info(anime_url, is_dubbed)
        return (info["name"], info["image"])

    def get_anime_seasons(self, anime_url, is_dubbed, desc_order):
        info = self._get_anime_info(anime_url, is_dubbed)
        if len(info["seasons"]) == 1:
            return self._get_anime_episodes(info, info["seasons"].keys().pop(), desc_order)

        seasons = sorted(info["seasons"].values(), key=lambda x: x["id"])
        return map(lambda x: utils.allocate_item(x['name'],
                                                 x['url'],
                                                 True,
                                                 x["image"],
                                                 x["plot"]), seasons)

    def get_anime_episodes(self, anime_url, is_dubbed, season, desc_order):
        info = self._get_anime_info(anime_url, is_dubbed)
        return self._get_anime_episodes(info, season, desc_order)

    def get_episode_sources(self, anime_url, is_dubbed, season, episode):
        info = self._get_anime_info(anime_url, is_dubbed)
        if not info["seasons"]: return []
        season = info["seasons"][season]

        ep = season["episodes"][episode]
        return ep["sources"]
