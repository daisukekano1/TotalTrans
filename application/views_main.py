from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse
from application.models import Works, Language, WorkUserTag, UserTag, UserGlossary, TranslationHistory
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def home(request):
    filters = {'user_id': request.user.id}
    template = loader.get_template('app/main_home.html')
    # Work counts
    count = {}
    count['DraftCount'] = Works.objects.filter(**filters).filter(status='Draft').count()
    count['OpenCount'] = Works.objects.filter(**filters).filter(status='Open').count()
    count['AllCount'] = Works.objects.filter(**filters).count()
    # Tags
    tags = []
    for tag in UserTag.objects.filter(**filters).filter(validFlg=1).order_by('createdDate'):
        onedata = {}
        onedata['id'] = tag.id
        onedata['tagname'] = tag.tagname
        onedata['workcount'] = WorkUserTag.objects.filter(tag__exact=tag.id).count()
        tags.append(onedata)
    # glossary
    gl = UserGlossary.objects.filter(**filters).first()
    glossary = {}
    if gl != None:
        glossary['keyid'] = gl.id
        glossary['count'] = gl.numberofcount

    transhistory = []
    for history in TranslationHistory.objects.select_related('work').filter(work__user_id=request.user.id).order_by('createdDate').reverse()[:3]:
        onedata = {}
        onedata['workTitle'] = history.work.workTitle
        onedata['TranslationType'] = history.TranslationType
        onedata['beforeTranslation'] = history.beforeTranslation
        onedata['afterTranslation'] = history.afterTranslation
        onedata['createdDate'] = history.createdDate

    works_eta = []
    for work in Works.objects.filter(**filters).filter(eta).order_by('createdDate').reverse():
        onedata = {}
        onedata['work_id'] = work.id
        onedata['workTitle'] = work.workTitle
        onedata['eta'] = work.eta
        dt_now = datetime.datetime.now()
        if work.etagftr
        onedata['message'] = work.eta
        works_eta.append(onedata)

    works_draft = []
    for work in Works.objects.filter(**filters).filter(status='Draft').order_by('createdDate').reverse():
        onedata = {}
        onedata['work_id'] = work.id
        onedata['workTitle'] = work.workTitle
        srclang = Language.objects.filter(lc__exact=work.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=work.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['tags'] = WorkUserTag.objects.filter(work__exact=work.id).select_related('tag').values('tag__tagname', 'tag__backgroundcolor')
        onedata['createdDate'] = work.createdDate
        onedata['eta'] = work.eta
        works_draft.append(onedata)

    works_open = []
    for work in Works.objects.filter(**filters).filter(status='Open').order_by('createdDate').reverse():
        onedata = {}
        onedata['work_id'] = work.id
        onedata['workTitle'] = work.workTitle
        srclang = Language.objects.filter(lc__exact=work.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=work.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['tags'] = WorkUserTag.objects.filter(work__exact=work.id).select_related('tag').values('tag__tagname', 'tag__backgroundcolor')
        onedata['progress'] = work.progress
        onedata['createdDate'] = work.createdDate
        onedata['eta'] = work.eta
        works_open.append(onedata)

    data = {
        'count': count,
        'tags' : tags,
        'glossary' : glossary,
        'transwork' : transwork,
        'works_draft': works_draft,
        'works_open': works_open
    }
    return HttpResponse(template.render(data, request))

def contact(request):
    return render(request, 'app/main_contact.html')

def submitContact(request):
    return render(request, 'app/main_contactcompleted.html')

def manual(request):
    return render(request, 'app/main_manual.html')

def termsanduse(request):
    return render(request, 'app/main_termsanduse.html')