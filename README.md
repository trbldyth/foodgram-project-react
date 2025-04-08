# Проект Foodgram

Foodgram - продуктовый помощник с базой кулинарных рецептов. В проекте реализованы следующие возможности:публикация рецептов, подписка на авторов продуктового помощника, формирование списка избранных рецептов, списка покупок.

### Стек технологий:

Python, Django, DRF, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
git clone git@github.com/trbldyth/foodgram-project-react.git
```

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

- Скопировать на сервер файл docker-compose.yml из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/
```

- Обьявить в директории с файлом .env файл
```
SECRET_KEY              # секретный ключ Django проекта
ALLOWED_HOSTS           # список разрешенных хостов для подключения
DEBUG                   # default=TRUE
PAGE_SIZE               # количество обьектов на странице, default=6
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DB_HOST
DB_PORT
```

- Создать и запустить контейнеры Docker, выполнить команду на сервере
```
sudo docker compose up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic
```

- Наполнить базу данных содержимым из файла ingredients.json:
```
sudo docker compose exec backend python manage.py loaddata ingredients.json
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

## Проект в интернете
Проект запущен и доступен по [адресу](https://foodgramtrlbdyth.ddns.net/recipes)
Доступ в админ-зону [здесь](https://foodgramtrlbdyth.ddns.net/admin/)
Username: root
Password: root

Документация к API доступна [здесь](https://foodgramtrlbdyth.ddns.net/api/docs/)

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

### Автор:

Михаил Байлаков
