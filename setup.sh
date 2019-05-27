#! /bin/bash

########### 환경변수 설정(자신의 python 파일이 있는 경로로 주소 바꿔줄 것) ##################
PATH=$PATH:/c/Users/guswl/AppData/Local/Programs/Python/Python37
PATH=$PATH:/c/Users/guswl/AppData/Local/Programs/Python/Python37/Scripts
python -m venv myvenv
python -m pip install --upgrade pip
pip install django~=2.0.0
pip install djangorestframework
pip install psycopg2
pip install djangorestframework_jwt
pip install boot3
pip install requests
cd file
############## aws.py에 들어갈 aws key와 secret key 입력 #####################
echo $'ikey=""\nsecret_key=""\E:x\n' | vi aws.py
cd ..
python manage.py migrate
python manage.py makemigrations
