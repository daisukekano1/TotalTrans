from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import gspread
from pydrive.drive import GoogleDrive
from application.models import UserGlossary, Language, UserTag, WorkUserTag
from django.utils import timezone
import json
from django.http import JsonResponse
from application.customlib import GoogleApiLib

folder_id = '1z22K4kWicecG81sCPUOgnL1zwlOFKt5D'
message = ""

@login_required
def glossary(request):
    ug = UserGlossary.objects.filter(user=request.user.id).first()
    keyid = ""
    if ug != None:
        keyid = ug.id

    data = {
        'keyid' : keyid,
        'message' : message,
    }
    return render(request, 'app/glossary.html', data)

def createGlossary(request):
    lib = GoogleApiLib()
    gauth = lib.getGoogleAuth()
    drive = GoogleDrive(gauth)
    title = 'glossary-' + str(request.user.id)
    f = drive.CreateFile({
        'title': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [{'id': folder_id}]})
    f.Upload()
    fileid = f['id']
    gc = gspread.authorize(gauth.credentials)
    workbook = gc.open_by_key(fileid)
    worksheet = workbook.sheet1

    worksheet.update_acell('A1', 'key')
    worksheet.update_acell('B1', 'value')
    worksheet.update_acell('C1', 'Category')

    t1 = UserGlossary(
        user_id = request.user.id,
        filename = title,
        numberofcount= 0,
        fileid=fileid,
        validFlg=1,
        createdDate = timezone.now(),
    )
    t1.save()
    message = "#Create Glossary is successful#"
    return redirect('glossary')

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
    keyid = request.GET['keyid']
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=keyid).first()
    glossary = []
    if ug != None:
        glib = GoogleApiLib()
        gauth = glib.getGoogleAuth()
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
            onedata['Category'] = val[2]
            glossary.append(onedata)
            i = i + 1
    return JsonResponse({"data": glossary})

@login_required
def saveGlossary(request, glossary_id):
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=glossary_id).first()
    glossaryjson = request.POST['glossaryjson']
    glib = GoogleApiLib()
    gauth = glib.getGoogleAuth()
    drive = GoogleDrive(gauth)
    fileid = ug.fileid
    gc = gspread.authorize(gauth.credentials)
    workbook = gc.open_by_key(fileid)
    worksheet = workbook.sheet1
    glossary = json.loads(glossaryjson)
    i = 2
    for val in glossary:
        worksheet.update('A'+str(i) +':C'+str(i), [[val['#WordName#'], val['#Translate#'], val['#Category#']]])
        i = i + 1
    if len(glossary) < ug.numberofcount:
        for j in range(ug.numberofcount - len(glossary)):
            worksheet.update('A'+str(i+j) +':C'+str(i+j), [['', '', '']])

    ug.numberofcount = len(glossary)
    ug.save()
    message = "#Update Glossary is successful#"
    return redirect('glossarydetail', glossary_id=glossary_id)

@login_required
def taglist(request):
    data = []
    for vals in UserTag.objects.filter(user=request.user.id):
        onedata = {}
        onedata['tag_id'] = vals.id
        onedata['tagname'] = vals.tagname
        onedata['backgroundcolor'] = vals.backgroundcolor
        onedata['textcolor'] = vals.textcolor
        data.append((onedata))

    return render(request, 'app/tag_list.html', {"data": data})

@login_required
def gettags(request):
    data = []
    for vals in UserTag.objects.filter(user=request.user.id):
        onedata = {}
        onedata['tag_id'] = vals.id
        onedata['tagname'] = vals.tagname
        onedata['backgroundcolor'] = vals.backgroundcolor
        onedata['textcolor'] = vals.textcolor
        data.append((onedata))

    return JsonResponse({"data": data})

@login_required
def deleteTag(request, tag_id):
    data = []
    WorkUserTag.objects.filter(tag_id=tag_id).delete()
    UserTag.objects.filter(id=tag_id).delete()
    return redirect('taglist')

@login_required
def getworksfortag(request):
    tag_id = request.GET.get("tag_id")
    data = []
    for vals in WorkUserTag.objects.filter(tag_id=tag_id):
        onedata = {}
        onedata['work_id'] = vals.work_id
        onedata['workTitle'] = vals.work.workTitle
        onedata['status'] = vals.work.status

        data.append((onedata))

    return JsonResponse({"data": data})
