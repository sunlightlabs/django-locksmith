import datetime
from django.db import models
from django import forms
from django.contrib.auth.models import User
from locksmith.common import KEY_STATUSES
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

    class Meta:
        db_table = 'locksmith_hub_key'

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
