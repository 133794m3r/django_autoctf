#all of the django specific stuff.
import re
from json import dumps as json_encode
# JSON items.
from json import loads as json_decode

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404, FileResponse, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

# ratelimiter
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE

from .captcha import check_captchas, generate_captchas
from .totp import TotpAuthorize, user_tfa_valid

#re-adding the lost method
def __is_ajax(obj):
	return obj.headers.get('X-Requested-With') == 'XMLHttpRequest'
HttpRequest.is_ajax = __is_ajax
"""
CTFClub Project
By Macarthur Inbody <admin-contact@transcendental.us>
Licensed AGPLv3 Or later (2020)
"""

#TODO: May make it so that all solves/hints/etc also check for TFA being valid
# but for now I won't.

from .models import *
from .util import *

def is_ratelimited(request):
	return getattr(request,'limited',False)


# Create your views here.
@require_http_methods(("GET","POST"))
# @ratelimit(key='ip',rate='20/m')
def profile(request,username):
	return render(request,'control_panel.html')

@ratelimit(key='ip',rate='1/s')
@user_tfa_valid
def index(request):
	challenges=Challenges.objects.all()
	chals= make_index(challenges)
	return render(request,"index.html",{'objects':chals})

@require_http_methods(("GET","POST"))
@ratelimit(key='ip',rate='30/m',method=UNSAFE)
@ratelimit(key='post:username',rate='5/m',method=UNSAFE)
def login_view(request):
	if is_ratelimited(request):
		if request.session.get('require_captcha',False):
			captcha_expires = timezone.datetime.utcfromtimestamp(request.session.get('captcha_expires'))
			if request.session.get('captcha_valid', False) and captcha_expires < timezone.datetime.utcnow():
				request.session['captcha_valid'] = False
		else:
			request.session['captcha_valid'] = False
			request.session['require_captcha'] = True
	else:
		if request.session.get('require_captcha'):
			captcha_expires = timezone.datetime.utcfromtimestamp(request.session.get('captcha_expires'))
			if request.session.get('captcha_valid',False) and captcha_expires > timezone.datetime.utcnow():
				request.session['require_captcha'] = False

	show_captcha = False
	valid = True
	img_str = ''
	captcha_msg = ''
	color_name = ''
	message = ''
	# if they're rate-limited send this message.
	if is_ratelimited(request):
		message = "You're trying to fast please slow down."
		request.session['require_captcha'] = True
		valid = False
		show_captcha = True

	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]

		#if the captcha is wrong then don't even bother trying to auth them.
		if request.session.get('require_captcha',False) and request.session.get('captcha_valid') is False:
			captcha_expires = timezone.datetime.utcfromtimestamp(request.session.get('captcha_expires'))

			if captcha_expires < timezone.datetime.utcnow():
				message += "Captcha expired."
				valid = False
				show_captcha = True
			else:
				user_math_ans = request.POST.get('year','')
				user_letters_ans = request.POST.get('letters','')
				if not check_captchas(request,user_letters_ans,user_math_ans):
					valid = False
					show_captcha = True

		if valid:
			user = authenticate(request,username=username,password=password)
			request.session['failed_logins'] = request.session.get('failed_logins',0) + 1
			if user is not None:
				login(request,user)
				request.session['require_captcha'] = False
				request.session['captcha_valid'] = False
				if user.tfa_enabled:
					totp_authorizer = TotpAuthorize(user.tfa_secret)
					if totp_authorizer.valid(request.POST.get('token')):
						request.session['verified_tfa'] = True
					else:
						return HttpResponseRedirect(reverse("verify_tfa")+'?next='+request.POST.get('next_url'))

				from django.utils.http import url_has_allowed_host_and_scheme
				nxt = request.POST.get("next_url")
				if nxt and url_has_allowed_host_and_scheme(url=nxt,allowed_hosts={request.get_host()},require_https=request.is_secure()):
					return HttpResponseRedirect(nxt)
				else:
					return HttpResponseRedirect(reverse("index"))

			else:
				valid = False
				message += "Invalid username and/or password."
		if request.session.get('failed_logins',0) > 2:
			request.session['require_captcha'] = True
			show_captcha = True

		if not valid and show_captcha:
			captcha_msg, color_name, img_str = generate_captchas(request)
		return render(request,"login.html",{"message":message,"captcha_msg":captcha_msg,"color_name":color_name,"img_str":img_str,"show_captcha":show_captcha})
	else:
		if request.session.get('require_captcha',False):
			captcha_msg,color_name,img_str = generate_captchas(request)
		return render(request,"login.html",{"message":message,"captcha_msg":captcha_msg,"color_name":color_name,"img_str":img_str,"show_captcha":show_captcha})


@login_required(login_url="login")
@require_http_methods(["GET"])
def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse("index"))


@require_http_methods(["GET"])
def challenge_view(request,challenge_id):
	files = None
	if request.user.is_authenticated:
		solved = False if Solves.objects.filter(user_id=request.user.id,challenge_id=challenge_id).count() == 0 else True

		#If they've already solved it might as well show them the flag.
		if solved:
			chal = Challenges.objects.values('id','name','description','points','flag',"files__filename").get(id=challenge_id)
		else:
			chal = Challenges.objects.values('id', 'name', 'description', 'points',"files__filename").get(id=challenge_id)
		#a hack to get files by the proper name.
		chal["files"] = [chal["files__filename"]] if type(chal["files__filename"]) is str else chal["files__filename"]
		chal.pop("files__filename")

	else:
		solved = False
		chal = Challenges.objects.values('id', 'name', 'description', 'points').get(id=challenge_id)

	hints = Hints.objects.filter(challenge_id=chal['id']).values('id','level')
	num_hints = hints.count()
	chal = jsonify_queryset(chal)
	hints = jsonify_queryset(hints)
	resp = {'challenge': chal, 'hints': hints, 'num_hints':num_hints,'solved':solved,'authed':request.user.is_authenticated}
	return JsonResponse(resp)


@require_http_methods(("GET","POST"))
@ratelimit(key='ip',rate='30/m',method=UNSAFE)
def register(request):
	signup_valid = True
	if request.user.is_authenticated:
		return HttpResponseRedirect('index')


	if request.method == "POST":
		message = ''
		if getattr(request,'limited',False):
			captcha_msg,color_name,img_str = generate_captchas(request)
			return render(request, "register.html",
			              {"message":"You're going too fast. Slow down.",
			               "captcha_msg":captcha_msg, "color_name":color_name,
			               "img_str":img_str})

		username = request.POST.get("username")
		email = request.POST.get("email")

		password=request.POST.get("password")
		confirmation=request.POST.get("password_confirm")
		user_math_ans = request.POST.get("year")
		user_letters = request.POST.get("letters")
		try:
			password_score = int(request.POST.get("password_score",0))
		except ValueError:
			password_score = 255
		check_captchas(request,user_letters,user_math_ans)


		if request.session.get('captcha_valid',True):
			if password != confirmation:
				signup_valid = False
				message = "Passwords must match."
			elif password is None:
				signup_valid = False
				message = message + "Passwords can't be blank."
			elif len(password) < 6 or password_score < 3:
				signup_valid = False
				message = message + "Password must meet minimum requirements."

			if username is None:
				signup_valid = False
				message = message + "Username can't be blank."
			elif re.match('[^A-Za-z_\-0-9]',username):
				signup_valid = False
				message = message + "Username must only contain uppercase and lowercase letters, numbers, '-', and '_'."


			if signup_valid:
				try:
					user = User.objects.create_user(username=username,email=email,password=password)
					user.save()
					login(request,user)
					request.session.pop('captcha_valid')
					request.session.pop('correct_letters')
					request.session.pop('captcha_answer')
					return HttpResponseRedirect(reverse("index"))
				except IntegrityError as e:
					print(e)
					signup_valid = False
					message = message+"Username must be unique."



		else:
			signup_valid = False
			message = "Invalid captcha."

		if signup_valid is False:
			captcha_msg, color_name, img_str = generate_captchas(request)
			return render(request,"register.html",{"message":message,
			                                       "captcha_msg":captcha_msg,"color_name":color_name,"img_str":img_str})


	else:
		captcha_msg, color_name, img_str = generate_captchas(request)
		return render(request, "register.html", {"captcha_msg": captcha_msg, "color_name": color_name, "img_str": img_str})


@login_required(login_url="login")
@require_http_methods(["POST"])
@ratelimit(key='user',rate='20/m')
def solve(request,challenge_id):
	was_solved = False
	ratelimited = False
	if is_ratelimited(request):
		ratelimited = True
	else:
		challenge = Challenges.objects.filter(pk=challenge_id).first()
		if challenge is None:
			return Http404()
		data = json_decode(request.body)

		#Make sure that all matches are case-insensitve for simplicty's sake.
		answer = data['answer'].upper()
		correct_flag = challenge.flag.upper()
		points = challenge.points
		solved = Solves.objects.get(user=request.user,challenge_id=challenge_id).first()
		#if they have solved something don't do anything else.
		if solved:
			was_solved = True
		#they hadn't already solved it see if they did solve it.
		elif answer == correct_flag:
			#if so make sure to create a new solve.
			new_solve = Solves.objects.create(
				user=request.user,
				challenge_id=challenge_id
			)
			new_solve.save()
			#modify the number of solves to increase it by one.
			challenge.num_solves +=1
			challenge.save()
			was_solved = True
			#Really really stupid way to do an update statement here. But MVC is the future they say.
			# would be so much simpler to simply do an sql query like.
			# update ctf_club_user set points = points + challenge_points where id = user_id
			#One clean line of SQL instead of 3 lines of nonsense.
			user = User.objects.get(pk=request.user.id)
			user.points+=points
			user.save()
		#otherwise no solve was had.
		else:
			was_solved = False

	return JsonResponse({'solved':was_solved,'ratelimited':ratelimited})


@login_required(login_url="login")
@require_http_methods(("GET","POST"))
def challenge_hint(request,challenge_id):
	pass


@require_http_methods(("GET","POST"))
def hint(request,hint_id):
	if request.user.is_authenticated:
		unlocked = HintsUnlocked.objects.filter(hint_id=hint_id,user_id=request.user.id)

		if unlocked.count() == 0:
			hint_unlock = HintsUnlocked.objects.create(hint_id=hint_id,user_id=request.user.id)
	else:
		pass
	#give them just the hint itself as part of the result.
	revealed_hint = jsonify_queryset(Hints.objects.filter(id=hint_id).values('description'))

	return JsonResponse(revealed_hint)


@login_required(login_url="login")
@require_http_methods(("GET","POST"))
@user_tfa_valid
def control_panel(request,username):
	msg = ''
	if request.user.is_authenticated:
		if request.method == "POST":
			content = json_decode(request.body)
			old_password=content['old_password']
			new_password=content['new_password']
			confirm_password=content['confirm_password']
			if is_ratelimited(request):
				msg = "You're submitting too fast."
			elif old_password == '' or new_password == '':
				msg = "Passwords can't be blank."
			elif old_password != new_password and new_password == confirm_password:
				if request.user.check_password(old_password):
					request.user.set_password(new_password)
					request.user.save()
					update_session_auth_hash(request,request.user)
					msg = "Password updated successfully."
				else:
					msg = "Password does not match your old password."

			elif old_password == new_password:
				msg = "New password is the same as the old password."
			elif new_password != confirm_password:
				msg = "New passwords must match."

			return JsonResponse({'ok':True,'msg':msg})
	points = User.objects.get(username=username).points

	return render(request,'control_panel.html',{'points':points,'username':username})


@ratelimit(key='user',rate='30/m')
@login_required(login_url="login")
@user_tfa_valid
def solves(request,username = ''):

	if username == '':
		user_solves = Solves.objects.filter(user=request.user)
		username = request.user.username
	else:
		user_solves = Solves.objects.filter(user__username=username)

	if user_solves.first() is None:
		all_solves = {}
		num_solves = 0
	else:
		all_solves = jsonify_queryset(user_solves.all())
		num_solves = user_solves.count()

	return render(request,"solves.html",{"objects":all_solves,'num_solves':num_solves,'username':username})


@login_required(login_url="login")
@require_http_methods(("GET","POST"))
@user_tfa_valid
def challenge_admin(request):
	#for the sorting of the challenges later.
	from operator import itemgetter
	#If the user is not an admin or in the staff pretend like this route doesn't exist.
	if not (request.user.is_staff or request.user.is_superuser):
		return HttpResponseRedirect('/')
	elif not request.user.tfa_enabled:
		return HttpResponseRedirect(reverse('two_factor'))

	if request.method == "POST":
		files = None
		content = json_decode(request.body)
		name = content['name']
		category = content['category']

		if content['sn'] == 'fizzbuzz':
			minimum = content['min']
			maximum = content['max']
			description,flag = CHALLENGE_FUNCS[content['sn']](minimum, maximum)
		elif category == "Programming":
			chal_index = CHALLENGES_TEMPLATES_NAMES[name][1]
			if CHALLENGES_TEMPLATES[chal_index]['files']:
				description, flag, files = CHALLENGE_FUNCS[content['sn']]()
			else:
				description,flag = CHALLENGE_FUNCS[content['sn']]()
		elif category == "Programing Interactive":
			chal_index = CHALLENGES_TEMPLATES_NAMES[name][1]
			description,flag = CHALLENGE_FUNCS[content['sn']]()
		else:
			plaintext = content['plaintext']
			if content['sn'] in ["affine","hill"]:
				variety = content['variety']
				name +=f' - {variety}'
				description,flag = CHALLENGE_FUNCS[content['sn']](plaintext,variety)
			else:
				description,flag = CHALLENGE_FUNCS[content['sn']](plaintext)
		points = content.get('points') or 100

		if content.get('edit'):
			challenge = Challenges.objects.get(name=name)
			challenge.description = description
			challenge.flag = flag
			challenge.num_solves = 0
			challenge.save()
			#remove all solves for the challenge as it's been modified
			old_solves = Solves.objects.filter(challenge_id=challenge.id)
			for user_solve in old_solves:
				User.objects.filter(pk=user_solve.user_id).update(points=0)
			#delete the old solves finally.
			old_solves.delete()

		else:
			challenge = Challenges.objects.create(
				name = name,
				description = description,
				flag = flag,
				points = points,
				category = Categories.objects.get(name=category)
			)
			if files is not None:
				file_obj = Files.objects.create(
					filename=files
				)
				challenge.files.add(file_obj)

		return JsonResponse({'description':description,'flag':flag,'files':files})
	else:
		challenges = Challenges.objects.all()
		all_challenges = []
		challenges_used = []
		base_challenges = []
		varieties_used = {}
		for challenge in challenges:
			#Remove the - {VARIETY} part.
			#This is a hack until I modify the model to include the "variety" flag.
			if '-' in challenge.name and challenge.name[-1].isdigit():
				tmp_name = challenge.name[:-4]
				variety = int(challenge.name[-1])
			else:
				tmp_name = challenge.name
				variety = None

			if tmp_name in CHALLENGES_TEMPLATES_NAMES:
				indexed = CHALLENGES_TEMPLATES_NAMES[tmp_name][1]
				challenges_used.append(indexed)
				challenge_template = CHALLENGES_TEMPLATES[indexed]
				chal_obj = {
					'id':challenge.id, 'name': tmp_name, 'category': challenge.category.name,
					'full_description': challenge.description, 'description': challenge_template['description'],
					'sn': challenge_template['sn'], 'edit': True, 'flag': challenge.flag,
					'can_have_files':challenge_template['files'], 'variety':challenge_template['variety']
					}
				if variety is not None:
					if varieties_used.get(indexed):
						varieties_used[indexed].append(variety)
					else:
						varieties_used[indexed]=[variety]
					chal_obj['variety'] = variety
					all_challenges.append(chal_obj)
				else:
					challenges_used.append(indexed)
					base_challenges.append(chal_obj)
					if challenge_template['files']:

						files = challenge.files.all()
						chal_obj['files'] = [jsonify_queryset(files)] if files.count() == 1 else jsonify_queryset(files)
					all_challenges.append(chal_obj)
				challenges_used.append(indexed)


		for i,challenge in enumerate(CHALLENGES_TEMPLATES):
			if challenge['variety']:
				if i in challenges_used:
					if varieties_used.get(i):
						if len(varieties_used[i]) == 2:
							challenge['edit'] = True
					base_challenges.append(challenge)
					all_challenges.append(challenge)
				else:
					challenge['edit'] = False
					base_challenges.append(challenge)
					all_challenges.append(challenge)
			elif i not in challenges_used:
				base_challenges.append(challenge)
				all_challenges.append(challenge)
		new_chals = sorted(base_challenges,key=itemgetter('category','sn','name'))
		return render(request,"challenge_admin.html", {"challenges":new_chals,
		                                               'json':json_encode(all_challenges)})




@login_required(login_url="login")
@user_tfa_valid
def solves_admin(request):
	if not request.user.is_staff or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('index'))
	elif not request.user.tfa_enabled:
		return HttpResponseRedirect(reverse('two_factor'))
	all_challenges = Challenges.objects.order_by('category__name').values('id','name','category__name','num_solves')
	all_challenges = jsonify_queryset(all_challenges)
	#return JsonResponse(all_challenges,safe=False)
	return render(request,"solves_admin.html",{"challenges":all_challenges})


@login_required(login_url="login")
@user_tfa_valid
def get_all_solves(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404()

	all_solves = Solves.objects.order_by('challenge__category__name').values('user__username', 'challenge__name', 'challenge__category__name', 'timestamp')
	all_solves = jsonify_queryset(all_solves)
	solve_dict = {}

	if type(all_solves) is dict:
		solve_dict[all_solves.get('challenge__category__name')] = [all_solves]
	elif len(all_solves) > 1:
		for isolve in all_solves:
			if solve_dict.get(isolve['challenge__category__name']):
				solve_dict[isolve['challenge__category__name']].append(isolve)
			else:
				solve_dict[isolve['challenge__category__name']] = [isolve]
	else:
		pass

	return JsonResponse({'error':solve_dict})


@login_required(login_url="login")
@require_http_methods(["POST","GET"])
def hint_admin(request, challenge_identifier):
	if not (request.user.is_staff or request.user.is_superuser):
		return JsonResponse({'OK':False})
	elif not request.user.tfa_enabled:
		return JsonResponse({'OK':False})

	try:
		challenge_identifier = int(challenge_identifier)
		challenge_id = Challenges.objects.filter(pk=challenge_identifier).values("id").first()['id']
	except ValueError:
		challenge_id = Challenges.objects.filter(name=challenge_identifier).values("id").first()['id']

	if challenge_id is None:
			return JsonResponse({"OK":False})
	if request.method == "POST":
		content = json_decode(request.body)
		if content['id'] == 0:
			new_hint = Hints.objects.create(
				description=content['description'],
				level=content['level'],
				challenge_id = challenge_id
			)
			new_hint.save()
			return JsonResponse({'OK':True})
		else:
			edit_hint = Hints.objects.filter(pk=content['id']).first()
			if edit_hint is not None:
				edit_hint.description = content['description']
				edit_hint.level = content['level']
				edit_hint.save()
				return JsonResponse({'OK':True})
			else:
				return JsonResponse({"OK":False})
	else:
		challenge_hints = Hints.objects.filter(challenge_id = challenge_identifier)
		num_hints = challenge_hints.count()
		challenge_hints = jsonify_queryset(challenge_hints)
	return JsonResponse({'hints':challenge_hints,'len':num_hints})


@login_required(login_url="login")
@user_tfa_valid
def admin_view(request):
	if not (request.user.is_staff or request.user.is_superuser):
		return JsonResponse({'OK':False})
	elif not request.user.tfa_enabled:
		return JsonResponse({'OK':False})

	was_limited = getattr(request, 'limited', False)
	return render(request,"solves_admin.html",{'solves:solves'})


@require_http_methods(["GET"])
def high_scores(request):
	#only show users who have done something.
	top_users = User.objects.values('points', 'username', 'id').filter(points__gt=0).order_by('-points', 'username')[:25]
	#top_users = User.objects.values('points','username','id').order_by('-points', 'username')[:25]
	user_ranks = rank_users(top_users)

	return JsonResponse(user_ranks,safe=False)

@require_http_methods(["GET"])
def leaderboard(request):
	#Only show users who have actually done something.
	top_users = User.objects.values('points', 'username', 'id').filter(points__gt=0).order_by('-points', 'username')[:25]
	#top_users = User.objects.values('points','username','id').order_by('-points', 'username')[:25]
	user_ranks = rank_users(top_users)

	return render(request,"leaderboard.html",{"ranks":user_ranks})


@ratelimit(key='ip',rate='30/m',method=UNSAFE)
@require_http_methods(("GET","POST"))
def captcha(request):
	captcha_msg = ''
	error = False
	ratelimited = False
	msg = ''
	if request.method == "POST":
		if is_ratelimited(request):
			ratelimited = True
		else:
			captcha_expires = request.session.get('captcha_expires', False)
			if captcha_expires:
				captcha_expires = timezone.datetime.utcfromtimestamp(captcha_expires)

				if captcha_expires < timezone.datetime.utcnow():
					msg = "Captcha expired."
					error = True
					if request.session['captcha_valid']:
						request.session['captcha_valid'] = False
				else:

					if request.is_ajax():
						body = json_decode(request.body)
						usr_ans = body['captcha_ans']
						letters_ans = body['letters']
					else:
						usr_ans = request.POST.get('captcha_ans')
						letters_ans = request.POST.get('letters')

					check_captchas(request,letters_ans,usr_ans)



	else:
		request.session['captcha_valid'] = False

	color_name = ''
	img_str = ''
	if not request.session['captcha_valid'] and not error:

		msg = "Invalid Captcha"
		error = True
	elif not error:
		msg = "Captcha Solved"
		error = False

	if error:
		captcha_msg, color_name, img_str = generate_captchas(request)

	return JsonResponse({"msg":msg,"ratelimited":ratelimited,"error":error,"captcha_msg":captcha_msg,"color_name":color_name,"img_str":img_str})


@login_required(login_url="login")
def file(request,filename):
	import os.path
	path = os.path.normpath(os.path.join('file',filename))
	if not path.startswith('file'):
		return HttpResponse(reason='Malformed filename.',status=403)
	if os.path.exists(path) and os.path.isfile(path):
		return FileResponse(path)
	else:
		return HttpResponse(reason="File doesn't exist.",status=404)


# TFA related views.
@login_required(login_url='login')
@require_http_methods("GET")
def tfa_qr_code(request):
	domain = request.get_host()
	if not domain:
		domain = 'example.com'
	username = f"{request.user.username}@{domain}"
	new_totp = TotpAuthorize(request.user.tfa_secret)
	request.session['totp_secret'] = new_totp.secret

	qrcode = new_totp.qrcode(username)
	response = HttpResponse(content_type="image/png")
	qrcode.save(response,"PNG")
	return response


@login_required(login_url='login')
@require_http_methods(("GET","POST"))
def tfa_enable(request):
	if request.method == "GET":
		has_tfa_enabled = request.user.tfa_enabled
		return render(request,"two_factor.html",{"enabled":has_tfa_enabled})
	else:
		if request.is_ajax():
			token = json_decode(request.body).get('token')
		else:
			token = request.POST.get('token')

		new_totp = TotpAuthorize(request.session['totp_secret'])
		if token and new_totp.valid(token):
			request.user.tfa_secret = request.session['totp_secret']
			request.user.tfa_enabled = True
			request.user.save()
			enabled = True
			error = ""
		else:
			enabled = False
			error = "The token you provided didn't work. Refresh the page and try again."
		if request.is_ajax():
			return JsonResponse({"enabled":enabled,"error":error})
		else:
			return render(request,"two_factor.html",{"enabled":enabled,error:error})


@login_required()
@require_http_methods(("GET","POST"))
def verify_tfa(request):
	if request.method == "GET":

		if request.session.get('verified_tfa',False):
			return HttpResponseRedirect(reverse("index"))
		else:
			return render(request,"verify_tfa.html")
	else:
		if request.headers['Content-Type'] == 'application/json':
			token = json_decode(request.body).get('token')
		else:
			token = request.POST.get('token')

		totp_authorizer = TotpAuthorize(request.user.tfa_secret)
		if totp_authorizer.valid(token):
			request.session['verified_tfa'] = True
			if request.headers['Content-Type'] == 'application/json':
				return JsonResponse({'token_invalid':False})
			else:
				from django.utils.http import url_has_allowed_host_and_scheme
				nxt = request.POST.get("next_url")
				if nxt and url_has_allowed_host_and_scheme(url=nxt,allowed_hosts={request.get_host()},require_https=request.is_secure()):
					return HttpResponseRedirect(nxt)
				else:
					return HttpResponseRedirect(reverse("index"))
		else:
			return render(request,"verify_tfa.html",{"token_invalid":True})


def about(request):
	return render(request,"about.html")


@login_required()
@require_http_methods("GET")
@user_tfa_valid
def admin_leaderboard(request):
	if not (request.user.is_staff or request.user.is_superuser):
		return HttpResponseRedirect(reverse('index'))

	top_users = User.objects.values('points','username','id').order_by('-points', 'username')
	user_ranks = rank_users(top_users)

	return render(request,"admin_leaderboard.html",{"ranks":user_ranks})


def top_secret_test(request):
	if request.method == "GET":
		return render(request,"prog_challenge.html")
	else:
		import requests
		from json import loads
		if request.is_ajax():
			data = json_decode(request.body)
			solution = """
			"""
			good_code = """
import sys



def fizzbuzz(n):
	sum15 = 0
	sum5 = 0
	sum3 = 0
	for i in range(1,n+1):
		if i % 15 == 0:
			sum15 +=1
			sum5 += 1
			sum3 += 1
		elif i % 5 == 0:
			sum5 += 1
		elif i % 3 == 0:
			sum3 += 1

	return sum3,sum5,sum15

results = []
for test in map(int, sys.argv[1:]):
	print(fizzbuzz(test))
	

"""

			req_data = {'language':'py3','version':'3.10.0','stdin':'','args':[1,10,20,30], 'files':[{'name':'main.py','content':good_code}]}

			r = requests.post('https://emkc.org/api/v2/piston/execute', json=req_data)
			run  = r.json()
			print(run)
			solutions = run['run']['output']
			if data['language'] == 0:
				req_data['language'] = 'py3'
				req_data['version'] = '3.10.0'
			else:
				req_data['language'] = 'javascript'
				req_data['version'] = '16.3.0'
				req_data['files'][0]['name'] = 'main.js'

			req_data['files'][0]['content'] = data['code']

			r = requests.post('https://emkc.org/api/v2/piston/execute', json=req_data)
			run  = r.json()
			print(run)
			user_answers = run['run']['output']
			if run['run']['stderr'] != '' or run['run']['code'] != 0:
				return JsonResponse({'score':0,'errors':run['run']['stderr']})
			else:
				total = 0
				total_c = 0
				for solution,user_answer in solutions,user_answers:
					total += 1
					if solution == user_answer:
						total_c += 1


				return JsonResponse({'score':total_c/total})

@login_required(login_url='login')
@require_http_methods(("GET","POST"))
@user_tfa_valid
def programming_admin(request):
	return render(request,'prog_challenge.html')

@login_required(login_url='login')
@require_http_methods(("GET","POST"))
@user_tfa_valid
def top_secret(request):
	return render(request,'top_secret.html')
