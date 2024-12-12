# Streaming Test Project to test out asynchronous behaviour of django using channel and websockets

**Setup environment**
```bash
python3 -m venv venv
source ./venv/bin/activate # Mac only
```

**Install requirements**
```bash
pip install -r requirements.txt
```

**Run migrations**
```
python manage.py makemigrations
python manage.py migrate
```

## Done with the boilerplate, let's see it in action

**First run redis**
```bash
redis-server
```

**Then start django server using uvicorn**
```bash
uvicorn streaming_test.asgi:application --reload
```

**Now open localhost:8000 and see websocket & asynchronous power of django in action**