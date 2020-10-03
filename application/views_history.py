import sys

from django.template import loader
from django.http import HttpResponse, JsonResponse
from application.models import TranslationHistory
from django.contrib.auth.decorators import login_required

@login_required
def historylist(request):
    template = loader.get_template('app/history_list.html')
    filters = {}
    data = []
    for history in TranslationHistory.objects.filter(work__user=request.user.id).order_by('createdDate').reverse():
        onedata = {}
        onedata['work_id'] = history.work.id
        onedata['workTitle'] = history.work.workTitle
        onedata['TranslationType'] = history.TranslationType
        onedata['beforeTranslation'] = history.beforeTranslation
        onedata['afterTranslation'] = history.afterTranslation
        onedata['createdDate'] = history.createdDate
        data.append(onedata)
    return HttpResponse(template.render({"data": data}, request))

