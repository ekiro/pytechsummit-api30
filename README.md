Install gunicorn (or any other wsgi server)

```
pip install gunicorn
```

Run app:

```
$ gunicorn my_app:app
```

Test:

```
curl http://localhost:8000/
curl http://localhost:8000/user/1
```
