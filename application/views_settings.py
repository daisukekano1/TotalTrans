from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pprint, os
from application.models import UserGlossary, Language
from django.utils import timezone
import json
from django.http import JsonResponse
from application.customlib import GoogleApiLib

folder_id = '1z22K4kWicecG81sCPUOgnL1zwlOFKt5D'
message = ""
@login_required
def glossarylist(request):
    glossary = []
    for ug in UserGlossary.objects.filter(user=request.user.id):
        onedata = {}
        onedata['id'] = ug.id
        srclang = Language.objects.filter(lc__exact=ug.lc_src).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        tgtlang = Language.objects.filter(lc__exact=ug.lc_tgt).extra(select={'displaylang': request.user.userLanguage}).values('displaylang').first()
        onedata['srclang'] = srclang['displaylang']
        onedata['tgtlang'] = tgtlang['displaylang']
        onedata['numberofcount'] = ug.numberofcount
        glossary.append(onedata)

    langs = Language.objects.filter(validFlag=1).extra(select = { 'displaylang' : request.user.userLanguage}).values('lc','language','flagId', 'displaylang').order_by('displaylang')
    data = {
        'glossary' : glossary,
        'message' : message,
        'langs' : langs
    }
    return render(request, 'app/glossary_list.html', data)

def createGlossary(request):
    gauth = GoogleApiLib.getGoogleAuth()
    drive = GoogleDrive(gauth)
    lc_src = request.POST['lc_src']
    lc_tgt = request.POST['lc_tgt']
    title = 'glossary-' + str(request.user.id) + "_" + lc_src + "_" + lc_tgt
    f = drive.CreateFile({
        'title': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [{'id': folder_id}]})
    f.Upload()
    fileid = f['id']
    gc = gspread.authorize(gauth.credentials)
    workbook = gc.open_by_key(fileid)
    worksheet = workbook.sheet1

    worksheet.update_acell('A1', lc_src)
    worksheet.update_acell('B1', lc_tgt)

    t1 = UserGlossary(
        user_id = request.user.id,
        filename = title,
        numberofcount= 0,
        lc_src = lc_src,
        lc_tgt=lc_tgt,
        fileid=fileid,
        validFlg=1,
        createdDate = timezone.now(),
    )
    t1.save()
    message = "#Create Glossary is successful#"
    return redirect('glossarylist')

@login_required
def glossarydetail(request, glossary_id):
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=glossary_id).first()
    lc_src_displayname = ''
    lc_tgt_displayname = ''
    if ug != None:
        lc_src_display = Language.objects.filter(lc=ug.lc_src).extra(select = { 'displaylang' : request.user.userLanguage}).values('displaylang').first()
        lc_tgt_display = Language.objects.filter(lc=ug.lc_tgt).extra(select = { 'displaylang' : request.user.userLanguage}).values('displaylang').first()

    data = {
        'glossary_id' : glossary_id,
        'lc_src_display' : lc_src_display,
        'lc_tgt_display' : lc_tgt_display
    }
    return render(request, 'app/glossary_detail.html', data)

@login_required
def getglossarylist(request):
    glossary_id = request.GET['glossary_id']
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=glossary_id).first()
    glossary = []
    lc_src_displayname = ''
    lc_tgt_displayname = ''
    if ug != None:
        gauth = GoogleApiLib.getGoogleAuth()
        gc = gspread.authorize(gauth.credentials)
        workbook = gc.open_by_key(ug.fileid)
        worksheet = workbook.sheet1
        wklist = worksheet.get_all_values()
        wklist = wklist[1:]
        i = 1
        for val in wklist:
            onedata = {}
            onedata['id'] = str(i)
            onedata['WordName'] = val[0]
            onedata['Translate'] = val[1]
            glossary.append(onedata)
            i = i + 1
    return JsonResponse({"data": glossary})

@login_required
def saveGlossary(request, glossary_id):
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=glossary_id).first()
    glossaryjson = request.POST['glossaryjson']
    gauth = GoogleApiLib.getGoogleAuth()
    drive = GoogleDrive(gauth)
    fileid = ug.fileid
    gc = gspread.authorize(gauth.credentials)
    workbook = gc.open_by_key(fileid)
    worksheet = workbook.sheet1
    glossary = json.loads(glossaryjson)
    i = 2
    for val in glossary:
        worksheet.update('A'+str(i)+':B'+str(i), [[val['#WordName#'], val['#Translate#']]])
        i = i + 1
    if len(glossary) < ug.numberofcount:
        for j in range(ug.numberofcount - len(glossary)):
            worksheet.update('A'+str(i+j)+':B'+str(i+j), [['', '']])

    ug.numberofcount = len(glossary)
    ug.save()
    message = "#Update Glossary is successful#"
    return redirect('glossarydetail', glossary_id=glossary_id)

@login_required
def taglist(request):
    return render(request, 'app/tag_list.html')
