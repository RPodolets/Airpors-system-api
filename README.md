# Airport system API

API for airport service, that developed with Django REST Framework. 

## Features
* JWT Authentication
* Filters with django query_params
* User can create order with tickets
* Swagger documentation

## API DB diagram
!["db-diagram"](demo/airport_diagram.webp)

## Installation
### Windows
```bash
git clone https://github.com/RPodolets/Airport-system-api.git
cd airport-system-api
python3 -m venv venv
venv/bin/activate
pip install -r requirements.txt
set DB_HOST=<your_host>
set DB_NAME=<your_db_name>
set DB_USER=<your_db_user>
set DB_PASSWORD=<your_db_password>
set SECRET_KEY=<your_secret_key>
python manage.py migrate
python manage.py runserver
```
### Mac / Linux
```bash
git clone https://github.com/RPodolets/Airport-system-api.git
cd airport-system-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DB_HOST=<your_host>
export DB_NAME=<your_db_name>
export DB_USER=<your_db_user>
export DB_PASSWORD=<your_db_password>
export SECRET_KEY=<your_secret_key>
python manage.py migrate
python manage.py runserver
```

### Get from docker hub
```commandline
docker pull dexpod/airport-system-api:latest
```

### Run with Docker
```commandline
docker-compose build
docker-compose up
```

## Demo pages
![img.png](demo/img.png)
![img.png](demo/img_1.png)
![img_2.png](demo/img_2.png)
![img_3.png](demo/img_3.png)
![img_4.png](demo/img_4.png)
![img_5.png](demo/img_5.png)
![img_6.png](demo/img_6.png)
![img_7.png](demo/img_7.png)