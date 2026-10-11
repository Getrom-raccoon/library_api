"""
Логика поиска книг по ISBN: Wildberries → Open Library → кэш.
"""
import json
import re
import urllib.request
import urllib.error


WB_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/141.0.0.0 Safari/537.36'
    ),
    'Accept': '*/*',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/',
}


def lookup_wb(isbn: str) -> dict | None:
    """Ищет книгу в WB. Возвращает dict или None."""
    url = (
        f'https://search.wb.ru/exactmatch/ru/common/v5/search'
        f'?query={isbn}&resultset=catalog&dest=-1257786'
    )
    try:
        req = urllib.request.Request(url, headers=WB_HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None
    except json.JSONDecodeError:
        return None

    products = (data.get('data') or {}).get('products') or []
    if not products:
        return None

    # Берём первый товар. WB ищет нечётко, потом можно улучшить
    # (проверять, есть ли ISBN в описании).
    p = products[0]

    # В списке WB нет автора/года/страниц — только название и бренд.
    # Бренд у книг WB = издательство, но иногда в brand пишут автора.
    title = (p.get('name') or '').strip()
    brand = (p.get('brand') or '').strip()

    # Пытаемся выделить автора: если brand похож на имя (2 слова с большой буквы)
    author = ''
    if brand and re.match(r'^[А-ЯЁA-Z][а-яёa-z]+ [А-ЯЁA-Z][а-яёa-z]+', brand):
        author = brand

    # Обложка
    nm_id = p.get('id')
    cover_url = None
    if nm_id:
        # Упрощённое построение URL. Иногда WB меняет хосты basket-01..basket-30,
        # но для базового просмотра этого достаточно.
        vol = nm_id // 100000
        part = nm_id // 1000
        cover_url = (
            f'https://basket-12.wbbasket.ru/vol{vol}/part{part}/{nm_id}'
            f'/images/big/1.webp'
        )

    return {
        'title': title,
        'author_name': author,
        'genre': '',
        'year': None,
        'pages': None,
        'cover_url': cover_url,
        'description': None,
        'source': 'wb',
        'raw_data': p,
    }


def lookup_openlibrary(isbn: str) -> dict | None:
    """Ищет книгу в Open Library. Возвращает dict или None."""
    try:
        with urllib.request.urlopen(
            f'https://openlibrary.org/isbn/{isbn}.json', timeout=10
        ) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

    title = data.get('title', '')
    subtitle = data.get('subtitle')
    if subtitle:
        title = f'{title}: {subtitle}'

    # Автор
    authors = []
    for a in (data.get('authors') or [])[:1]:
        key = a.get('key')
        if not key:
            continue
        try:
            with urllib.request.urlopen(
                f'https://openlibrary.org{key}.json', timeout=5
            ) as ar:
                ad = json.loads(ar.read().decode('utf-8'))
                if ad.get('name'):
                    authors.append(ad['name'])
        except Exception:
            pass

    # Год
    year = None
    publish_date = data.get('publish_date', '')
    m = re.search(r'\d{4}', publish_date)
    if m:
        year = int(m.group())

    # Жанр
    subjects = data.get('subjects') or []
    genre = subjects[0] if subjects else ''

    # Обложка
    covers = data.get('covers') or []
    cover_url = (
        f'https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg'
        if covers else None
    )

    return {
        'title': title,
        'author_name': authors[0] if authors else '',
        'genre': genre,
        'year': year,
        'pages': data.get('number_of_pages'),
        'cover_url': cover_url,
        'description': None,
        'source': 'openlibrary',
        'raw_data': None,
    }