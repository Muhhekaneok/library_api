# Library API — Тестовый проект со стажировки

## Описание

RESTful API для управления библиотекой.
Реализована базовая аутентификация, управление книгами и регистрация пользователей.
Проект написан на Python с использованием FastAPI и PostgreSQL (через psycopg2).

## Установка и запуск

1. Клонируй репозиторий:
   git clone git@github.com:.../library_api.git
2. Установи зависимости:
   pip install -r requirements.txt
3. Зпусти команду:
   uvicorn app.main:app --reload
4. Используй Swagger для документации либо Postman:
   http://127.0.0.1:8000/docs
5. Регистрация юзера (библиотекаря):
    - Выполните POST "/register" с email и паролем
6. Логин:
    - Выполнить POST "/login" -> получение JWT токена
    - Использовать "Authorization: Bearer <token>" в заголовке для защищённых маршрутов

В процессе работы Swagger UI не позволял полноценно работать и корректно вводить токен.
В результате чего было принято решение использовать Postman для копирования токена и его использования

## Структура Базы данных

### Таблица users
- "id" — int, primary key
- "email" — уникальный email библиотекаря
- "hashed_password" — хэшированный пароль

### Таблица books
- "id", "title", "author", "quantity"

### Таблица readers
- "id", "name", "email"

### Таблица borrowed_books
- "id", "book_id", "reader_id", "borrowed_date", "returned_date"
- Реализует связь между книгами и читателями посредством join

## Аутентификация
Используется:
- python-jose[cryptography] для генерации и верификации JWT токенов
- passlib[bcrypt] для безопасного хэширования паролей

JWT создается в "/login"
- Алгоритм: HS256
- Время действия: 45 минут (константа ACCESS_TOKEN_EXPIRE_MINUTES)
- Используется ключ SECRET_KEY
- Токен возвращается в формате:
  {
      "access_token": "<token>",
      "token_type": "bearer"
  }
- Маршруты "/books", "/borrow", "/return", "/readers", и т.п. защщены через "Depends(get_current_user)`.

### Регистрация (POST /register)
* Принимает: email и password
* Пароль хешируется с помощью bcrypt (passlib)
* Email валидируется через Pydantic (EmailStr)
* Защита от повторной регистрации с тем же email (ошибка 400)

### Логин (POST /login)
* Принимает email и password
* Ищет пользователя в базе
* Проверяет пароль (verify_password)
* Генерирует JWT токен с exp (время действия)

## Бизнес-логика
* Нельзя взять книгу, если её quantity = 0
* Нельзя взять книгу, если читатель уже держит 3 книги одновременно
* При возврате книги обновляется returned_date и quantity увеличивается

## ️ Сложности и решения
* Swagger UI не поддержал OAuth2 корректно, решено использованием Postman

## Принятые решения
* Использован python-jose[cryptography], т.е. по документации рекомендуется использовать именно его, а не просто
  python-jose из-за его современности и более высокой безопасности.
* psycopg2 используется напрямую без ORM, чтобы реализовать проект поэтапно, т.к. пока не сталкивался с этим.
  В дальнейшем планирую задействовать ORM.
* Все основные параметры (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES) оформлены как константы, чтобы не
  использовать стиль хардкод

## Покрытие тестами
* попытка взять недоступную книгу
* доступ к защищённому эндпоинту без токена

## Творческая фича
* Можно добавить эндпоинт `/reader-history/{reader_id}`, возвращающий все записи о взятых и возвращённых книгах 
  Реализация: дополнительный SELECT по "/borrowed_books" без фильтрации returned_date IS NULL.