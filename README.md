# Baby AI Security Backend
Веб-сервер для сервиса родительского контроля Baby AI Security. Предоставляет API для предсказания категории текста на основе искусственного интеллекта, а также API для работы с пользователем.

### Список предсказываемых категорий
- Табак
- Порнография
- Нейтральный текст
- Азартные игры
- Насилие
- Политика
- Алкоголь
## Установка
Инструкция по установке и запуску.
1. Клонировать репозиторий:
    ```bash
    git clone https://github.com/r0manb/baby-ai-security-backend.git

    cd baby-ai-security-backend
    ```
2. Установить зависимости:
    ```Bash
    pip install -r requirements.txt
    ```
3. Скачать [архив](https://drive.google.com/file/d/1574SL22ZYm-MZ7Sa9WS9KmhA2FMvZZEY/view?usp=sharing) с моделью и распаковать его в директорию `model/`.
4. Переименовать файл `.env.example` в `.env`.
5. Установить [PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads), если не установлен, и запустить.
6. Установить [Redis](https://redis.io/downloads/), если не установлен, и запустить.
7. Открыть и заполнить `.env`.
8. Запустить `db_handler.py` для создания необходимых таблиц.
9. Запустить `app.py` 
## Документация API
Доступные эндпоинты:
- **POST** `/api/auth/register` - регистрировать пользователя
- **POST** `/api/auth/login` - авторизовать пользователя
- **POST** `/api/auth/user_confirmation` - аутентифицировать пользователя
- **POST** `/api/auth/logout` - деавторизовать пользователя
- **POST** `/api/auth/refresh` - обновить refresh токен
- **POST** `/api/predict` - предсказать категорию
- **GET** `/api/user/history` - получить историю пользователя

## Стек
Используемый стек технологий:
- Python 3.10.5
- Flask 3.0.3
- PostgreSQL 16.6
- Redis 7.4.1
- pyJWT 2.9.0
- pytorch 2.4.1
- transformers 4.45.1