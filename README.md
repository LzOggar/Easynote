# Easynote
![alt text](https://github.com/LzOggar/Easynote/blob/master/Images/Screenshot_2020-05-17%20Login.png)

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
1. Create a new project with django-admin
```
django-admin startproject Test
```
2. Clone the repository in the new django project
```
git clone https://github.com/LzOggar/Easynote
```
3. Add the following configuration to Test/settings.py file
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
4. Add the following configuration to Test/urls.py
```
...
from django.conf.urls import include
...
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Easynote.urls'))
]
```

5. Create the database db.sqlite3
```
python manage.py makemigrations Easynote
python manage.py migrate
```

6. Run the test
```
python manage.py runserver
```

7. Open your browser then browse to "localhost:8000"

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
