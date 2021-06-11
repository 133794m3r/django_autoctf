from django.contrib.admin import apps
from django.apps import AppConfig

class CtfClubConfig(AppConfig):
	name = 'ctf_club'

class RateLimitedAdminConfig(apps.AdminConfig):
	default_site = 'ctf_club.admin.RateLimitedAdmin'
