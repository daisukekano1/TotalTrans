import sys

from django.template import loader
import json
import re
import math
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

from application.models import Works, Language, TranslationHistory, WorkUserTag, UserTag, UserGlossary, CustomUser
from django.contrib.auth.decorators import login_required
from application.customlib import GoogleApiLib, DataLib, CookieLib

from datetime import datetime as dt
from bs4 import BeautifulSoup
import requests as req

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

@login_required
def worklist(request):
    CookieLib.setLanguage(request)
    template = loader.get_template('app/work_list.html')
    filters = {}
    tag = request.GET.get("tag")
    status = request.GET.get("status")
    if status != None:
        filters = {'user_id': request.user.id, 'status':status}
    elif tag != None:
        filters = {'user_id': request.user.id, 'workusertag__tag__tagname':tag }
    else:
        filters = {'user_id': request.user.id}

    data = []
    for work in Works.objects.filter(**filters).order_by('createdDate').reverse():
        onedata = {}
        onedata['work_id'] = work.id
        onedata['workTitle'] = work.workTitle
        srclang = Language.objects.filter(lc__exact=work.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=work.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['tags'] = WorkUserTag.objects.filter(work__exact=work.id).select_related('tag').values('tag__tagname', 'tag__backgroundcolor', 'tag__textcolor')
        onedata['progress'] = work.progress
        onedata['createdDate'] = work.createdDate
        onedata['status'] = work.status
        onedata['eta'] = work.eta

        data.append(onedata)
    return HttpResponse(template.render({"data": data}, request))

@login_required
def workcreation(request, work_id = 0):
    CookieLib.setLanguage(request)
    work = Works.objects.filter(user=request.user.id).filter(id=work_id).first()
    langs = Language.objects.filter(validFlag=1).extra(select = { 'displaylang' : request.user.userLanguage}).values('lc','language', 'displaylang').order_by('displaylang')
    worktags = WorkUserTag.objects.filter(work_id=work_id).values('tag__tagname', 'tag__backgroundcolor', 'tag__textcolor')
    tags = UserTag.objects.filter(user__exact=request.user.id).values('id', 'tagname','backgroundcolor', 'textcolor')
    selectedlang = {}
    if work == None:
        dlib = DataLib()
        selectedlang = dlib.getUserLang(request)
    else:
        selectedlang = {
            'srcValue': work.lc_src,
            'srcName': Language.objects.filter(lc__exact=work.lc_src).extra(
                select={'displaylang': request.user.userLanguage}).values('displaylang').first(),
            'tgtValue': work.lc_tgt,
            'tgtName': Language.objects.filter(lc__exact=work.lc_tgt).extra(
                select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        }
    data = {
        'langs' :langs,
        'tags' : json.dumps(list(tags), cls=DjangoJSONEncoder),
        'selectedlang' : selectedlang,
        'work' : work,
        'worktags' : json.dumps(list(worktags), cls=DjangoJSONEncoder)
    }
    return render(request, 'app/work_add.html', data)

@login_required
def savework(request):
    save(request)
    data = {
        'work_id': request.POST['work_id']
    }
    return JsonResponse({"data": data})

@login_required
def startTranslation(request):
    save(request)
    work_id = request.POST['work_id']
    return redirect(workdetail, work_id)

@login_required
def save(request):
    etastr = request.POST['eta']
    eta = None
    if etastr != '':
        eta = dt.strptime(etastr, '%Y/%m/%d')
    status = request.POST['status']
    work_id = request.POST['work_id']
    redirecttarget = ''
    if work_id == '':
        t1 = Works(
            user_id = request.user.id,
            workTitle = request.POST['workTitle'],
            wordsOriginal = request.POST['wordsOriginal'],
            lc_src = request.POST['lc_src'],
            lc_tgt = request.POST['lc_tgt'],
            progress = 0,
            # numberofchar = len(str(request.POST['wordsOriginal'])),
            wordsTranslated = request.POST['wordsOriginal'],
            status = status,
            eta = eta,
            url = request.POST['url'],
            createdDate = timezone.now()
        )
        t1.save()
        work_id = Works.objects.latest('id').id
    else:
        t1 = Works.objects.filter(user=request.user.id).filter(id=work_id).first()
        if t1 != None:
            t1.workTitle = request.POST['workTitle']
            t1.wordsOriginal = request.POST['wordsOriginal']
            t1.lc_src = request.POST['lc_src']
            t1.lc_tgt = request.POST['lc_tgt']
            t1.wordsTranslated = request.POST['wordsOriginal']
            t1.eta = eta
            t1.status = status
            t1.url = request.POST['url']
            t1.save()

    tags = json.loads(request.POST['tagsinfo'])
    for tag in tags:
        ut = UserTag.objects.filter(user=request.user.id).filter(tagname=tag['tagname'])
        tag_id = 0
        if ut.first() is None:
            t2 = UserTag(
                user_id=request.user.id,
                tagname=tag['tagname'],
                backgroundcolor=tag['backgroundcolor'],
                textcolor=tag['textcolor'],
                createdDate=timezone.now()
            )
            t2.save()
            tag_id = UserTag.objects.filter(user=request.user.id).latest().id
        else:
            tag_id = ut.first().id;
        wt = WorkUserTag.objects.filter(work=work_id).filter(tag=tag_id)
        if wt.first() is None:
            t3 = WorkUserTag(
                work_id=work_id,
                tag_id=tag_id,
                createdDate=timezone.now()
            )
            t3.save()

@login_required
def addTag(request):
    work_id = request.GET.get("work_id")
    tagname = request.GET.get("tagname")
    backgroundcolor = request.GET.get("backgroundcolor")
    textcolor = request.GET.get("textcolor")
    querySet = UserTag.objects.filter(user=request.user.id).filter(tagname=tagname)
    tagId = None
    if querySet.first() is None:
        t2 = UserTag(
            user_id=request.user.id,
            tagname=tagname,
            backgroundcolor=backgroundcolor,
            textcolor=textcolor,
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

@login_required
def removeTag(request):
    work_id = request.GET.get("work_id")
    tagname = request.GET.get("tagname")
    WorkUserTag.objects.filter(work=work_id).filter(tag__tagname=tagname).delete()
    return HttpResponse()

@login_required
def requestTranslation(request):
    return render(request, 'app/requestTranslation.html')

@login_required
def workdetail(request, work_id):
    CookieLib.setLanguage(request)
    for vals in Works.objects.filter(pk=work_id):
        work = {}
        work['work_id'] = work_id
        work['workTitle'] = vals.workTitle
        work['wordsOriginal'] = vals.wordsOriginal
        work['progress'] = vals.progress
        work['createdDate'] = vals.createdDate
        work['numberofchar'] = vals.numberofchar
        work['lc_src'] = vals.lc_src
        work['lc_tgt'] = vals.lc_tgt
        work['wordsTranslated'] = vals.wordsTranslated
        work['eta'] = vals.eta
        work['status'] = vals.status
        srclang = Language.objects.filter(lc__exact=vals.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=vals.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        work['srclang'] = srclang['displaylang']
        work['tgtlang'] = tgtlang['displaylang']
        work['tags'] = tgtlang['displaylang']
    worktags = WorkUserTag.objects.filter(work_id=work_id).values('tag__tagname', 'tag__backgroundcolor', 'tag__textcolor')
    usertags = UserTag.objects.filter(user__exact=request.user.id).values('id', 'tagname', 'backgroundcolor', 'textcolor')
    data = {
        'work': work,
        'worktags' : json.dumps(list(worktags), cls=DjangoJSONEncoder),
        'usertags' : json.dumps(list(usertags), cls=DjangoJSONEncoder)
    }
    return render(request, 'app/work_detail.html', data)

@login_required
def gethistory(request, work_id = 0):
    data = []
    filters = {}
    if work_id != 0:
        filters = {'work_id': work_id}

    data = []
    for vals in TranslationHistory.objects.filter(**filters):
        onedata = {}
        onedata['work_id'] = vals.work_id
        onedata['historyNum'] = vals.historyNum
        onedata['workTitle'] = vals.work.workTitle
        onedata['createdDate'] = vals.createdDate
        onedata['createdDateTime'] = vals.createdDate.strftime('%Y/%m/%d %H:%M')
        onedata['TranslationType'] = vals.TranslationType
        onedata['beforeTranslation'] = vals.beforeTranslation
        onedata['afterTranslation'] = vals.afterTranslation
        onedata['startline'] = vals.startline
        onedata['startchar'] = vals.startchar
        onedata['endline'] = vals.endline
        onedata['endchar'] = vals.endchar
        data.append((onedata))

    return JsonResponse({"data": data})

@login_required
def requestGengoTranslation(request):
    result = []
    return JsonResponse({"data": result})

@login_required
def requestGoogleTranslation(request):
    text = request.GET.get("originalText")
    lc_src = request.GET.get("lc_src")
    lc_tgt = request.GET.get("lc_tgt")
    glossary_id = ""
    ug = UserGlossary.objects.filter(user=request.user.id).filter(lc_src=lc_src).filter(lc_tgt=lc_tgt).first()
    if ug != None:
        glossary_id = ug.filename
    result = GoogleApiLib.requestGoogleTranslation(text, glossary_id, lc_src, lc_tgt)
    return JsonResponse({"data": result})

@login_required
def saveGoogleTranslation(request):
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
        createdDate=timezone.now(),
        startline=request.GET.get("startline"),
        startchar=request.GET.get("startchar"),
        endline=request.GET.get("endline"),
        endchar=request.GET.get("endchar")
    )
    t2.save()

    work = Works.objects.get(pk=work_id)
    # work.wordsOriginal = getConvertWords(work.wordsOriginal, OriginalText, OriginalText, historyNum, "g")
    work.wordsTranslated = getConvertWords(work.wordsTranslated, OriginalText, TranslatedText, historyNum, "g")
    work.progress = getPercentage3(work_id)
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress': work.progress
    }
    return JsonResponse(data)

@login_required
def saveSelfTranslation(request):
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
        createdDate=timezone.now(),
        startline = request.GET.get("startline"),
        startchar = request.GET.get("startchar"),
        endline = request.GET.get("endline"),
        endchar = request.GET.get("endchar"),
    )
    t2.save()

    work = Works.objects.get(pk=work_id)
    work.wordsTranslated = getConvertWords(work.wordsTranslated, OriginalText, TranslatedText, historyNum, "s")
    work.progress = getPercentage3(work_id)
    work.save()
    data = {
        'wordsTranslated': work.wordsTranslated,
        'progress': work.progress
    }
    return JsonResponse(data)

@login_required
def saveIgnoreTranslation(request):
    work_id = request.GET.get("work_id")
    OriginalText = request.GET.get("OriginalText").replace('\n', '\r\n')
    historyNum = 1
    querySet = TranslationHistory.objects.filter(work_id=work_id).order_by("historyNum")
    if querySet.first() is not None:
        historyNum = querySet.last().historyNum + 1

    # Insert History
    t2 = TranslationHistory(
        work_id = work_id,
        beforeTranslation = OriginalText,
        afterTranslation = OriginalText,
        TranslationType = "Ignore",
        historyNum = historyNum,
        createdDate=timezone.now(),
        startline=request.GET.get("startline"),
        startchar=request.GET.get("startchar"),
        endline=request.GET.get("endline"),
        endchar=request.GET.get("endchar")
    )
    t2.save()

    work = Works.objects.get(pk=work_id)
    work.wordsTranslated = getConvertWords(work.wordsTranslated, OriginalText, OriginalText, historyNum, "i")
    work.progress = getPercentage3(work_id)
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress': work.progress
    }
    return JsonResponse(data)

def getPercentage2(wordsTranslated):
    wkval = wordsTranslated.replace('\r\n','')
    wkval = wordsTranslated.replace('\n','')
    wk = ''
    wk2 = ''
    removeTags = re.sub(r'\[(s|g|i):(e|s):[0-9]+\]','', wkval)
    totallength = len(removeTags)
    while bool(re.search('\[(s|g|i):s:[0-9]+\]',wkval)):
        search = re.search('\[(s|g|i):s:[0-9]+\]',wkval)
        wkval = wkval[search.start():]
        wk = re.sub('\[(s|g|i):s:[0-9]+\]', '', wkval, 1)
        wk = re.sub('\[(s|g|i):e:.*$', '', wk)
        wk2 = wk2 + wk
        search = re.search('\[(s|g|i):e:[0-9]+\]', wkval)
        wkval = wkval[search.end():]
    wklen = len(wk2)
    return math.ceil(wklen/totallength * 100)

def getPercentage3(work_id):
    work = Works.objects.get(pk=work_id)
    history = TranslationHistory.objects.filter(work_id=work_id)
    totallength = len(work.wordsOriginal)
    translatedlength = 0
    for vals in history:
        translatedlength = translatedlength + len(vals.beforeTranslation)
    return math.ceil(translatedlength/totallength * 100)

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

@login_required
def deleteHistory(request):
    work_id = request.GET.get("work_id")
    historyNum = request.GET.get("historyNum")
    history = TranslationHistory.objects.filter(work=work_id).filter(historyNum=historyNum).first()
    beforeTranslation = history.beforeTranslation
    afterTranslation = history.afterTranslation
    history.deleteFlag = 1
    history.save()

    work = Works.objects.get(pk=work_id)
    work.wordsTranslated = re.sub('\[(s|g|i):s:'+str(historyNum)+'\]'+afterTranslation+'\[(s|g|i):e:'+str(historyNum)+'\]',
                                  beforeTranslation,
                                  work.wordsTranslated)
    work.progress = getPercentage3(work_id)
    work.save()
    data = {
        'wordsOriginal': work.wordsOriginal,
        'wordsTranslated': work.wordsTranslated,
        'progress':work.progress
    }
    return JsonResponse(data)

@login_required
def history(request):
    CookieLib.setLanguage(request)
    return render(request, 'app/work_history.html')

@login_required
def workstart(request, work_id = 0):
    work = Works.objects.filter(user=request.user.id).filter(id=work_id).first()
    work.status = "Open"
    work.save()
    return redirect("workdetail", work_id=work_id)

@login_required
def workclose(request, work_id = 0):
    work = Works.objects.filter(user=request.user.id).filter(id=work_id).first()
    work.status = "Closed"
    work.save()
    return redirect("worklist")

@login_required
def workreopen(request, work_id = 0):
    work = Works.objects.filter(user=request.user.id).filter(id=work_id).first()
    work.status = "Open"
    work.save()
    return redirect("workdetail", work_id=work_id)

@login_required
def getTextfromURL(request):
    url = request.GET.get("url")
    html = req.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    for i in soup.select("br"):
        i.replace_with("\n")
    text = soup.body.get_text()
    text = '\n'.join(filter(lambda x: x.strip(), map(lambda x: x.strip(), text.split('\n'))))
    data = {
        'text': text
    }
    return JsonResponse(data)

