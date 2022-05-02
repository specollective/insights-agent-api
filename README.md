# Insights Agent API

# Contributing

Clone repository the git repository.
```Shell
git clone git@github.com:specollective/insights-agent-api.git
cd insights-agent-api
```

# Development Environment (localhost)

1. Set up environment variables
```Shell
cp .env.development .env
```

2. Set up python environment
```Shell
python3 -m venv python-env
```

3. Active python environment
```Shell
source python-env/bin/activate
```

4. Install dependencies
```Shell
pip install -r requirements.txt
```

5. Migrate database
```Shell
python manage.py migrate
```

7. Creating an admin user
```Shell
python manage.py createsuperuser --email example@example.com --username admin
```

8. Running development server
```Shell
python manage.py runserver
```

9. Running tests
```Shell
python manage.py test
```

10. Setting breakpoints for debugging
```Python
# Import ipdb at top of file
import ipdb
# Set interactive debugger in the code your
ipdb.set_trace()
```

11. Test basic project API
```
curl -X POST http://localhost:8000/api/projects/ \
     -d '{"title": "Example title", "description": "Example description"}' \
     -H 'Content-Type: application/json'
```

12. Test basic SMS API
```
curl -X POST http://localhost:8000/api/send_magic_link \
     -d '{"phone_number": "TEST_PHONE_NUMBER", "name": "John Shmo"}' \
     -H 'Content-Type: application/json'
```
  **Note:** Right now, we are using a trial Twilio phone number for testing. Your phone number needs to be added to the verified caller list to be able to test sending messages to your phone number.

14. Local SSL setup

https://timonweb.com/django/https-django-development-server-ssl-certificate/
