# Backend - Face-recognition Based Attendance Taking System

## Setup

### Docker

First, make sure docker and docker-compose are installed. For installation guide, visit [Docker Docs](https://docs.docker.com/) and select appropriate OS on the bottom of the page.

under the project root directory run

```sh
docker-compose up
```

The docker compose will automatically pull the required images and config them. (ref: docker-compose.yml)

After building (first time may take a longer time), the backend server will be ready at port `8000`.

### Django Super User and Admin Page

To create super users for `django`

```bash
docker-compose run web python manage.py createsuperuser
```

The admin page will be accessble at `http://{DJANGO_SERVER_URL}/admin`. For example, if you are running the server locally at port 8000, then `http://localhost:8000/admin`

### Creating new users

New users can be created from the django admin page:
  1. Visit the django admin page at `http://localhost:8000/admin`,
  2. Login with the super user created in the previous section,
  3. Click `➕Add` in `Users` under `AUTHENTICATION AND AUTHORIZATION`
  4. Type in the credentials and click save.
  5. You will be able to use the user created to login from the frontend
 
## Test

run tests

```
$ python manage.py test
```

run coverage

```
$ coverage run manage.py test
$ coverage report
```

generate html report

```
$ coverage run manage.py test && coverage html
```

open htmlcov/index.html
