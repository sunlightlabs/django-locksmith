import datetime
from django.db import models
from locksmith.common import KEY_STATUSES

UNPUBLISHED, PUBLISHED, NEEDS_UPDATE = range(3)
PUB_STATUSES = (
    (UNPUBLISHED, 'Unpublished'),
    (PUBLISHED, 'Published'),
    (NEEDS_UPDATE, 'Needs Update'),
)

class Key(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    email = models.EmailField('Email Address')
    status = models.CharField(max_length=1, choices=KEY_STATUSES, default='U')

    issued_on = models.DateTimeField(default=datetime.datetime.now, editable=False)
    pub_status = models.IntegerField(default=UNPUBLISHED, choices=PUB_STATUSES)

    def active(self):
        return status == 'A'

    def mark_for_update(self):
        if self.pub_status != UNPUBLISHED:
            self.pub_status = NEEDS_UPDATE

    def __unicode__(self):
        return '%s (%s) [%s]' % (self.email, self.key, self.get_status_display())

    class Meta:
        db_table = 'locksmith_auth_key'
