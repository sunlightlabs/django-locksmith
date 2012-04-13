import datetime
from django.db import models
from django.db.models.signals import post_save
from django.forms import Form, ModelForm, ValidationError, BooleanField, EmailField
from locksmith.common import (KEY_STATUSES, PUB_STATUSES, UNPUBLISHED,
                              NEEDS_UPDATE, PUBLISHED)
from locksmith.hub.tasks import push_key

class Api(models.Model):
    '''
        API that Keys are issued to and Reports come from
    '''
    name = models.CharField(max_length=30)
    signing_key = models.CharField(max_length=32)
    url = models.URLField(verify_exists=False)
    push_enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'locksmith_hub_api'

class Key(models.Model):
    '''
        API key to be handed out to Apis
    '''
    key = models.CharField(max_length=32)
    email = models.EmailField()
    status = models.CharField(max_length=1, choices=KEY_STATUSES, default='U')

    name = models.CharField('Name', max_length=100, blank=True)
    org_name = models.CharField('Organization Name', max_length=100, blank=True)
    org_url = models.CharField('Organization URL', blank=True, max_length=200)
    usage = models.TextField('Intended Usage', blank=True)

    issued_on = models.DateTimeField(default=datetime.datetime.now, editable=False)

    def __unicode__(self):
        return '%s %s [%s]' % (self.key, self.email, self.status)

    def mark_for_update(self):
        '''
            Note that a change has been made so all Statuses need update
        '''
        self.pub_statuses.exclude(status=UNPUBLISHED).update(status=NEEDS_UPDATE)
        push_key.delay(self)

    class Meta:
        db_table = 'locksmith_hub_key'

class KeyPublicationStatus(models.Model):
    '''
        Status of Key with respect to an API
    '''
    key = models.ForeignKey(Key, related_name='pub_statuses')
    api = models.ForeignKey(Api, related_name='pub_statuses')
    status = models.IntegerField(default=UNPUBLISHED, choices=PUB_STATUSES)

    class Meta:
        db_table = 'locksmith_hub_keypublicationstatus'

class Report(models.Model):
    '''
        Daily Analytics Report
    '''
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

# Key registration form

class KeyForm(ModelForm):
    class Meta:
        model = Key
        exclude = ('key', 'issued_on', 'status', 'pub_status')

    terms_of_service = BooleanField(required=False)

    def clean_email(self):
        if Key.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError('Email address already registered')
        return self.cleaned_data['email']

    def clean(self):
        if not self.cleaned_data['terms_of_service']:
            raise ValidationError('Please read and agree to the Terms of Service')
        return self.cleaned_data

class ResendForm(Form):
    email = EmailField()
