# Review environment

Windows, Python 3.13.13. These are the packages present during route/database checks, not a claim that all recognition dependencies were installed or a replacement for the project dependency files.

| Package | Version |
|---|---|
| Flask | 3.1.3 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-Login | 0.6.3 |
| Flask-WTF | 1.3.0 |
| Flask-Mail | 0.10.0 |
| Flask-SocketIO | 5.7.0 |
| SQLAlchemy | 2.1.4 |
| Werkzeug | 3.1.7 |
| numpy | 2.4.3 |
| pandas | 3.0.6 |
| opencv-python | 4.13.0.92 |
| python-dotenv | 1.2.4 |


## Fresh pinned-install verification

The original `requirements.txt` was installed into a new empty environment on Windows/Python 3.13.13; all four workflow tests passed. Full installed package snapshot:

```text
bidict==0.24.1
blinker==1.9.0
click==8.5.0
dnspython==2.9.0
email-validator==2.1.0
Flask==3.0.0
Flask-Login==0.6.3
Flask-Mail==0.9.1
Flask-SocketIO==5.3.6
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
h11==0.16.0
idna==3.20
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.4
python-dotenv==1.0.0
python-engineio==4.14.0
python-socketio==5.17.0
simple-websocket==1.1.0
SQLAlchemy==2.1.4
typing_extensions==4.16.0
Werkzeug==3.0.1
wsproto==1.3.2
WTForms==3.2.2
```
