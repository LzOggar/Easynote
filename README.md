# Easynote
Easynote is a web application dedicated to privacy. Keep your data safe with Easynote.

## Usage
```
1. Register new user (you'll automatically redirect to /Dashboard/ page).
2. Create new Notes :
2.1 Set the name,
2.2 Set the content,
2.3 Click on the button Save.
```

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

4. Create the database db.sqlite3
```
python manage.py makemigrations Easynote
python manage.py migrate
```

5. Run the test
```
python manage.py runserver
```

6. Open your browser then browse to "localhost:8000"

## Built With

* [Python] 
* [Django] 
* [TinyMCE]
* [HighCharts]

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Authors

**LzOggar**
