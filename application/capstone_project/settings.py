"""
Django settings for capstone_project project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from .hashers import ScryptPasswordHasher
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []
# SECURITY WARNING: keep the secret key used in production secret!
# Also make sure that you generate your own secret_key
try:
	with open('secret_key.txt','rb') as f:
		SECRET_KEY = f.read().strip()
except FileNotFoundError:
	# For development uncomment next line and comment out 3 below.
	# SECRET_KEY = 'KA7r3N2Tz9QIivMM8-AajrmYoJ3TztL6PgpohNG5iBLBMujOvNh2KAe-2h5zgE3GUUk'

	#comment out the next 4 lines for dev environments when you don't want the secret key file being wrote to.
	from secrets import token_urlsafe
	SECRET_KEY = token_urlsafe(60)
	with open('secret_key.txt','wb') as f:
		f.write(SECRET_KEY)

# Application definition

INSTALLED_APPS = [
	'ctf_club',
	#'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
#	'ctf_club.apps.CtfClubConfig',
	'ctf_club.apps.RateLimitedAdminConfig'
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'capstone_project.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates'),os.path.join(BASE_DIR,'ctf_club/templates')]
		#'DIRS': []
		,
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

STATICFILES_DIRS = [
	os.path.join(BASE_DIR,'static'),
	#os.path.join(BASE_DIR, 'ctf_club/../static')
]
WSGI_APPLICATION = 'capstone_project.wsgi.application'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
"""
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	},

}"""
#Uncomment the line below to have it run from postgres(as I am on the server.)
#and set the username and password to whatever you want it to be.
psql_user = os.getenv("PSQL_USER")
psql_pass = os.getenv("PSQL_PASS")

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'ctf_club',
		'USER': psql_user,
		'PASSWORD': psql_pass,
		'HOST': 'localhost',
		'PORT': '5432',
	}
}

AUTH_USER_MODEL = "ctf_club.User"

PASSWORD_HASHERS = [
	'capstone_project.hashers.ScryptPasswordHasher',
	# 'django.contrib.auth.hashers.BCryptSHA255PasswordHasher',
	# 'django.contrib.auth.hashers.PBKDF2PasswordHasher',
	# 'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
	# 'django.contrib.auth.hashers.Argon2PasswordHasher'
]
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': '127.0.0.1:11211',
	}
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

FIXTURE_DIRS = [
   'ctf_club/fixtures/',
]
