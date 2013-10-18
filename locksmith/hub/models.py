import datetime
from django.db import models
from django.db.models.signals import post_save
from django import forms
#from django.forms import Form, ModelForm, ValidationError, BooleanField, EmailField
from django.contrib.auth.models import User
from locksmith.common import (KEY_STATUSES,
                              PUB_STATUSES,
                              UNPUBLISHED,
                              NEEDS_UPDATE,
                              API_OPERATING_STATUSES,
                              API_STATUSES)
from locksmith.hub.tasks import push_key
from taggit.managers import TaggableManager
    
def resolve_model(model, fields):
    """
    model: Model class
    fields: List of 2-tuples of the form (field, value) in order of descending priority
    """
    for (f, v) in fields:
        if v is not None:
            try:
                kwargs = {f: v}
                obj = model.objects.get(**kwargs)
                return obj
            except model.DoesNotExist:
                pass
            except model.MultipleObjectsReturned:
                pass
    raise model.DoesNotExist()

class Api(models.Model):
    '''
        API that Keys are issued to and Reports come from
    '''
    name = models.CharField(max_length=30)
    signing_key = models.CharField(max_length=32)
    url = models.URLField()
    push_enabled = models.BooleanField(default=True)
    description = models.TextField('Description', blank=True)
    status = models.IntegerField(choices=API_OPERATING_STATUSES, default=1)
    mode = models.IntegerField(choices=list(API_STATUSES), default=1)
    status_message = models.TextField('A more detailed status message', null=True, blank=True)
    display_name = models.TextField('Display name of the API', blank=False, null=True)
    documentation_link = models.TextField('Link to this API\'s documentation', null=True, blank=True)
    tools_text = models.TextField('Tools this API powers', null=True, blank=True)
    tags = TaggableManager(blank=True)
    querybuilder_link = models.TextField('Link to this API\'s query builder page', null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'locksmith_hub_api'

class Key(models.Model):
    '''
        API key to be handed out to Apis
    '''
    user = models.OneToOneField(User, null=True, blank=True, related_name='api_key')

    key = models.CharField(max_length=32, db_index=True)
    email = models.EmailField(unique=True)
    alternate_email = models.EmailField(blank=True, null=True) #
    status = models.CharField(max_length=1, choices=KEY_STATUSES, default='U')

    name = models.CharField('Name', max_length=100, blank=True, null=True,
                            db_index=True)
    org_name = models.CharField('Organization Name', max_length=100,
                                blank=True, null=True, db_index=True)
    org_url = models.CharField('Organization URL', blank=True, null=True,
                               max_length=200, db_index=True)
    usage = models.TextField('Intended Usage', blank=True, null=True)

    promotable = models.BooleanField(default=False)
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

    def __unicode__(self):
        return u'api={0!r} key={1!r} status={2}'.format(self.api.name,
                                                        self.key.key,
                                                        self.status)

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

def kps_callback(sender, instance, created, raw, **kwargs):
    ''' create KeyPublicationStatus object for Keys/Apis '''
    if created and not raw:
        if sender == Api:
            for key in Key.objects.all():
                KeyPublicationStatus.objects.create(key=key, api=instance)
        elif isinstance(instance, Key):
            for api in Api.objects.all():
                KeyPublicationStatus.objects.create(key=instance, api=api)
post_save.connect(kps_callback, sender=Api)
post_save.connect(kps_callback, sender=Key)

# Key registration form

class KeyForm(forms.ModelForm):
    class Meta:
        model = Key
        exclude = ('key', 'issued_on', 'status', 'pub_status', 'user')
    
    terms_of_service = forms.BooleanField(required=False)
#    user = forms.CharField(widget=forms.HiddenInput())

    def clean_email(self):
        if Key.objects.filter(email=self.cleaned_data['email']).count():
            raise forms.ValidationError('Email address already registered')
        return self.cleaned_data['email']

    def clean(self):
        if not self.cleaned_data['terms_of_service']:
            raise forms.ValidationError('Please read and agree to the Terms of Service')
        return self.cleaned_data

class ResendForm(forms.Form):
    email = forms.EmailField()
