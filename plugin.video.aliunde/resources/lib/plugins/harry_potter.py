# -*- coding: utf-8 -*-
"""
    Harry Potter
    Copyright (C) 2018,
    Version 1.0.1

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    -------------------------------------------------------------

    -------- These are the xml examples you place in your xml to call the plugin
          Make the tag relevant to your plugin. <harryp_movie> is the example below-----

    Returns the temp5late Movie list-

    <dir>
    <title>Harry Potter Movies</title>
    <harryp_movie>movies</harryp_movie>
    <thumbnail>https://ae01.alicdn.com/kf/HTB1lQBLJXXXXXcCaXXXq6xXFXXX6/Custom-Canvas-Art-Harry-Potter-Poster-Harry-Porter-Wall-Stickers-Harry-Porter-Wallpaper-Emma-Watson-Sticker.jpg_640x640.jpg</thumbnail>
    <fanart>https://exodus-themesurgesonslt.netdna-ssl.com/wp-content/uploads/2017/03/harry-potter.jpg</fanart>
    </dir>


    ---------------------

    Possible Genre's are:
    Documentary
    Extras
    Movie
    Audio Books

    -----------------------

    Genre tag examples

    <dir>
    <title>Harry Potter Movies</title>
    <harryp_movie>genre/Movie</harryp_movie>
	<fanart></fanart>
	<thumbnail></thumbnail>
	<summary>All Harry Potter Movies</summary>
    </dir>

    <dir>
    <title>Harry Potter Documentaries</title>
    <harryp_movie>genre/Documentary</harryp_movie>
	<fanart></fanart>
	<thumbnail></thumbnail>
	<summary>Harry Potter Docs</summary>
    </dir>    
	
	<dir>
    <title>Harry Potter Extras</title>
    <harryp_movie>genre/Extras</harryp_movie>
	<fanart></fanart>
	<thumbnail></thumbnail>
	<summary>Extras & Fan Made</summary>
    </dir> 
	
	<dir>
    <title>Harry Potter Audio Books</title>
    <harryp_movie>genre/Audio Books</harryp_movie>
	<fanart></fanart>
	<thumbnail></thumbnail>
	<summary>Audio Books</summary>
    </dir> 
    --------------------------------------------------------------

"""


import requests,re,os,xbmc,xbmcaddon
import koding,base64,pickle,time,xbmcgui
import resources.lib.external.tmdbsimple as tmdbsimple
from koding import route
from ..plugin import Plugin
from resources.lib.util.context import get_context_items
from resources.lib.util.xml import JenItem, JenList, display_list
from resources.lib.external.airtable.airtable import Airtable
from unidecode import unidecode


"""
----------------------------------------------------------
"""
table_id = "appfHeBBhg44AlpMO"
table_name = "Harry Potter"
workspace_api_key = "keyFw4tAzBr8ximp0"
"""
----------------------------------------------------------
"""


CACHE_TIME = 3600  # change to wanted cache time in seconds

addon_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
AddonName = xbmc.getInfoLabel('Container.PluginName')
AddonName = xbmcaddon.Addon(AddonName).getAddonInfo('id')



class Harryp_Movie_List(Plugin):

    name = "harryp_movie_list"


    def process_item(self, item_xml):
        if "<harryp_movie>" in item_xml:
            item = JenItem(item_xml)
            if "movies" in item.get("harryp_movie", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_harryp_movies",
                    'url': "",
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item

            elif "genre" in item.get("harryp_movie", ""):    
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_harryp_genre_movies",
                    'url': item.get("harryp_movie", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item 


@route(mode='open_harryp_movies')
def open_movies():
    pins = ""
    xml = ""
    at = Airtable(table_id, table_name, api_key=workspace_api_key)
    match = at.get_all(maxRecords=1200, sort=['name'])  
    for field in match:
        try:
            res = field['fields']   
            name = res['name']
            name = remove_non_ascii(name)
            summary = res['summary']
            summary = remove_non_ascii(summary)
            fanart = res['fanart']
            thumbnail = res['thumbnail']
            link1 = res['link1']
            link2 = res['link2']
            link3 = res['link3']
            link4 = res['link4']
            link5 = res['link5']
            if link2 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1)
            elif link3 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2) 
            elif link4 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3)
            elif link5 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3,link4)           
            else:
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3,link4,link5) 
        except:
            pass                                                                     
    jenlist = JenList(xml)
    display_list(jenlist.get_list(), jenlist.get_content_type(), pins)

@route(mode='open_harryp_genre_movies',args=["url"])
def open_genre_movies(url):
    pins = ""
    xml = ""
    genre = url.split("/")[-1]
    at = Airtable(table_id, table_name, api_key=workspace_api_key)
    try:
        match = at.search('type', genre)
        for field in match:
            res = field['fields']   
            name = res['name']
            name = remove_non_ascii(name)
            summary = res['summary']
            summary = remove_non_ascii(summary)
            fanart = res['fanart']
            thumbnail = res['thumbnail']
            link1 = res['link1']
            link2 = res['link2']
            link3 = res['link3']
            link4 = res['link4']
            link5 = res['link5'] 
            if link2 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1)
            elif link3 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2) 
            elif link4 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3)
            elif link5 == "-":
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3,link4)           
            else:
                xml += "<item>"\
                     "<title>%s</title>"\
                     "<meta>"\
                     "<content>movie</content>"\
                     "<imdb></imdb>"\
                     "<title></title>"\
                     "<year></year>"\
                     "<thumbnail>%s</thumbnail>"\
                     "<fanart>%s</fanart>"\
                     "<summary>%s</summary>"\
                     "</meta>"\
                     "<link>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>%s</sublink>"\
                     "<sublink>(Trailer)</sublink>"\
                     "</link>"\
                     "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3,link4,link5)                   
    except:
        pass                  
    jenlist = JenList(xml)
    display_list(jenlist.get_list(), jenlist.get_content_type(), pins)


def remove_non_ascii(text):
    return unidecode(text)
   
