# 📚 Library API

API для управления библиотекой: книги, авторы, выдача, пользователи, JWT-аутентификация.

## 🚀 Технологии

- Python 3.12
- Django 5.0 + DRF
- PostgreSQL
- Docker + Docker Compose
- JWT (SimpleJWT)
- drf-spectacular (OpenAPI)
- GitHub Actions (CI)

## 📦 Установка и запуск

### Локально

```bash
git clone <repo>
cd library_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🐋 Docker
```bash
docker-compose up --build
```
## 🧪 Тесты
```bash
coverage run manage.py test
coverage report
```
## 📖 Документация API
```bash
После запуска откройте:

Swagger UI: /api/docs/
ReDoc: /api/redoc/
```
## 🔐 Эндпоинты


| Метод | URL | Описание |
| :--- | :--- | :--- |
| **POST** | `/api/users/register/` | Регистрация |
| **POST** | `/api/users/token/` | Получить JWT |
| **GET** | `/api/books/` | Список книг |
| **POST** | `/api/books/` | Создать книгу |
| **PUT/PATCH** | `/api/books/{id}/` | Обновить книгу |
| **DELETE** | `/api/books/{id}/` | Удалить книгу |
| **GET** | `/api/loans/` | Мои выдачи |
| **POST** | `/api/loans/` | Взять книгу |
| **DELETE** | `/api/loans/{id}/` | Вернуть книгу |

## 🛠 Создатели

* **Разработка:** Глеб Трофимов ([@Getrom-raccoon](https://github.com/Getrom-raccoon))
* **Курирование и код-ревью:** Наставники Skypro
