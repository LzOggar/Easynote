from django import forms
from django.contrib.auth.models import User

from Easynote.models import Notes
from Easynote.lib import const

class AuthenticationForm(forms.Form):
	"""
		AuthenticationForm class. Inherit from Form class.
		:fields username: User username. Must be a str.
		:fields password: User password. Must be a str.
	"""

	username = forms.CharField(max_length=const.AUTH["username"], widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Username"}))
	password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}))

class RegisterForm(forms.ModelForm):
	"""
		RegisterForm class. Inherit from Form class.
		:fields username: User username. Must be a str.
		:fields password1: User password. Must be a str.
		:fields password2: User password. Must be a str.
	"""

	username = forms.CharField(max_length=const.AUTH["username"], widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Username"}))
	password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}))
	confirm_password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Confirm password"}))

	class Meta:
		"""
			Meta class. Called save() to register new entry in User table.
		"""

		model = User
		fields = ("username", "password", "confirm_password")

class NewNoteForm(forms.ModelForm):
	"""
		NewNoteForm class. Inherit from ModelForm.
		:fields name: Notes name. Must be a str.
		:fields summary: Notes summary. Must be a str.
	"""

	name = forms.CharField(max_length=const.NOTES["name"], widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Name"}))
	summary = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "cols":"80", "rows":"10", "placeholder":"Type your text here"}))

	class Meta:
		"""
			Meta class. Called save() to register new entry in User table.
		"""

		model = Notes
		fields = ("name", "summary")

class EditNoteForm(forms.Form):
	"""
		EditNoteForm class. Inherit from Form.
		:fields name: Notes name. Must be a str.
		:fields summary: Notes summary. Must be a str.
	"""

	name = forms.CharField(max_length=const.NOTES["name"], widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Name", "readonly":"" }))
	summary = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "cols":"80", "rows":"10", "placeholder":"Type your text here"}))

class ChangePasswordForm(forms.Form):
	"""
		ChangePasswordForm class. Inherit from Form.
		:fields current_password: Must be a str.
		:fields new_password: Must be a str.
		:fields confirm_password: Must be a str.
	"""

	username = forms.CharField(max_length=const.AUTH["username"], widget=forms.TextInput(attrs={"hidden":""}))
	current_password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Current password"}))
	new_password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"New password"}))
	confirm_password = forms.CharField(max_length=const.AUTH["password"], widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Confirm password"}))
