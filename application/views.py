from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from gengo import Gengo
from application.models import Works

# GENGO Parameter
# GENGO_SANDBOX_FLG = False
# GENGO_URL = 'http://api.gengo.com/v2/translate/jobs'
# GENGO_PUBLIC_KEY = 'j[05V5zy_)DvoE8lpyD}pI{crbXqk@N^0x7DVr^QjLbrHwyS}=@H0(ruuEqGIR7g'
# GENGO_PRIVATE = 'pxYYiUIWRkjLxviSqHR)E_omsxVFm0PUeJ[c^KHsO)UL(pqB15vDoLu{=(wBG[e|'
# Sandbox
GENGO_SANDBOX_FLG = True
GENGO_URL = 'http://api.sandbox.gengo.com/v2/translate/jobs'
GENGO_PUBLIC_KEY = 'kq|NlLCoLWWaal-LTbdyFV$zXIbomiu|vPlBfevP6HGeJXXdTpgBN2JYkAMCHJh|'
GENGO_PRIVATE = 'vuqb9x2yEEL~WD0SPbe3f~RVU[e}6|Y$ZwAyo2Qu$slZ}gS(p}q|3iIfmm[hqHT9'

def index(request):
    template = loader.get_template('app/index.html')

    filters = {'user_id': 1}
    data = []
    for work in Works.objects.filter(**filters):
        onedata = {}
        onedata['id'] = work.id
        onedata['workTitle'] = work.workTitle
        onedata['wordsOriginal'] = work.WordsOriginal
        onedata['lc_src'] = work.lc_src
        onedata['lc_tgt'] = work.lc_tgt
        onedata['progress'] = work.progress
        onedata['createdDate'] = work.createdDate
        onedata['numberofchar'] = work.numberofchar
        onedata['status'] = work.status

        data.append(onedata)

    return HttpResponse(template.render({"data": data}, request))

def addwork(request):
    template = loader.get_template('app/addwork.html')
    data = []
    return HttpResponse(template.render({"data": data}, request))

def workdetail(request, work_id):
    template = loader.get_template('app/workdetail.html')
    data = Works.objects.get(pk=work_id)
    return HttpResponse(template.render({"data": data}, request))

# def index(request):
#     context = {}
#     template = loader.get_template('app/index.html')
#
#     gengo = Gengo(
#         public_key=GENGO_PUBLIC_KEY,
#         private_key=GENGO_PRIVATE,
#         sandbox=GENGO_SANDBOX_FLG,
#         debug=True
#     )
#     jobs = gengo.getTranslationJobBatch(id="3391238,3391236")
#     print(gengo.getTranslationJobs(count=15))
#     print(gengo.getTranslationJobBatch(id=3391230))
#     print(gengo.getTranslationJobComments(id=3391230))
#     print(gengo.getTranslationJobFeedback(id=3391230))
#     print(gengo.getTranslationJobRevisions(id=3391230))
#     print(gengo.getTranslationOrderJobs(id=295326))
#     print(gengo.getOrderComments(id=295326))
#
#     return HttpResponse(template.render(jobs, request))

def list_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))

