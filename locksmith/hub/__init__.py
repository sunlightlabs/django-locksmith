from django.conf.urls.defaults import url
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.http import require_POST

from locksmith.common import ViewsBase, apicall, get_signature
from locksmith.hub.models import Api, Key, Report

class HubViews(ViewsBase):

    key_model = Key

    def verify_signature(self, post):
        api = get_object_or_404(Api, name=post['api'])
        return get_signature(post, api.signing_key) == post['signature']

    def get_urls(self):
        urls = super(HubViews, self).get_urls()
        return urls + [
            url(r'^report_calls/$', require_POST(self.report_calls),
                name='report_calls'),
            url(r'^$', self.analytics_index, name='analytics_index'),
        ]

    def report_calls(self, request):
        if not self.verify_signature(request.POST):
            return HttpResponseBadRequest('bad signature')

        api_obj = get_object_or_404(Api, name=request.POST['api'])
        key_obj = get_object_or_404(Key, key=request.POST['key'])

        calls = int(request.POST['calls'])
        try:
            report,c = Report.objects.get_or_create(date=request.POST['date'],
                                                    api=api_obj,
                                                    key=key_obj,
                                                    endpoint=request.POST['endpoint'],
                                                    defaults={'calls':calls})
            if not c:
                report.calls = calls
                report.save()
        except Exception, e:
            print e
            raise

        return HttpResponse('OK')


    def create_key(self, request):
        api_obj = get_object_or_404(Api, name=request.POST['api'])

        # create the key
        key = Key.objects.create(key=request.POST['key'],
                                 email=request.POST['email'],
                                 issued_by=api_obj,
                                 status=request.POST['status'])
        # notify other servers
        for api in Api.objects.exclude(name=api_obj.name):
            apicall('%s/create_key/' % api.url, api.signing_key, api=api.name,
                    key=key.key, email=key.email, status=key.status)

        return HttpResponse('OK')

    def update_key(self, request, get_by='key'):

        super(HubViews, self).update_key(request, get_by)

        api_obj = get_object_or_404(Api, name=request.POST['api'])

        # notify other servers
        endpoint = 'update_key' if get_by == 'key' else 'update_key_by_email'
        for api in Api.objects.exclude(name=api_obj.name):
            apicall('%s/%s/' % (api.url, endpoint), api.signing_key,
                    api=api.name, key=key.key, email=key.email, 
                    status=key.status)

        return HttpResponse('OK')

    # analytics views

    def analytics_index(self, request):
        apis = Api.objects.all().annotate(calls=Sum('reports__calls'))
        return render_to_response('locksmith/analytics_index.html',
                                  {'apis':apis})

site = HubViews()
