import datetime
from django.db import models
from locksmith.common import KEY_STATUSES

class ApiKey(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    email = models.EmailField('Email Address')
    status = models.CharField(max_length=1, choices=KEY_STATUSES, default='U')

    issued_on = models.DateTimeField(default=datetime.datetime.now, editable=False)

    def active(self):
        return status == 'A'

    def __unicode__(self):
        return '%s (%s) [%s]' % (self.email, self.key, self.get_status_display())

    class Meta:
        db_table = 'locksmith_auth_apikey'
