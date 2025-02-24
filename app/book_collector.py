import requests_html
from urllib.parse import urlparse, parse_qs, urlunsplit
from requests_html import HTML
from collections import defaultdict
from time import sleep
from random import randint


class Book_collector ():
    """
    Класс для работы с книжным сайтом, поиска и загрузки открытых книг
    без авторизации в аккаунте
    """
    _SCHEME = 'https'
    _HOST = 'litgorod.ru'
    _service_path = ''  # строка или тупел к сервису хоста
    _service_params = None # словарь параметров запроса


    _CSS_PAGES_LST = 'a.b-paging__num'

    _CSS_BOOK = 'div.b-book_item__container'
    _CSS_FREE_BOOK = 'a.b-btn-outline-success'
    _CSS_BUY_BOOK = 'div.buy-button'
    _CSS_BOOK_STATUS = 'div.b-book_item__status'  #'div#search_list_status_book'
    _CSS_BOOK_NAME = 'div.b-book_item__name' # ссылка внутри дива на  книгу 'a#search_list_book_name'
    _CSS_BOOK_AUTOR = 'div.b-book_item__author'   #a#book_autor_name - каждая ссылка отдельный автор со своим ид в поиске ссылка без класса  ан стр книги с классом
    _CSS_BOOK_CYCLE = 'div.b-book_item__cycle > a > b'
    _CSS_BOOK_GENRES = 'a#search_list_genre_book'


    _CSS_GENRES_MAP = "div.genres-map-list__block"
    _CSS_GENRE_BLOCK = "div.genres-map-list__genre"
    _CSS_GENRE_COUNT = "div.genres-map-list__genre__count"
    _CSS_GENRE_LINK = "div.genres-map-list__genre"

    _userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                "Chrome/92.0.4515.131 Safari/537.36"

    def __init__(self):
            self.bot = requests_html.HTMLSession()
            self.bot.headers.update({'user-agent': self._userAgent})
            response = self.bot.get(self.url, params=self._service_params)
            if response.status_code == 200:
                self.bot.headers.update(
                    {'x-xsrf-token': response.cookies.get('XSRF-TOKEN'),
                     'x-csrf-token': response.cookies.get('XSRF-TOKEN')})

            self.genres = defaultdict(tuple)
            self.books = defaultdict(dict)


    @property
    def url(self):
        return urlunsplit((self._SCHEME, self._HOST, self._service_path, None, None))


    def url_paramp(self, url=None, keep_blank_values=True):
        """
        Возвращает словароль параментров из url, каждый параеметр список.
        :param url: абсолтная ссылка для разбора.
        :keep_blank_values: сохранять ключи без значений,
                   True - добавить ключ со значением []
                   False - исключить ключ
        :return: записываеи части урл по атрибутам
        """
        target_url = urlparse(url)
        if target_url.netloc != self._HOST:
            raise ValueError(f'не верная ссылка, скрипт не работает с {target_url.host}')
        self._service_params = parse_qs(target_url.query, keep_blank_values=keep_blank_values)
        self._service_path = target_url.path

    def genres_load(self):
        """
        загуржаем словарь жанров
        структура
        {genre_id:ganre_name, genre_count (sub_genres(genre_id, ganre_name, genre_count)}
        :return:
        """

        self._service_path = 'genres'
        response = self.bot.get(self.url, params=self._service_params)
        genres_list = response.html.find(self._CSS_GENRES_MAP)

        for block in genres_list:
            genre_block = HTML(html=block.html)
            genre_bl = genre_block.find(self._CSS_GENRE_BLOCK)
            sub_genres = []
            for sub_genre in genre_bl:
                link = sub_genre.find("a").pop()
                self.url_paramp(link.absolute_links.pop())
                genre_id = self._service_params.get("genre_id", ['']).pop()
                ganre_name = link.text.strip()
                genre_count = sub_genre.find(self._CSS_GENRE_COUNT).pop().text.strip()

                sub_genres.append((genre_id, ganre_name, genre_count))
            else:
                self.genres[sub_genres[0][0]] = (sub_genres[0][1], sub_genres[0][2], sub_genres[1:])


    def get_book_info(self, books):
        """
        разбираем блок книги, преобразуем в обьект
        :param book: html блок книги
        :return:
        """
        for book in books:
            book_html = HTML(html=book.html)
            book_free = book_html.find(self._CSS_FREE_BOOK)
            book_buy = book_html.find(self._CSS_BUY_BOOK)
            book_name = book_html.find(self._CSS_BOOK_NAME)
            book_autor = book_html.find(self._CSS_BOOK_AUTOR)
            book_genres = book_html.find(self._CSS_BOOK_GENRES)
            book_cycle = book_html.find(self._CSS_BOOK_CYCLE)
            book_status = book_html.find(self._CSS_BOOK_STATUS)

            yield  book_id

    def book_loader(self, book_id, chapter=0):

        self._service_path = f'books/load-chapter/{book_id}'
        is_next = True
        while is_next:
            sleep(randint(0, 3))
            chapter_request = {"type": "current", "fromChapterIndex": chapter, "lazyLoadChapter": True, }
            response = self.bot.post(self.url, json=chapter_request)
            if response.status_code == 200:
                boook_chapter = response.json()
                is_next = boook_chapter.get('hasNextChapter')
                if not boook_chapter['chapter'].get('need_pay'): # boook_chapter['chapter'].get('is_free')
                    self.books[book_id][chapter] = (boook_chapter['chapter']['name'], boook_chapter['chapter']['explodedParagraphs'])
                    print(f'глава {chapter + 1} загружена')
                else:
                    self.books[book_id]['need_pay'] = True
                    break
            else:
                input('что то не то')
            chapter += 1


    def seabook_searchrch(self, genre_id=None, status_id=None, search_text=None, sort=None, page=None, need_pay=None ):
        """
        по поиску ищем книги и собираем информацию
        :param genre_id: id жанра , необязательно
        :param status_id: 1 - в процессе , 2 - полный текст, необязательно
        :param search_text: поисковая  фраза , необязательна (Саша + Ларина)
        :param sort: сортировка результата, необязательна (rating comments new likes)
        :param need_pay: платно /бесплатно  параметры  для скрипта
        :return:
        """
        self._service_path = 'books/search'
        self._service_params = {'genre_id': genre_id,
                                'status_id': status_id,
                                'search_text': search_text,  # привести сроку в порядок
                                'sort': sort,
                                'page': page
                                }
        response = self.bot.get(self.url, params=self._service_params)

        if response.status_code == 200:
            self.get_book_info(response.html.find(self._CSS_BOOK))
            link_last = response.html.find(self._CSS_PAGES_LST)
            if link_last:
                self.url_paramp(link_last[-1].absolute_links.pop())
                total_pages = self._service_params.get('page', 1)
                for current_pages in range(2,int(total_pages)+1):
                    self._service_params['page'] = current_pages
                    response = self.bot.get(self.url, params=self._service_params)
                    if response.status_code == 200:
                        self.get_book_info(response.html.find(self._CSS_BOOK))


my_book = Book_collector()

input('жанры загружены')



