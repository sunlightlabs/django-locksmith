import datetime
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm, ValidationError
from locksmith.common import KEY_STATUSES

UNPUBLISHED, PUBLISHED, NEEDS_UPDATE = range(3)
PUB_STATUSES = (
    (UNPUBLISHED, 'Unpublished'),
    (PUBLISHED, 'Published'),
    (NEEDS_UPDATE, 'Needs Update'),
)

class Api(models.Model):
    name = models.CharField(max_length=30)
    signing_key = models.CharField(max_length=32)
    url = models.URLField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'locksmith_hub_api'

class Key(models.Model):
    key = models.CharField(max_length=32)
    email = models.EmailField()
    status = models.CharField(max_length=1, choices=KEY_STATUSES, default='U')

    org_name = models.CharField('Organization Name', max_length=100, blank=True)
    org_url = models.URLField('Organization URL', blank=True)
    usage = models.TextField('Intended Usage', blank=True)

    issued_on = models.DateTimeField(default=datetime.datetime.now, editable=False)

    def __unicode__(self):
        return '%s %s [%s]' % (self.key, self.email, self.status)

    def mark_for_update(self):
        self.pub_statuses.exclude(status=UNPUBLISHED).update(status=NEEDS_UPDATE)

    class Meta:
        db_table = 'locksmith_hub_key'

class KeyPublicationStatus(models.Model):
    key = models.ForeignKey(Key, related_name='pub_statuses')
    api = models.ForeignKey(Api, related_name='pub_statuses')
    status = models.IntegerField(default=UNPUBLISHED, choices=PUB_STATUSES)

    class Meta:
        db_table = 'locksmith_hub_keypublicationstatus'

class Report(models.Model):
    date = models.DateField()
    api = models.ForeignKey(Api, related_name='reports')
    key = models.ForeignKey(Key, related_name='reports')
    endpoint = models.CharField(max_length=100)
    calls = models.IntegerField()
    reported_time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'locksmith_hub_report'

def kps_callback(sender, instance, created, **kwargs):
    ''' create KeyPublicationStatus object for Keys/Apis '''
    if created:
        if sender == Api:
            for key in Key.objects.all():
                KeyPublicationStatus.objects.create(key=key, api=instance)
        elif sender == Key:
            for api in Api.objects.all():
                KeyPublicationStatus.objects.create(key=instance, api=api)
post_save.connect(kps_callback, sender=Api)
post_save.connect(kps_callback, sender=Key)

# forms

class KeyForm(ModelForm):
    class Meta:
        model = Key
        exclude = ('key', 'issued_on', 'status', 'pub_status')

    def clean_email(self):
        if Key.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError('Email address already registered')
        return self.cleaned_data['email']
