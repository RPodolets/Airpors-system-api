# Airport system API

API for airport service, that developed with Django REST Framework. 

## Features
* JWT Authentication
* Filters with django query_params
* User can create order with tickets
* Swagger documentation

## API DB diagram
!["db-diagram"](airport_diagram.webp)

## Installation
### Windows
```commandline
git clone https://github.com/RPodolets/Airport-system-api.git
cd airport-system-api
python3 -m venv venv
venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
### Mac / Linux
```commandline
git clone https://github.com/RPodolets/Airport-system-api.git
cd airport-system-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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