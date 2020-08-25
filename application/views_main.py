from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse
from application.models import Works, Language, WorkUserTag, UserTag
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    template = loader.get_template('app/main_home.html')
    filters = {'user_id': request.user.id}
    works = []
    for work in Works.objects.filter(**filters).order_by('createdDate').reverse():
        onedata = {}
        onedata['id'] = work.id
        onedata['wordsOriginal'] = work.wordsOriginal
        srclang = Language.objects.filter(lc__exact=work.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=work.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['tags'] = WorkUserTag.objects.filter(work__exact=work.id).select_related('tag').values('tag__tagname', 'tag__backgroundcolor')
        onedata['progress'] = work.progress
        onedata['createdDate'] = work.createdDate
        onedata['numberofchar'] = work.numberofchar
        onedata['status'] = work.status

        works.append(onedata)
    tags = []
    for tag in UserTag.objects.filter(**filters).filter(validFlg=1).order_by('createdDate'):
        onedata = {}
        onedata['id'] = tag.id
        onedata['tagname'] = tag.tagname
        onedata['workcount'] = WorkUserTag.objects.filter(tag__exact=tag.id).count()
        tags.append(onedata)
    count = {}
    count['DraftCount'] = Works.objects.filter(**filters).filter(status='Draft').count()
    count['OpenCount'] = Works.objects.filter(**filters).filter(status='Open').count()
    count['AllCount'] = Works.objects.filter(**filters).count()
    data = {
        'works': works,
        'tags' : tags,
        'count': count
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