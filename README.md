# Django AutoCTF
This repo is broken up into 2 folders. One for the django application, and one for the database/server configurations.

## Running Locally
If you are running it just locally w/o a DB server comment out the postgres section and uncomment the sqlite file.
## SECRET KEY
If you don't already have a `secret_key.txt` in your application folder upon running then `settings.py` will generate it for you. This is so that you never don't have a good strong secret token.

## Installation Locally/Server
The instructions below don't assume you're going to use a virtual environment. It's up to you chose if you want to have one.

```
pip3 install -r requirements.txt
./manage.py makemigrations
./manage.py migrate
./manage.py loaddata initial_data
```

### Server Installation
Follow instructions in the server files folder. Install uwsgi via either ```pip3 install uwsgi``` or via your package manager. 

Installation instructions will assume debian. For your own system you'll have to translate package names.

```
apt-get install nginx nginx-extras postgresql memcached
```
For pcre library it requires that you install pcre-dev. And you have to enable it, as I have in the wsgi.ini file. This is an optimization that can make uwsgi run faster in some circumstances.


### Requirements
Also requires Python 3.6 or later as it utilizes hashlib for Scrypt.

pip3 install -r requirements.txt
