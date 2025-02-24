import requests
from time import sleep
from random import randint
from html import unescape
from urllib3.util import parse_url

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/92.0.4515.131 Safari/537.36"

load_url = 'https://litgorod.ru/books/load-chapter/'
url = 'https://litgorod.ru/books/read/'


def convert_book_html(book=None):
    text = r'<!DOCTYPE html><html lang="ru-RU"><head></head><body bgcolor="#f7f0df" style="margin: 10%;"><h2>Название</h2>'
    for chapter in range(len(book)):
        text += f'<h3>{book[chapter][0]}</h3>'

        text += '\n'.join(
            (tx.replace('/images/pages/', 'https://litgorod.ru/images/pages/') for tx in book[chapter][1]))
    text += r'</body></html>'

    return unescape(text)


def save_book(book_text=None, file_name=None):
    with open(file_name, 'w', encoding='utf-8') as fl:
        fl.write(book_text)
        print(f'книга  записана \n{file_name}')


def chapter_loader(bot=None, chapter_request=None, chapter_url=None):
    """
    загружаем главу
    :param bot: авторизованая сессия
    :param chapter_request: json запроса
    :param chapter_url: урл  вебхука книги
    :return:
    """
    response = bot.post(chapter_url, json=chapter_request)
    if response.status_code == 200:
        boook_chapter = response.json()

        return ((boook_chapter['chapter']['name'], boook_chapter['chapter']['explodedParagraphs']), boook_chapter.get(
            'hasNextChapter'))


book_url = input('даи ссылку на книгу: ')
book_id = parse_url(book_url.strip()).path.split('/')[-1]

chapter_url = load_url + book_id
url_au = f'{url}{book_id}?chapter=1&page=1'
book = {}
chapter = -1
is_next = True

bot = requests.Session()
bot.headers.update({'user-agent': userAgent})
response = bot.get(url=url_au)
if response.status_code == 200:
    bot.headers.update({'x-xsrf-token': response.cookies['XSRF-TOKEN'], 'x-csrf-token': response.cookies['XSRF-TOKEN']})
    while is_next:
        chapter += 1
        sleep(randint(0, 3))
        chapter_request = {"type": "current", "fromChapterIndex": chapter, "lazyLoadChapter": True, }
        book[chapter], is_next = chapter_loader(bot=bot, chapter_request=chapter_request, chapter_url=chapter_url)

        print(f'глава {chapter + 1} загружена')

print('книга загружена, конвертируем и сохраняем ')
text = convert_book_html(book=book)
save_book(book_text=text, file_name=f'{book_id}.html')
