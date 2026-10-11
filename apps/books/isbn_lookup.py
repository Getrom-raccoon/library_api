"""
Поиск книг по ISBN через Open Library.

Покрытие русских книг у OL слабое — если книга не находится,
пользователь заполняет поля вручную, а ISBN попадает в БД приложения
и становится частью локальной коллекции.
"""
import json
import re
import urllib.request
import urllib.error


def lookup_openlibrary(isbn: str) -> dict | None:
    """
    Ищет книгу в Open Library по ISBN.
    Возвращает dict с полями для ISBNCache или None, если не нашлось.
    """
    # Санитайзер: только цифры и X (для ISBN-10)
    isbn = re.sub(r'[^0-9Xx]', '', isbn)
    if len(isbn) < 10:
        return None

    try:
        with urllib.request.urlopen(
            f'https://openlibrary.org/isbn/{isbn}.json', timeout=10
        ) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        # 404 — книги нет в OL, это нормально
        if e.code == 404:
            return None
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    title = data.get('title', '').strip()
    if not title:
        return None

    subtitle = data.get('subtitle')
    if subtitle:
        title = f'{title}: {subtitle}'

    # Автор (первый из списка)
    author = ''
    authors = data.get('authors') or []
    if authors:
        key = authors[0].get('key')
        if key:
            try:
                with urllib.request.urlopen(
                    f'https://openlibrary.org{key}.json', timeout=5
                ) as ar:
                    ad = json.loads(ar.read().decode('utf-8'))
                    if ad.get('name'):
                        author = ad['name']
            except Exception:
                # Если автора не получилось — не страшно
                pass

    # Год
    year = None
    publish_date = data.get('publish_date', '') or ''
    m = re.search(r'\d{4}', publish_date)
    if m:
        year = int(m.group())

    # Жанр (первая тема)
    subjects = data.get('subjects') or []
    genre = subjects[0] if subjects else ''

    # Обложка
    covers = data.get('covers') or []
    cover_url = None
    if covers and covers[0] > 0:
        cover_url = f'https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg'

    # Страницы
    pages = data.get('number_of_pages')

    return {
        'title': title,
        'author_name': author,
        'genre': genre,
        'year': year,
        'pages': pages,
        'cover_url': cover_url,
        'description': None,
        'source': 'openlibrary',
        'raw_data': None,
    }