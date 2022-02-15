# Django Application Boilerplate

## Set up

1. Clone repository
```
git clone git@github.com:specollective/django-application-boilerplate.git
```

2. Set up environment variables
```
cp .env.development .env
```

4. Install dependencies
```
pip install -r requirements.txt
```

3. Run server
```
python manage.py runserver
```

4. Migrate database
```
python manage.py migrate
```

5. Test basic API
```
curl -X POST http://localhost:8000/api/projects/ \
     -d '{"title": "Example title", "description": "Example description"}' \
     -H 'Content-Type: application/json'
```
