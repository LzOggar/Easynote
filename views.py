from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone, crypto
from django.core.paginator import Paginator
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa
from functools import reduce

from Easynote import forms, models
from Easynote.lib import const, aes

import binascii, bleach, io, json

# Create your views here.

@require_http_methods("GET")
def index(request):
	"""
		index view. Handle index call GET then return to login page.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	return HttpResponseRedirect(reverse("login", args=()))

@require_http_methods(["GET","POST"])
def login(request):
	"""
		login view. Handle login user.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	# check whether user is already logged
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("dashboard", args=()))

	# GET call
	if request.method == "GET":
		context = { "form" : forms.AuthenticationForm() }
	else:
		# POST call
		form = forms.AuthenticationForm(data=request.POST)

		if form.is_valid():
			username = form.cleaned_data["username"]
			password = form.cleaned_data["password"]

			user = authenticate(request, username=username, password=password)
			if user is None:
				context = { "form" : form }
				messages.error(request, "Invalid username or password.", extra_tags="login")
			else:
				profile = models.Profiles.objects.get(user=User.objects.get(username=username))
				master_key = crypto.hashlib.pbkdf2_hmac("sha256", password.encode(), profile.salt.encode(), 100000)
				request.session["master_key"] = master_key.hex()

				auth_login(request, user)
				return HttpResponseRedirect(reverse("dashboard", args=()))
		else:
			context = { "form" : form }

			# form errors
			# errors displayed in form
			for k,v in form.errors.items():
				messages.error(request, v.data[0].message, extra_tags=k)

	return render(request, "registration/login.html", context)

@login_required
@require_http_methods("GET")
def logout(request):
	"""
		logout view. Handle logout user.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	request.session["master_key"] = ""

	auth_logout(request)
	return HttpResponseRedirect(reverse("login", args=()))

@require_http_methods(["GET","POST"])
def register(request):
	"""
		register view. Handle register user.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	# check whether user is already logged
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("dashboard", args=()))

	# GET call
	if request.method == "GET":
		context = { "form" : forms.RegisterForm() }
	else:
		# POST call
		form = forms.RegisterForm(data=request.POST)

		if form.is_valid():
			username = bleach.clean(form.cleaned_data["username"], tags=[], strip=True)
			password = bleach.clean(form.cleaned_data["password"], tags=[], strip=True)
			confirm_password = bleach.clean(form.cleaned_data["confirm_password"], tags=[], strip=True)

			if password == confirm_password:
				users = User.objects.filter(username=username)
				if users.exists():
					# do not view error message for security
					context = { "form" : form }
				else:
					user = form.save(commit=False)
					user.set_password(password)
					user.save()

					salt = crypto.get_random_string(const.PROFILES["salt"])
					profile = models.Profiles.objects.create(salt=salt, user=User.objects.get(username=username))

					# auto login after create the user
					auth_login(request, user)
					master_key = crypto.hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
					request.session["master_key"] = master_key.hex()

					return HttpResponseRedirect(reverse("dashboard", args=()))
			else:
				messages.error(request, "Password does not match.", extra_tags="register")
				context = { "form" : form }
		else:
			context = { "form" : form }
			# form errors
			# errors displayed in form
			for k,v in form.errors.items():
				if k != "username":
					messages.error(request, v.data[0].message, extra_tags=k)

	return render(request, "registration/register.html", context)

@require_http_methods("GET")
def about(request):
	"""
		about view. Handle about page call GET.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	return render(request, "about.html", {})

@login_required
@require_http_methods("GET")
def dashboard(request):
	"""
		dashboard views. Handle dashboard page call GET.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	return render(request, "dashboard.html", {})

@login_required
@require_http_methods("GET")
def view_available_notes(request):
	"""
		view_available_notes views. Show all available notes for the user.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	# GET method
	# paginator builds pagination and handle get parameter ?page=
	# return current notes for current page with paginator.get_page
	queryset = models.Notes.objects.filter(user=User.objects.get(username=request.user.username)).order_by("name")
	paginator = Paginator(queryset, const.NOTES["items_per_page"])
	page = request.GET.get("page")
	notes = paginator.get_page(page)
	context = { "notes":notes }

	return render(request, "notes/notes.html", context)

@login_required
@require_http_methods(["GET","POST"])
def create_new_note(request):
	"""
		create_new_note views. Create new <Notes> entry into database from form input then redirect to notes/ page.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	if request.method == "GET":
		# GET call
		# create Note form
		context = { "form":forms.NewNoteForm() }
	else:
		# POST call
		# create Note form with POST inputs
		form = forms.NewNoteForm(data=request.POST)
		if form.is_valid():
			name = bleach.clean(form.cleaned_data["name"], tags=[], strip=True)
			summary = bleach.clean(form.cleaned_data["summary"], tags=const.BLEACH["AUTHORIZED_TAGS"], 
								   attributes=const.BLEACH["AUTHORIZED_ATTRIBUTES"], styles=const.BLEACH["AUTHORIZED_STYLES"], 
								   strip=True)

			notes = models.Notes.objects.filter(name=name, user=User.objects.get(username=request.user.username))
			if notes.exists():
				# add error message in request
				# tag : notes
				# errors displayed with topper.js
				messages.error(request, "A note with this name already in use.", extra_tags="notes")
			elif len(name) > 0 and len(summary) > 0:
				# generate random symetric key
				# encrypt summary with random symetric key
				key = crypto.get_random_string(const.KEYS["key"])
				algorithm = aes.AdvancedEncryptionStandard(key.encode())
				ciphersummary = algorithm.encrypt(summary.encode())

				# create note entry in database
				note = form.save(commit=False)
				note.name = name
				note.summary = ciphersummary.hex()
				note.published_date = timezone.now()
				note.updated_date = timezone.now()
				note.changes = 0
				note.views = 0
				note.exports = 0
				note.user = User.objects.get(username=request.user.username)
				note.save()

				# encrypt symetric key with master_key
				master_key = binascii.unhexlify(request.session["master_key"])
				algorithm = aes.AdvancedEncryptionStandard(master_key)
				cipherkey = algorithm.encrypt(key.encode())

				# create key entry
				models.Keys.objects.create(key=cipherkey.hex(), note=note)

				return HttpResponseRedirect(reverse("view_available_notes", args=()))
			else:
				# add error message in request
				# tag : notes
				# errors displayed with topper.js
				messages.error(request, "NAME or SUMMARY field is empty.", extra_tags="notes")
		else:
			# form errors
			# errors displayed in form
			for k,v in form.errors.items():
				messages.error(request, v.data[0].message, extra_tags=k)

		context = { "form":form }

	return render(request, "notes/new-note.html", context)

@login_required
@require_http_methods(["GET","POST"])
def edit_current_note(request, name):
	"""
		edit_current_note views. Edit current <Notes> entry then update the <Notes> entry fromform input.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	if request.method == "GET":
		# GET call
		try:
			# recover encrypted symetric key
			# convert string to hexadecimal
			note = models.Notes.objects.get(name=name, user=User.objects.get(username=request.user.username))
			key = models.Keys.objects.get(note=note)
			cipherkey = binascii.unhexlify(key.key)

			# decrypt key with master key
			master_key = binascii.unhexlify(request.session["master_key"])
			algorithm = aes.AdvancedEncryptionStandard(master_key)
			plaintext_key = algorithm.decrypt(cipherkey)

			# convert string to hexadecimal
			# decrypt summary with symetric key
			algorithm = aes.AdvancedEncryptionStandard(plaintext_key)
			ciphersummary = binascii.unhexlify(note.summary)
			summary = algorithm.decrypt(ciphersummary)

			data = { "name":note.name, "summary":summary.decode() }
			form = forms.EditNoteForm(initial=data)

			context = { "note":note, "form":form }
			return render(request, "notes/edit-note.html", context)
		except models.Notes.DoesNotExist as err:
			# appear whether note does not exist
			# add error message in request
			# tag : notes
			# errors displayed with topper.js
			messages.error(request, err, extra_tags="notes")
			return HttpResponseRedirect(reverse("view_available_notes",args=()))
	else:
		# POST call
		form = forms.EditNoteForm(data=request.POST)
		if form.is_valid():
			summary = bleach.clean(form.cleaned_data["summary"], tags=const.BLEACH["AUTHORIZED_TAGS"], 
								   attributes=const.BLEACH["AUTHORIZED_ATTRIBUTES"], styles=const.BLEACH["AUTHORIZED_STYLES"], 
								   strip=True)

			if len(summary) > 0:
				try:
					# recover encrypted symetric key
					# convert string to hexadecimal
					note = models.Notes.objects.get(name=name, user=User.objects.get(username=request.user.username))
					key = models.Keys.objects.get(note=note)
					cipherkey = binascii.unhexlify(key.key)

					# decrypt key with master key
					master_key = binascii.unhexlify(request.session["master_key"])
					algorithm = aes.AdvancedEncryptionStandard(master_key)
					plaintext_key = algorithm.decrypt(cipherkey)

					# convert string to hexadecimal
					# decrypt summary with symetric key
					algorithm = aes.AdvancedEncryptionStandard(plaintext_key)
					ciphersummary = algorithm.encrypt(summary.encode())
					
					note.summary = ciphersummary.hex()
					note.updated_date = timezone.now()
					note.changes = note.changes + 1
					note.save()

				except models.Notes.DoesNotExist as err:
					# appear whether note does not exist
					# add error message in request
					# tag : notes
					# errors displayed with topper.js
					messages.error(request, err, extra_tags="notes")
					return HttpResponseRedirect(reverse("view_available_notes", args=()))
			else:
				# appear whether note does not exist
				# add error message in request
				# tag : notes
				# errors displayed with topper.js
				messages.error(request, "SUMMARY field is empty.", extra_tags="notes")
		else:
			# form errors
			# errors displayed in form
			for k,v in form.errors.items():
				messages.error(request, v.data[0].message, extra_tags=k)

		return HttpResponseRedirect(reverse("edit_current_note", args=(name,)))

@login_required
@require_http_methods("GET")
def view_current_note(request, name):
	"""
		view_current_note views. Handle notes/view/ call GET.
		:param request: Must be <HttpRequest>
		:return:  <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	try:
		# recover encrypted symetric key
		# convert string to hexadecimal
		note = models.Notes.objects.get(name=name, user=User.objects.get(username=request.user.username))
		key = models.Keys.objects.get(note=note)
		cipherkey = binascii.unhexlify(key.key)

		# decrypt key with master key
		master_key = binascii.unhexlify(request.session["master_key"])
		algorithm = aes.AdvancedEncryptionStandard(master_key)
		plaintext_key = algorithm.decrypt(cipherkey)

		# convert string to hexadecimal
		# decrypt summary with symetric key
		algorithm = aes.AdvancedEncryptionStandard(plaintext_key)
		ciphersummary = binascii.unhexlify(note.summary)
		summary = algorithm.decrypt(ciphersummary)

		# update note stats
		note.views = note.views + 1
		note.save()

		context = { "note":note, "summary":summary.decode() }
		return render(request, "notes/view-note.html", context)
	except models.Notes.DoesNotExist as err:
		# appear whether note does not exist
		# add error message in request
		# tag : notes
		# errors displayed with topper.js
		messages.error(request, err, extra_tags="notes")
		return HttpResponseRedirect(reverse("view_available_notes",args=()))


@login_required
@require_http_methods("POST")
def delete_current_note(request):
	"""
		delete_current_note views. Handle notes/delete/ page call POST. Delete the note passed in POST form for the user.
		:param request: Must be <HttpRequest>
		:return: <HttpResponse> instance
		:rtype: <HttpResponse>
	"""

	try:
		name = request.POST["name"]
		note = models.Notes.objects.get(name=name, user=User.objects.get(username=request.user.username))
		note.delete()
	except models.Notes.DoesNotExist as err:
		# appear whether note does not exist
		# add error message in request
		# tag : notes
		# errors displayed with topper.js
		messages.error(request, err, extra_tags="notes")
	except KeyError as err:
		# appear whether name field is not in request
		# add error message in request
		# tag : notes
		# errors displayed with topper.js
		messages.error(request, "NAME field is mandatory.", extra_tags="notes")

	return HttpResponseRedirect(reverse("view_available_notes", args=()))

@login_required
@require_http_methods("GET")
def export_current_note(request, name):
	"""
		export_current_note views. Handle notes/export/ page call GET. Export the note as PDF file.
		:param request: Must be <HttpRequest>
		:return: PDF file.
		:rtype: <HttpResponse>
	"""

	def render_to_pdf(template, context):
		"""
			render_to_pdf. 
			:param request: Must be <HttpRequest>
			:return: PDF file.
			:rtype: <HttpResponse>
		"""

		template = get_template(template)
		html = template.render(context)

		result = io.BytesIO()
		pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)

		if pdf.err:
			return None
		else:
			return result.getvalue()

	try:
		# recover encrypted symetric key
		# convert string to hexadecimal
		note = models.Notes.objects.get(name=name, user=User.objects.get(username=request.user.username))
		key = models.Keys.objects.get(note=note)
		cipherkey = binascii.unhexlify(key.key)

		# decrypt key with master key
		master_key = binascii.unhexlify(request.session["master_key"])
		algorithm = aes.AdvancedEncryptionStandard(master_key)
		plaintext_key = algorithm.decrypt(cipherkey)

		# convert string to hexadecimal
		# decrypt summary with symetric key
		algorithm = aes.AdvancedEncryptionStandard(plaintext_key)
		ciphersummary = binascii.unhexlify(note.summary)
		summary = algorithm.decrypt(ciphersummary)
		context = { "note":note, "summary":summary.decode() }

		result = render_to_pdf("notes/export-note.html", context)

		if result:
			# update note stats
			note.exports = note.exports + 1
			note.save()

			return HttpResponse(result, content_type="application/pdf")
		else:
			messages.error(request, "Unable to generate the PDF file.", extra_tags="notes")
			return HttpResponseRedirect(reverse("view_current_note", args=(name,)))
	except models.Notes.DoesNotExist as err:
		# appear whether note does not exist
		# add error message in request
		# tag : notes
		# errors displayed with topper.js
		messages.error(request, err, extra_tags="notes")
		return HttpResponseRedirect(reverse("view_available_notes", args=()))
	

@login_required
@require_http_methods("GET")
def search_note(request):
	"""
		search_notes view. Get all <Notes> with name contains query.
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: JSONResponse instance.
		:rtype: JSONResponse class.
	"""

	if request.is_ajax():
		try:
			query = request.GET["query"]
			# check whether query is not empty
			if len(query) > 0:
				notes = models.Notes.objects.filter(name__contains=query, user=User.objects.get(username=request.user.username)).order_by("name")
			else:
				notes = models.Notes.objects.filter(user=User.objects.get(username=request.user.username)).order_by("name")
			
			notes = [ note.as_dict() for note in notes ]

			context = { "notes" : notes }
			return JsonResponse(context)
		except KeyError:
			# add error message in request
			# tag : notes
			# errors displayed with topper.js
			messages.error(request, "QUERY field is required.", extra_tags="notes")
			
	return HttpResponseRedirect(reverse("view_available_notes",args=()))

@login_required
@require_http_methods("GET")
def view_current_profile(request):
	"""
		view_current_profile view. Display the current user profile. Equaly, handle password change.
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: HttpResponse instance.
		:rtype: HttpResponse class.
	"""

	return render(request, "account/profile.html", {})

@login_required
@require_http_methods("POST")
def change_current_password(request):
	"""
		change_current_password view. Decrypt current keys then encrypt keys with new master key, 
		update current user session and change the user password.
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: HttpResponse instance.
		:rtype: HttpResponse class.
	"""

	try:
		form = forms.ChangePasswordForm(data=request.POST)
		if form.is_valid():
			username = bleach.clean(form.cleaned_data["username"], tags=[], strip=True)
			current_password = bleach.clean(form.cleaned_data["current_password"], tags=[], strip=True)
			new_password = bleach.clean(form.cleaned_data["new_password"], tags=[], strip=True)
			confirm_password = bleach.clean(form.cleaned_data["confirm_password"], tags=[], strip=True)

			if username == request.user.username:
				user = models.User.objects.get(username=request.user.username)
				if user.check_password(current_password):
					if new_password == confirm_password:
						notes = models.Notes.objects.filter(user=user)
						current_master_key = binascii.unhexlify(request.session["master_key"])

						profile = models.Profiles.objects.get(user=user)
						new_master_key = crypto.hashlib.pbkdf2_hmac("sha256", new_password.encode(), profile.salt.encode(), 100000)

						algorithm = aes.AdvancedEncryptionStandard(current_master_key)

						for note in notes:
							key = models.Keys.objects.get(note=note)
							cipherkey = binascii.unhexlify(key.key)

							# decrypt key with master key
							plaintext_key = algorithm.decrypt(cipherkey)
							algorithm = aes.AdvancedEncryptionStandard(new_master_key)

							cipherkey = algorithm.encrypt(plaintext_key)
							key.key = cipherkey.hex() 
							key.save()

						user.set_password(new_password)
						user.save()

						update_session_auth_hash(request, user)
						request.session["master_key"] = new_master_key.hex()
					else:
						messages.error(request, "Password does not match.", extra_tags="profiles")
				else:
					messages.error(request, "Invalid password.", extra_tags="profiles")
			else:
				messages.error(request, "Invalid username.", extra_tags="profiles")
		else:
			# form errors
			# errors displayed in form
			for k,v in form.errors.items():
				messages.error(request, v.data[0].message, extra_tags=k)
	except models.User.DoesNotExist as err:
		messages.error(request, err, extra_tags="profiles")

	return HttpResponseRedirect(reverse("view_current_profile", args=()))
@login_required
@require_http_methods("GET")
def export_all_notes(request):
	"""
		export_all_notes view. Export all notes in json file.
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: HttpResponse instance.
		:rtype: HttpResponse class.
	"""

	notes = models.Notes.objects.filter(user=User.objects.get(username=request.user.username))
	if len(notes) > 0:
		data = {}
		data["notes"] = []
		master_key = binascii.unhexlify(request.session["master_key"])

		for note in notes:
			key = models.Keys.objects.get(note=note)
			cipherkey = binascii.unhexlify(key.key)

			# decrypt key with master keys
			algorithm = aes.AdvancedEncryptionStandard(master_key)
			plaintext_key = algorithm.decrypt(cipherkey)

			# convert string to hexadecimal
			# decrypt summary with symetric key
			algorithm = aes.AdvancedEncryptionStandard(plaintext_key)
			ciphersummary = binascii.unhexlify(note.summary)
			summary = algorithm.decrypt(ciphersummary)

			data["notes"].append({ "name":note.name,
								   "summary":bleach.clean(summary.decode(), tags=[], strip=True), 
								   "published_date":timezone.datetime.strftime(note.published_date, format="%b. %d, %Y, %H:%m %p."),
								   "updated_date":timezone.datetime.strftime(note.updated_date, format="%b. %d, %Y, %H:%m %p."),
								   "author":request.user.username })

		date = timezone.datetime.strftime(timezone.now(), format="%Y_%M_%d_%H_%m_%S")
		filename = "-".join([ request.user.username,"notes",date ])

		response = HttpResponse(json.dumps(data), content_type="application/json")
		response["Content-Disposition"] = "attachment; filename={}.json".format(filename)

		return response
	else:
		# appear whether note does not exist
		# add error message in request
		# tag : profiles
		# errors displayed with topper.js
		messages.error(request, "No notes available." , extra_tags="profiles")
		return HttpResponseRedirect(reverse("view_current_profile", args=()))
	

@login_required
@require_http_methods("POST")
def delete_current_account(request):
	"""
		delete_current_account view. Delete current user account and all related data in database (Profile, Notes, etc.)
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: HttpResponse instance.
		:rtype: HttpResponse class.
	"""

	try:
		username = request.POST["username"]
		if username == request.user.username:
			user = User.objects.get(username=request.user.username)
			user.delete()
			return HttpResponseRedirect(reverse("login", args=()))
	except KeyError as err:
		# appear whether username field is not in request
		# add error message in request
		# tag : profiles
		# errors displayed with topper.js
		messages.error(request, "Username field is mandatory.", extra_tags="profiles")
	else:
		# appear whether username is invalid
		# add error message in request
		# tag : profiles
		# errors displayed with topper.js
		messages.error(request, "Invalid username.", extra_tags="profiles")

	return HttpResponseRedirect(reverse("view_current_profile", args=()))

@login_required
@require_http_methods("GET")
def get_statistics(request):
	"""
		get_statistics view. Get notes statistics (changes, views, exports, etc.)
		:param request: HttpRequest instance. Must be a HttpRequest class.
		:return: JsonResponse instance.
		:rtype: JsonResponse class.
	"""

	if request.is_ajax():
		try:
			months = request.GET["months"]
			notes = models.Notes.objects.filter(user=User.objects.get(username=request.user.username))
			changes, views, exports = 0,0,0

			if len(notes) > 0:
				changes = reduce(lambda x,y: x+y, [ el.changes for el in notes ])
				views = reduce(lambda x,y: x+y, [ el.views for el in notes ])
				exports = reduce(lambda x,y: x+y, [ el.exports for el in notes ])

			if months == "1":
				notes = [ el.as_dict() for el in notes if (timezone.now() - el.published_date).days <= 28 ]
			elif months == "3":
				notes = [ el.as_dict() for el in notes if (timezone.now() - el.published_date).days <= 84 ]
			elif months == "6":
				notes = [ el.as_dict() for el in notes if (timezone.now() - el.published_date).days <= 168 ]
			else:
				notes = [ el.as_dict() for el in notes if (timezone.now() - el.published_date).days <= 336 ]

			context = { "notes_count":len(notes),
						"changes":changes,
						"views":views,
						"exports":exports,
						"notes": notes }

			return JsonResponse(context)
		except KeyError:
			# add error message in request
			# tag : notes
			# errors displayed with topper.js
			messages.error(request, "MONTHS field is required.", extra_tags="statistics")
			
	return HttpResponseRedirect(reverse("dashboard",args=()))
