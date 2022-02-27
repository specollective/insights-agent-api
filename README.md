# Django Application Boilerplate

# Getting the source code

Clone repository the git repository.
```
git clone git@github.com:specollective/django-application-boilerplate.git
cd django-application-boilerplate
```

# Development Environment (localhost)

1. Set up environment variables
```
cp .env.development .env
```

2. Set up python environment
```
python3 -m venv python-env
```

3. Active python environment
```
source python-env/bin/activate
```

4. Install dependencies
```
pip install -r requirements.txt
```

5. Migrate database
```
python manage.py migrate
```

6. Run server
```
python manage.py runserver
```

7. Test basic API
```
curl -X POST http://localhost:8000/api/projects/ \
     -d '{"title": "Example title", "description": "Example description"}' \
     -H 'Content-Type: application/json'
```
