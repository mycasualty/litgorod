"""
получаем словарь жанров
структура
{genre_id:ganre_name, genre_count (sub_genres(genre_id, ganre_name, genre_count)}
"""
import requests_html
from urllib.parse import parse_qs, urlparse
from requests_html import HTML
from collections import defaultdict

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Chrome/92.0.4515.131 Safari/537.36"

CSS_GENRES_MAP = "div.genres-map-list__block"
CSS_GENRE_BLOK = "div.genres-map-list__genre"
CSS_GENRE_COUNT = "div.genres-map-list__genre__count"
CSS_GENRE_LINK = "div.genres-map-list__genre"


def get_paramp(url=None, keep_blank_values=True):
    """
    Возвращает словароль параментров из url, каждый параеметр список.
    :param url: абсолтная ссылка для разбора.
    :keep_blank_values: параметрв с пустыми значениями,
               True - добавить ключ со значением []
               False - исключить ключ
    :return: словарь параметров запроса, каждыи ключь содержит список
    """
    return parse_qs(urlparse(url).query, keep_blank_values=keep_blank_values)


ganres = defaultdict(tuple)
url = 'https://litgorod.ru/genres'

bot = requests_html.HTMLSession()
bot.headers.update({'user-agent': userAgent})
response = bot.get(url)
if response.status_code == 200:
    bot.headers.update(
        {'x-xsrf-token': response.cookies.get('XSRF-TOKEN'), 'x-csrf-token': response.cookies.get('XSRF-TOKEN')})

genres_list = response.html.find(CSS_GENRES_MAP)

for block in genres_list:
    genre_block = HTML(html=block.html)
    genre_bl = genre_block.find(CSS_GENRE_BLOK)
    sub_genres = []
    for sub_genre in genre_bl:
        link = sub_genre.find("a").pop()
        genre_id = get_paramp(link.absolute_links.pop()).get("genre_id", ['']).pop()
        ganre_name = link.text.strip()
        genre_count = sub_genre.find(CSS_GENRE_COUNT).pop().text.strip()
        sub_genres.append((genre_id, ganre_name, genre_count))
    else:
        ganres[sub_genres[0][0]] = (sub_genres[0][1], sub_genres[0][2], sub_genres[1:])
