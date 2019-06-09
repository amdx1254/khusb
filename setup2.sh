#! /bin/bash
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt
python3 manage.py makemigrations account
python3 manage.py makemigrations file
python3 manage.py migrate
python3 manage.py runserver 0:8000
