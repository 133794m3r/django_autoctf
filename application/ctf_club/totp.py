#  Macarthur Inbody <admin-contact@transcendental.us>
#  Licensed under LGPLv3 Or Later (2020)

import datetime
from functools import wraps
from urllib import parse
import pyotp
import qrcode

class TotpAuthorize:
	"""
	The TOTP Authorizer Class.
	"""
	def __init__(self, secret=None):
		if secret is None:
			secret = pyotp.random_base32()
		self.secret = secret
		self.totp = pyotp.TOTP(secret)

	def generate_token(self):
		"""
		Generates a TOTP token based on the given secret.

		:return: a token representing the current time.
		"""
		return self.totp.now()

	def valid(self, token:object) -> bool:
		"""

		:param token: The token we're going to check. It's either a string or an integer.
		:return: True if the token or the previous one is valid else False.
		"""
		token = int(token)
		now = datetime.datetime.now()
		prior_time = now + datetime.timedelta(seconds=-30)
		try:
			valid_now = self.totp.verify(token)
			valid_past = self.totp.verify(token, for_time=prior_time)
			return valid_now or valid_past
		except:
			return False

	def qrcode(self, username) -> object:
		"""

		:param username:The username of the token.
		:return: An PIL Image object representing the QRCode.
		"""
		uri = self.totp.provisioning_uri(username)
		#A hack to get around android-token not deocoding the URI for me.
		uri = parse.unquote(uri)
		return qrcode.make(uri)


def user_tfa_valid(view_func):
	"""
	Decorator that makes sure they have a valid 2fa token.
	:param view_func:
	:return:
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		#only check it if the user has been authenticated.
		if request.user.is_authenticated:
			#then check if they haven't enabled TFA no reason to require them to do it or to check the session variable.
			if request.user.tfa_enabled is False:
				return view_func(request,*args,**kwargs)

			#check if the user has not been verified.
			# elif request.session.get('verified_tfa', False) is False:
			# 	from django.http import HttpResponseRedirect
			# 	from django.urls import reverse
			# 	return HttpResponseRedirect(reverse('verify_tfa'))
			#they've already been verified apparently.
			else:
				return view_func(request, *args, **kwargs)
		else:
			return view_func(request,*args,**kwargs)

	return _wrapped_view