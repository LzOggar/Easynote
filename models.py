from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Easynote.lib import const

# Create your models here.
class Profiles(models.Model):
	"""
		Profiles models.
		:field salt: Must be <str>
		:field user: Muste be <User>
	"""

	salt = models.CharField(max_length=const.PROFILES["salt"])
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Notes(models.Model):
	"""
		Notes models.
		:field name: Must be <str>
		:field summary: Must be <str>
		:field publish_date: Must be <datetime>
		:field update_date: Must be <datetime>
		:field changes: Must be <integer>
		:field views: Must be <integer>
		:field user: Muste be <User>
	"""

	name = models.CharField(max_length=const.NOTES["name"])
	summary = models.TextField()
	published_date = models.DateTimeField()
	updated_date = models.DateTimeField()
	changes = models.IntegerField()
	views = models.IntegerField()
	exports = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def as_dict(self):
		"""
			Translate Notes table into a dictionary struct.
			:param self: Notes instance. Must be Notes object.
			:return: dictionary of Notes table from Notes instance.
			:rtype: <dict>.
		"""

		return {
			"name":self.name,
			"published_date":timezone.datetime.strftime(self.published_date, format="%b. %d, %Y, %H:%m %p."),
			"updated_date":timezone.datetime.strftime(self.updated_date, format="%b. %d, %Y, %H:%m %p."),
			"changes":self.changes,
			"views":self.views,
			"exports":self.exports,
			"user":self.user.username
		}

class Keys(models.Model):
	"""
		Keys models.
		:field key: Must be <str>
		:field note: Must be <Notes>
	"""

	key = models.CharField(max_length=const.KEYS["key"])
	note = models.ForeignKey(Notes, on_delete=models.CASCADE)
