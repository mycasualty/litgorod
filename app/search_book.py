import requests_html
from urllib3.util import parse_url
from requests_html import HTML
from collections import defaultdict

SCHEME = 'https://'
HOST = 'litgorod.ru'
CSS_PAGES_LST = 'a.b-paging__num'#'a[class~="b-paging__num"]'
CSS_FREE_BOOK = 'a.b-btn-outline-success'#'a[class~="b-btn-outline-success"]'
CSS_BUY_BOOK = 'div.buy-button'
CSS_BOOK = 'div.b-book_item__container' #'div[class~="b-book_item__container"]'
CSS_STATUS = 'div#search_list_status_book'
CSS_BOOK_NAME = 'a#search_list_book_name'
CSS_BOOK_AUTOR = 'div.b-book_item__author > div'  #(в тексте фио в ссылке на профиль  ид. авторов может быть несколько)
CSS_BOOK_CYCLE = 'div.b-book_item__cycle > a > b'
CSS_BOOK_GENRE = 'a#search_list_genre_book'
CSS_BOOK_STATUS = 'div#search_list_status_book'

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Chrome/92.0.4515.131 Safari/537.36"

total_pages = None


def get_page_number(url=None):
    """
    возвращает  значение параментра page из урла
    :param url: урл
    :return: значение парамерта или  none
    """
    target_url = parse_url(url)
    if target_url.host != HOST:
        raise ValueError(f'не верная ссылка, скрипт не работает с {target_url.host}')
    params = {params.split('=')[0]: params.split('=')[1] for params in target_url.query.split('&') if '=' in params}
    return params.get('page'), target_url.path, params


url = 'https://litgorod.ru/books/search?genre_id=3'
url = "https://litgorod.ru/books/search?q=love"

current_pages, url_path, params = get_page_number(url)

bot = requests_html.HTMLSession()
bot.headers.update({'user-agent': userAgent})
response = bot.get(SCHEME + HOST + url_path, params=params)
if response.status_code == 200:
    bot.headers.update(
        {'x-xsrf-token': response.cookies.get('XSRF-TOKEN'), 'x-csrf-token': response.cookies.get('XSRF-TOKEN')})

link_last = response.html.find(CSS_PAGES_LST)
if link_last:
    total_pages, *_ = get_page_number(link_last[-1].absolute_links.pop())

if total_pages and total_pages.isdigit():

    if current_pages and current_pages.isdigit():
        current_pages = input(
            'ищем книги начиная с {current_pages} или с самого начала? (по умолчанию поиск с 1 стр)') or 1
    else:
        current_pages = 1

else:
    current_pages = total_pages = 1

books_elements = {}
books_status = defaultdict(list)
books_autor = defaultdict(list)
books_cycle = defaultdict(list)
for page in range(current_pages, int(total_pages) + 1):
    print(f'проверяем страницу {page}')
    params['page'] = page
    response = bot.get(SCHEME + HOST + url_path, params=params)
    books = response.html.find(CSS_BOOK)
    for book in books:
        book_html = HTML(html=book.html)
        book_free = book_html.find(CSS_FREE_BOOK)

        if book_free:
            book_status = book_html.find(CSS_STATUS)[-1].text
            book_name = book_html.find(CSS_BOOK_NAME)[-1].text
            book_autor = book_html.find(CSS_BOOK_AUTOR)[-1].text
            book_cycle = book_html.find(CSS_BOOK_CYCLE) or None
            if book_cycle:
                book_cycle = book_cycle[-1].text

            book_link = book_free[-1].absolute_links.pop()
            books_status[book_status].append(book_link)
            books_cycle[book_cycle].append(book_link)

            for autor in book_autor.split(','):
                books_autor[autor.strip()].append(book_link)

            books_elements[book_link] = {
                'book_name': book_name,
                'book_autor': book_autor,
                'book_cycle': book_cycle,
                'books_status': book_status,
                'book_link': book_link
            }

print(f'всего книг наидено {len(books_elements)}')
