# Easynote
![alt text](https://github.com/LzOggar/Easynote/blob/master/images/Screenshot_2020-05-17%20Login.png)

# Encryption
* PBKDF2-HMAC used to derive a master key from your password,
* AES-512 used to encrypt your notes.

# How it works ?
We derive a master key from your password and we store it in your session. When you create a new Note, a random symetric key is generated then it used with AES-512 algorithm to encrypt your note. Finally, we encrypt your symetric key with your master key and AES-512 algorithm.

Keys and Notes are encrypted and stored in database. So, you are the only person who can decrypt your notes.
Important note, if you lost your password. We'll not able to recover it and all of your notes 'll be lost.

## Usage
1. Register new user (you'll automatically redirect to /Dashboard/ page).
2. Create new Notes :
- Set the name,
- Set the content,
- Click on the button Save.

### Installing
The project has been developed with Python3. You need to set up everything under Python3.
1. Clone the repository
```
git clone https://github.com/LzOggar/Easynote
```
2. Set up requirements
```
pip3 install -r Easynote/requirements.txt
```
3. Create a new project with django-admin
```
django-admin startproject Test
```
4. Copy Easynote folder in Test project
```
cp -r Easynote Test
```
5. Add the following configuration to Test/settings.py file
```
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
...
INSTALLED_APPS = [
    '...',
    'Easynote'
]
...
LOGIN_URL='/login/'
...
STATIC_ROOT = os.path.join(BASE_DIR, 'Easynote/static')
```
6. Add the following configuration to Test/urls.py file
```
...
rom django.conf.urls import include, handler403, handler404, handler500
from Easynote import views

handler403 = "Easynote.views.handler403"
handler404 = "Easynote.views.handler404"
handler500 = "Easynote.views.handler500"
...
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('dashboard/', include('Easynote.urls'))
]
```
7. Create the database db.sqlite3
```
python manage.py makemigrations Easynote
python manage.py migrate
```
8. Run the test
```
python manage.py runserver
```
9. Open your browser then browse to "localhost:8000"

## Features
- Register new users,
- Create new encrypted notes,
- Edit your notes,
- View your notes,
- Delete your notes,
- Export all notes in .json format,
- Change your password,
- Delete your account.

## Built With

* Python: https://www.python.org/
* Django: https://www.djangoproject.com/
* TinyMCE: https://www.tiny.cloud/
* HighCharts: https://www.highcharts.com/

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Authors

**LzOggar**
