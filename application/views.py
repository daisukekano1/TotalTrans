import sys

from django.template import loader
import json
import re
import requests
import math
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

from gengo import Gengo
from application.models import Works, Language, TranslationHistory, WorkUserTag, UserTag

from oauth2client.client import GoogleCredentials
from google.cloud import translate_v2 as translate
import os
from googleapiclient import discovery
from googleapiclient import errors

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

GOOGLEAPI_KEY = 'AIzaSyD0CNmHW04AtsTTyYJSvcdf5i99MmPzUQ8'
def index(request):
    request.session['user_id'] = 1
    request.session['user_lang'] = 'japanese'

    template = loader.get_template('app/index.html')
    user_id = request.session['user_id']
    user_lang = request.session['user_lang']

    filters = {'user_id': user_id}
    data = []
    for work in Works.objects.filter(**filters).order_by('createdDate').reverse():
        onedata = {}
        onedata['id'] = work.id
        onedata['wordsOriginal'] = work.wordsOriginal
        srclang = Language.objects.filter(lc__exact=work.lc_src).extra(select={'displaylang': user_lang}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=work.lc_tgt).extra(select={'displaylang': user_lang}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['tags'] = WorkUserTag.objects.filter(work__exact=work.id).select_related('tag').values('tag__tagname', 'tag__backgroundcolor')
        onedata['progress'] = work.progress
        onedata['createdDate'] = work.createdDate
        onedata['numberofchar'] = work.numberofchar
        onedata['status'] = work.status

        data.append(onedata)
    return HttpResponse(template.render({"data": data}, request))

def addwork(request):
    request.session['user_id'] = 1
    request.session['user_lang'] = 'japanese'
    user_id = request.session['user_id']
    user_lang = request.session['user_lang']
    langs = Language.objects.filter(validFlag=1).extra(select = { 'displaylang' : user_lang}).values('lc','language','flagId', 'displaylang').order_by('displaylang')
    tags = UserTag.objects.filter(user__exact=user_id).values('id', 'tagname','backgroundcolor')
    return render(request, 'app/addwork.html', {'langs' : langs, 'tags' : json.dumps(list(tags), cls=DjangoJSONEncoder)})

def getTargetLang(request):
    user_lang = request.session['user_lang']
    lc_src = request.GET.get("lc_src")
    gengo = Gengo(
        public_key=GENGO_PUBLIC_KEY,
        private_key=GENGO_PRIVATE,
        sandbox=GENGO_SANDBOX_FLG,
        debug=True
    )
    langpair = gengo.getServiceLanguagePairs(lc_src=lc_src)
    langpairArr = []
    for val in langpair['response']:
        langpairArr.append(val['lc_tgt'])
    langs = Language.objects.filter(lc__in=langpairArr).extra(select = { 'id' :'lc' , 'text' : user_lang}).values('id', 'text').order_by('text')
    return JsonResponse({"langs": list(langs)})

def saveWork(request):
    request.session['user_id'] = 1
    request.session['user_lang'] = 'japanese'

    user_id = request.session['user_id']

    # gengo = Gengo(
    #     public_key=GENGO_PUBLIC_KEY,
    #     private_key=GENGO_PRIVATE,
    #     sandbox=GENGO_SANDBOX_FLG,
    #     debug=True
    # )
    # jobs_data = {
    #     'job_1': {
    #         'type': 'text',
    #         'body_src': request.POST['wordsOriginal'],
    #         'lc_src': request.POST['lc_src'],
    #         'lc_tgt': request.POST['lc_tgt'],
    #         'tier': 'standard',
    #         'auto_approve': 0
    #     }
    # }
    # gengores = gengo.determineTranslationCost(jobs=jobs_data)
    t1 = Works(
        user_id = user_id,
        wordsOriginal = request.POST['wordsOriginal'],
        lc_src = request.POST['lc_src'],
        lc_tgt = request.POST['lc_tgt'],
        progress = 0,
        createdDate = timezone.now(),
        numberofchar = len(str(request.POST['wordsOriginal'])),
        wordsTranslated = request.POST['wordsOriginal'],
        status = 'Open'
    )
    t1.save()
    work = Works.objects.latest('id')
    tags = json.loads(request.POST['tagsinfo'])
    for tag in tags:
        querySet = UserTag.objects.filter(user=user_id).filter(tagname=tag['tagname'])
        if querySet.first() is None:
            t2 = UserTag(
                user_id=user_id,
                tagname=tag['tagname'],
                backgroundcolor=tag['backgroundcolor'],
                createdDate=timezone.now()
            )
            t2.save()
    return redirect('workdetail', work.id)

def addTag(request):
    request.session['user_id'] = 1
    user_id = request.session['user_id']

    work_id = request.GET.get("work_id")
    tagname = request.GET.get("tagname")
    backgroundcolor = request.GET.get("backgroundcolor")
    querySet = UserTag.objects.filter(user=user_id).filter(tagname=tagname)
    tagId = None
    if querySet.first() is None:
        t2 = UserTag(
            user_id=user_id,
            tagname=tagname,
            backgroundcolor=backgroundcolor,
            createdDate=timezone.now()
        )
        t2.save()
        tagId = UserTag.objects.latest().id
    else:
        tagId = querySet.first().id

    querySet = WorkUserTag.objects.filter(work=work_id).filter(tag=tagId)
    if querySet.first() is None:
        t3 = WorkUserTag(
            work_id=work_id,
            tag_id=tagId,
            createdDate=timezone.now()
        )
        t3.save()
    return HttpResponse()

def removeTag(request):
    request.session['user_id'] = 1
    user_id = request.session['user_id']
    work_id = request.GET.get("work_id")
    tagname = request.GET.get("tagname")
    WorkUserTag.objects.filter(work=work_id).filter(tag__tagname=tagname).delete()
    return HttpResponse()

def requestTranslation(request):
    gengo = Gengo(
        public_key=GENGO_PUBLIC_KEY,
        private_key=GENGO_PRIVATE,
        sandbox=GENGO_SANDBOX_FLG,
        debug=True
    )
    #     jobs = gengo.getTranslationJobBatch(id="3391238,3391236")
    languages = gengo.getServiceLanguages();
    data = {
        'languages': languages
    }
    return render(request, 'app/requestTranslation.html', {'data': data})

def workdetail(request, work_id):
    request.session['user_id'] = 1
    request.session['user_lang'] = 'japanese'

    user_id = request.session['user_id']
    user_lang = request.session['user_lang']

    for vals in Works.objects.filter(pk=work_id):
        work = {}
        work['work_id'] = work_id
        work['wordsOriginal'] = vals.wordsOriginal
        work['progress'] = vals.progress
        work['createdDate'] = vals.createdDate
        work['numberofchar'] = vals.numberofchar
        work['lc_src'] = vals.lc_src
        work['lc_tgt'] = vals.lc_tgt
        work['wordsTranslated'] = vals.wordsTranslated
        work['status'] = vals.status
        srclang = Language.objects.filter(lc__exact=vals.lc_src).extra(select={'displaylang': user_lang}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=vals.lc_tgt).extra(select={'displaylang': user_lang}).values('displaylang').first()
        work['srclang'] = srclang['displaylang']
        work['tgtlang'] = tgtlang['displaylang']
        work['tags'] = tgtlang['displaylang']
    worktags = WorkUserTag.objects.filter(work_id=work_id).values('tag__tagname', 'tag__backgroundcolor')
    usertags = UserTag.objects.filter(user__exact=user_id).values('id', 'tagname', 'backgroundcolor')
    data = {
        'work': work,
        'worktags' : json.dumps(list(worktags), cls=DjangoJSONEncoder),
        'usertags' : json.dumps(list(usertags), cls=DjangoJSONEncoder)
    }
    return render(request, 'app/workdetail.html', data)

def gethistory(request, work_id):
    data = []
    for vals in TranslationHistory.objects.filter(work_id=work_id):
        onedata = {}
        onedata['historyNum'] = vals.historyNum
        onedata['createdDate'] = vals.createdDate
        onedata['TranslationType'] = vals.TranslationType
        onedata['beforeTranslation'] = vals.beforeTranslation
        onedata['afterTranslation'] = vals.afterTranslation
        onedata['jobid'] = vals.jobid
        data.append((onedata))

    return JsonResponse({"data": data})

def requestGengoTranslation(request):
    result = []
    return JsonResponse({"data": result})

def requestGoogleTranslation(request):
    url = "https://translation.googleapis.com/language/translate/v2"
    url += "?key=" + GOOGLEAPI_KEY

    request.session['user_id'] = 1
    user_id = request.session['user_id']

    work_id = request.GET.get("work_id")
    tagname = request.GET.get("tagname")
    backgroundcolor = request.GET.get("backgroundcolor")

    url += "&q=" + request.GET.get("originalText")
    url += "&source=" + request.GET.get("lc_src")
    url += "&target=" + request.GET.get("lc_tgt")

    rr = requests.get(url)
    unit_aa = json.loads(rr.text)
    result = unit_aa["data"]["translations"][0]["translatedText"]
    return JsonResponse({"data": result})

    # # Imports the Google Cloud client library
    #
    # # add environment variable
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "translate-f085d3b42d5b.json"
    # #AIzaSyD0CNmHW04AtsTTyYJSvcdf5i99MmPzUQ8
    #
    # # Certification
    # credentials = GoogleCredentials.get_application_default()
    # # Instantiates a client
    # translate_client = translate.Client()
    #
    # # The text to translate
    # text = u'Hello, world!'
    # # The source and target language
    # trans_from = 'en'
    # trans_to = 'ja'
    #
    # # Translates some text into Japanese
    # translation = translate_client.translate(text, source_language=trans_from, target_language=trans_to, model='nmt')
    #
    # print(u'Text: {}'.format(text))
    # print(u'Translation: {}'.format(translation['translatedText']))
    # print(translation)


def saveGengoTranslation(request):
    data = {}
    return JsonResponse(data)

def saveGoogleTranslation(request):
    request.session['user_id'] = 1
    user_id = request.session['user_id']

    work_id = request.GET.get("work_id")
    OriginalText = request.GET.get("googleOriginalText").replace('\n', '\r\n')
    TranslatedText = str(request.GET.get("googleTranslatedText")).replace('\n', '\r\n')
    historyNum = 1
    querySet = TranslationHistory.objects.filter(work_id=work_id).order_by("historyNum")
    if querySet.first() is not None:
        historyNum = querySet.last().historyNum + 1

    # Insert History
    t2 = TranslationHistory(
        work_id = work_id,
        beforeTranslation = OriginalText,
        afterTranslation = TranslatedText,
        TranslationType = "Google",
        historyNum = historyNum,
        createdDate=timezone.now()
    )
    t2.save()

    work = Works.objects.get(pk=work_id)
    work.wordsOriginal = getConvertWords(work.wordsOriginal, OriginalText, OriginalText, historyNum, "g")
    work.wordsTranslated = getConvertWords(work.wordsTranslated, OriginalText, TranslatedText, historyNum, "g")
    work.progress = getPercentage(work.wordsOriginal, "g")
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress': work.progress
    }
    return JsonResponse(data)

def saveSelfTranslation(request):
    request.session['user_id'] = 1
    user_id = request.session['user_id']

    work_id = request.GET.get("work_id")
    OriginalText = request.GET.get("selfOriginalText").replace('\n', '\r\n')
    TranslatedText = request.GET.get("selfTranslatedText").replace('\n', '\r\n')
    historyNum = 1
    querySet = TranslationHistory.objects.filter(work_id=work_id).order_by("historyNum")
    if querySet.first() is not None:
        historyNum = querySet.last().historyNum + 1

    # Insert History
    t2 = TranslationHistory(
        work_id = work_id,
        beforeTranslation = OriginalText,
        afterTranslation = TranslatedText,
        TranslationType = "Self",
        historyNum = historyNum,
        createdDate=timezone.now()
    )
    t2.save()

    work = Works.objects.get(pk=work_id)
    workoriginal = work.wordsOriginal
    work.wordsOriginal = getConvertWords(work.wordsOriginal, OriginalText, OriginalText, historyNum, "s")
    work.wordsTranslated = getConvertWords(work.wordsTranslated, OriginalText, TranslatedText, historyNum, "s")
    work.progress = getPercentage(work.wordsOriginal, "s")
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress': work.progress
    }
    return JsonResponse(data)

def getPercentage(wordsOriginal, typeprefix):
    wkval = wordsOriginal.replace('\r\n','')
    wkval = wkval.replace('\n','')
    wk = ''
    wk2 = ''
    removeTags = re.sub(r'\[(r|g|s):(e|s):[0-9]+\]','', wkval)
    totallength = len(removeTags)
    while bool(re.search('\['+typeprefix+':s:[0-9]+\]',wkval)):
        search = re.search('\['+typeprefix+':s:[0-9]+\]',wkval)
        wkval = wkval[search.start():]
        wk = re.sub('\['+typeprefix+':s:[0-9]+\]', '', wkval, 1)
        wk = re.sub('\['+typeprefix+':e:.*$', '', wk)
        wk2 = wk2 + wk
        search = re.search('\['+typeprefix+':e:[0-9]+\]', wkval)
        wkval = wkval[search.end():]
    wklen = len(wk2)
    return math.ceil(wklen/totallength * 100)

def getConvertWords(original, originalText, translatedText, historyId, typePrefix):
    wkval = original
    endFlag = False
    convertedwords = ''
    while endFlag == False:
        search = re.search('\['+typePrefix+':s:[0-9]+\]', wkval)
        if bool(search) == False:
            convertedwords = convertedwords + wkval.replace(originalText, '['+typePrefix+':s:' +str(historyId) +']'+translatedText+'['+typePrefix+':e:' +str(historyId) +']')
            endFlag = True
        else:
            convertedwords = convertedwords + wkval[:search.start()].replace(originalText, '['+typePrefix+':s:' +str(historyId) +']'+translatedText+'['+typePrefix+':e:' +str(historyId) +']')
            search = re.search('\['+typePrefix+':s:[0-9]+\]', wkval)
            wkval = wkval[search.start():]
            search = re.search('\['+typePrefix+':e:[0-9]+\]', wkval)
            convertedwords = convertedwords + wkval[:search.end()]
            wkval = wkval[search.end():]
    return convertedwords

def deleteHistory(request):
    request.session['user_id'] = 1
    user_id = request.session['user_id']
    work_id = request.GET.get("work_id")
    historyNum = request.GET.get("historyNum")
    history = TranslationHistory.objects.filter(work=work_id).filter(historyNum=historyNum).first()
    beforeTranslation = history.beforeTranslation
    afterTranslation = history.afterTranslation
    history.deleteFlag = 1
    history.save()

    work = Works.objects.get(pk=work_id)
    work.wordsOriginal = re.sub('\[(r|g|s):(s|e):'+str(historyNum)+'\]','',work.wordsOriginal)
    work.wordsTranslated = re.sub('\[(r|g|s):s:'+str(historyNum)+'\]'+afterTranslation+'\[(r|g|s):e:'+str(historyNum)+'\]',
                                  beforeTranslation,
                                  work.wordsTranslated)
    history = TranslationHistory.objects.filter(work_id=work_id).filter(historyNum=historyNum).first()
    typeprefix = ""
    if history.TranslationType == "Request":
        typeprefix = "r"
    elif history.TranslationType == "Google":
        typeprefix = "g"
    elif history.TranslationType == "Self":
        typeprefix = "s"
    work.progress = getPercentage(work.wordsOriginal, typeprefix)
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress':work.progress
    }
    return JsonResponse(data)
