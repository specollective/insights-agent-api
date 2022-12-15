# Insights Agent API

🚧 This repository is actively under development and should be consider unstable. 🚧

This service exposes a RESTful JSON API and administration panel for the Insights Agent application.

# Contributing

Clone repository the git repository.
```Shell
git clone git@github.com:specollective/insights-agent-api.git
cd insights-agent-api
```

## Software Architecture

```
├── README.md
├── api
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── auth.py
│   ├── migrations
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests
│   ├── utils.py
│   └── views.py
├── bin
│   ├── docs
│   ├── install
│   ├── lint
│   ├── serve
│   └── test
├── config
│   ├── __init__.py
│   ├── __pycache__
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── pages
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── templates
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── requirements.txt
```

# Setting up Development Environment (localhost)

### 1. Set environment variables
  ```Shell
  cp .env.development .env
  ```

### 2. Build the docker images
  ```Shell
  docker compose build
  ```

### 3. Start the database
  ```Shell
  docker compose up db
  ```

### 4. Start the webserver
  ```Shell
  docker compose up web
  ```

### 5. Create admin user
  ```Shell
  docker compose run web python manage.py createsuperuser --email example@example.com --username admin
  ```

**Note:** In the future you can  run `docker compose up` to start both db and web server. It is only necessary to run them separately the first time.


### 6. Running Tests
The application currently uses Django's out-of-the-box testing environment. You can run all tests using the manage.py comment.
  
  ```Shell
  docker compose run web python manage.py test
  ```

### 7. Setting breakpoints for debugging
  ```Python
  # Import ipdb at top of file
  import ipdb
  # Set interactive debugger in the code your
  ipdb.set_trace()
  ```

### 8. Test basic SMS API
  ```Shell
  curl -X POST https://insights-agent-api.specollective.org/api/resend_access_code \
      -d '{"phone_number": "+18888888888", "name": "John Shmo"}' \
      -H 'Content-Type: application/json'
  ```

**Note:** Right now, we are using a trial Twilio phone number for testing. Your phone number needs to be added to the verified caller list to be able to test sending messages to your phone number.

### 9. Local SSL setup

https://timonweb.com/django/https-django-development-server-ssl-certificate/

# Cors resources

Set-cookies for cross-origin requests
https://stackoverflow.com/questions/46288437/set-cookies-for-cross-origin-requests

Changing local domain
https://stackoverflow.com/questions/58715204/how-to-change-the-domain-name-on-a-local-deployed-react-app

A practical, Complete Tutorial on HTTP cookies
https://www.valentinog.com/blog/cookies

```Shell
curl -X POST http://localhost:8000/api/send_access_code \
  -d '{"phone_number": "+18888888888"}' \
  -H 'Content-Type: application/json'

curl -X POST http://localhost:8000/api/confirm_access_code \
  -d '{"access_code": "366997"}' \
  -H 'Content-Type: application/json'
```
