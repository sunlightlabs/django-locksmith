from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.conf.urls.defaults import url
from django.views.decorators.http import require_POST
from locksmith.common import ApiBase
from locksmith.hub.models import Api, Key, Report

class ApiHub(ApiBase):

    def verify_signature(self, post):
        api_obj = get_object_or_404(Api, name=post['api'])
        return self.get_signature(post, api_obj.key) == post['signature']

    def get_urls(self):
        urls = super(ApiHub, self).get_urls()
        urls.append(
            url(r'^report_views/$', require_POST(self.report_views),
                name='report_views')
        )
        return urls

    def report_views(self, request):
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
            apicall('%s/create_key/' % api.url, api=api.name,
                    key=key.key, email=key.email, status=key.status)

        return HttpResponse('OK')

    def update_key(self, request, get_by='key'):
        api_obj = get_object_or_404(Api, name=request.POST['api'])

        # get the key
        if get_by == 'key':
            key = get_object_or_404(Key, key=request.POST['key'])
        elif get_by == 'email':
            key = get_object_or_404(Key, key=request.POST['email'])

        # update key
        key.key = request.POST['key']
        key.email = request.POST['email']
        key.status = request.POST['status']
        key.save()

        # notify other servers
        endpoint = 'update_key' if get_by == 'key' else 'update_key_by_email'
        for api in Api.objects.exclude(name=api_obj.name):
            apicall('%s/%s/' % (api.url, endpoint), api=api.name,
                    key=key.key, email=key.email, status=key.status)

        return HttpResponse('OK')
