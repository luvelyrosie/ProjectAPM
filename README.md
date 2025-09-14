# ProjectAPM

ProjectAPM is a FastAPI-based application for managing orders and tasks.  
It includes user authentication, CRUD operations for orders and tasks, and a PostgreSQL database.  
The project is fully containerized with Docker, making it easy to run and test on any machine.

---

## Features

* User registration and authentication (JWT)
* CRUD operations for orders and tasks
* Role-based access control (admin/operator)
* Full Docker containerization
* Database migrations with Alembic

---

## Deployment and Access

The project is available online:  

[ProjectAPM on Railway](https://projectapm.up.railway.app/)

Main orders page:  

[Orders Page](https://projectapm.up.railway.app/orders/page)

### Test Administrator

For testing orders and tasks creation, a test administrator account is available:  

- **Username:** admin  
- **Email:** admin@admin  
- **Password:** admin123  

With this user you can:  
- Create new orders  
- View all orders  
- Create tasks for orders  
- Change task statuses  
- View order and task details  

After logging in as administrator, you will be redirected to the main orders page.  

> **Important:** To create orders and tasks, you must use a user with the `admin` role.

---

## Installation and Run with Docker

### Requirements

* [Docker](https://www.docker.com/get-started) installed  
* [Docker Compose](https://docs.docker.com/compose/install/)  
* Optional: Python 3.11+ for local development  

---

1. Clone the repository:

```bash
git clone https://github.com/luvelyrosie/ProjectAPM.git
cd ProjectAPM
```

2. Build and start containers:

```bash
docker compose build
docker compose up -d
```

3. Apply database migrations:

```bash
docker compose run --rm web bash -c "cd backend && alembic upgrade head"
```

---

## Application Access

* FastAPI runs on port **8000**. Open in your browser or API client:

```
http://localhost:8000
```

* Orders main page:

```
http://localhost:8000/orders/page
```

4. Create a user with the `admin` role to be able to manage orders, tasks, and the full functionality of the app.  

* role: admin  

* Swagger UI documentation:

```
http://localhost:8000/docs
```

* Redoc API documentation:

```
http://localhost:8000/redoc
```

---

## Alembic Migrations

* Migration scripts are located in `backend/alembic/versions`.  
* To create a new migration:

```bash
docker compose run --rm web bash -c "cd backend && alembic revision -m 'your_message'"
docker compose run --rm web bash -c "cd backend && alembic upgrade head"
```

---

## Database Notes

* Each developer gets a **separate Postgres database** via Docker.  
* The database is created automatically when the container starts.  
* Alembic migrations create all tables and columns, including user roles and order/task relationships.  
* Initial data can be added through the admin user.  

---

## Running Locally (without Docker)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
uvicorn backend.app.main:app --reload
```

3. Apply migrations:

```bash
alembic upgrade head
```

---

## Additional Notes

* Make sure Postgres is running before applying migrations.  
* Database password is defined in `docker-compose.yml` and can be safely changed.  
* On a fresh setup, Alembic will create all tables and columns, and the application will be ready to run.  




# ProjectAPM

ProjectAPM — это приложение на FastAPI для управления заказами и задачами. Оно включает аутентификацию пользователей, операции CRUD для заказов и задач, а также базу данных PostgreSQL. Проект полностью контейнеризован с помощью Docker, что позволяет легко запускать и тестировать его на любой машине.

---

## Функции

* Регистрация и аутентификация пользователей (JWT)
* CRUD операции для заказов и задач
* Доступ на основе ролей (админ/оператор)
* Полная контейнеризация с Docker
* Миграции базы данных с Alembic

---

## Деплой и доступ к приложению

Проект доступен онлайн по ссылке:  

[ProjectAPM на Railway](https://projectapm.up.railway.app/)

Основная страница заказов:  

[Orders Page](https://projectapm.up.railway.app/orders/page)

Тестовый Администратор

Чтобы протестировать создание заказов и задач я создала тестового администратора, вы можете использовать тестового администратора:
\
Имя пользователя: admin

Email: admin@admin

Пароль: admin123

С этим пользователем вы сможете:

Создавать новые заказы

Просматривать все заказы

Создавать задачи для заказов

Менять статус задач

Просматривать детали заказов и задач

После входа администратора вы попадёте на главную страницу заказов:

> **Важно:** для создания заказов и задач необходимо использовать пользователя с ролью `admin`.

---

## Установка и запуск через Docker


## Требования

* [Docker](https://www.docker.com/get-started) установлен
* [Docker Compose](https://docs.docker.com/compose/install/)
* Необязательно: Python 3.11+ для локальной разработки

---

1. Клонируйте репозиторий:

```bash
git clone https://github.com/luvelyrosie/ProjectAPM.git
cd ProjectAPM
```

2. Постройте и запустите контейнеры:

```bash
docker compose build
docker compose up -d
```

3. Примените миграции базы данных:

```bash
docker compose run --rm web bash -c "cd backend && alembic upgrade head"
```

---

## Доступ к приложению

* FastAPI работает на порту 8000. Откройте в браузере или API-клиенте:

```
http://localhost:8000
```

* Главная страница заказов:

```
http://localhost:8000/orders/page
```

4. Создайте пользователя с ролью администратора, чтобы иметь возможность создавать заказы, задачи и управлять всем функционалом приложения.


* role: admin


* Swagger UI документация:

```
http://localhost:8000/docs
```

* Redoc API документация:

```
http://localhost:8000/redoc
```

---

## Миграции Alembic

* Скрипты миграций находятся в `backend/alembic/versions`.
* Чтобы создать новую миграцию:

```bash
docker compose run --rm web bash -c "cd backend && alembic revision -m 'ваше_сообщение'"
docker compose run --rm web bash -c "cd backend && alembic upgrade head"
```

---

## Замечания о базе данных

* Каждый разработчик получает **отдельную базу Postgres** через Docker.
* База создается автоматически при старте контейнера.
* Миграции Alembic создают все таблицы и колонки, включая роли пользователей и связи заказов/задач.
* Начальные данные можно добавить через админ-пользователя.

---

## Запуск локально (без Docker)

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запустите приложение:

```bash
uvicorn backend.app.main:app --reload
```

3. Примените миграции:

```bash
alembic upgrade head
```

---

## Дополнительно

* Убедитесь, что Postgres запущен перед применением миграций.
* Пароль базы данных указан в `docker-compose.yml` и может быть безопасно изменен.
* Для новой установки Alembic создаст все таблицы и колонки, приложение будет готово к запуску.
