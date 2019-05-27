git clone https://github.com/Hi-friends/khusb.git
cd desktop
cd khusb
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
echo $'ikey=""\nsecret_key=""\E:x\n' | vi aws.py
cd ..
python manage.py migrate
python manage.py makemigrations
