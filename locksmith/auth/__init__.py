from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.conf import settings
from django.forms import ModelForm
from django.conf.urls.defaults import url
from locksmith.common import ApiAuthBase
from locksmith.auth.models import Key

class ApiAuth(ApiAuthBase):
    key_model = Key
    key_model_form = None

    require_confirmation = False

    registration_email_subject = 'API Registration'
    registration_email_from = settings.DEFAULT_FROM_EMAIL

    registration_email_template = 'locksmith/registration_email.txt'
    registration_template = 'locksmith/register.html'
    registration_complete_template = 'locksmith/registered.html'
    registration_confirmed_template = 'locksmith/confirmed.html'

    def get_key_model_form(self):
        if not self.key_model_form:
            class Form(ModelForm):
                class Meta:
                    model = self.key_model
                    fields = ('email',)
            self.key_model_form = Form
        return self.key_model_form

    def get_urls(self):
        urls = super(ApiAuth, self).get_urls()
        return urls + [
            url(r'^register/$', self.register, name='api_registration'),
            url(r'^confirm/(?P<key>[0-9af]{32})/$', self.confirm_registration,
                name='api_confirm')]

    def register(self, request):
        if request.method == 'POST':
            form = self.get_key_model_form()(request.POST)
            if form.is_valid():
                newkey = form.save(commit=False)
                newkey.key = uuid.uuid4().hex
                if self.require_confirmation:
                    newkey.status = 'U'
                else:
                    newkey.status = 'A'
                newkey.save()
                self.publish_new_key(key.key, key.email, key.status)

            email_msg = render_to_string(self.registration_email_template,
                                         {'key': newkey})
            send_mail(self.registration_email_subject, email_msg,
                      self.registration_email_from, [newkey.email])
            return render_to_response(self.registration_complete_template,
                                      {'key': newkey})
        else:
            form = self.get_key_model_form()()
        return render_to_response(self.registration_template, {'form':form})

    def confirm_registration(self, request, key):
        context = {}
        try:
            context['key'] = key_obj = self.key_model.get(key=key)
            if key_obj.status != 'U':
                context['error'] = 'Key Already Activated'
            else:
                key_obj.status = 'A'
                key_obj.save()
                self.publish_key_update(key_obj.key, key_obj.email, key_obj.status)
        except self.key_model.DoesNotExist:
            context['error'] = 'Invalid Key'
        return render_to_response(self.registration_confirmed_template, context)
