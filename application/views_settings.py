from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pprint, os
from application.models import UserGlossary, Language
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder

folder_id = '1z22K4kWicecG81sCPUOgnL1zwlOFKt5D'
message = ""
@login_required
def glossary(request):
    glossary = UserGlossary.objects.filter(user=request.user.id).all()
    langs = Language.objects.filter(validFlag=1).extra(select = { 'displaylang' : request.user.userLanguage}).values('lc','language','flagId', 'displaylang').order_by('displaylang')
    data = {
        'glossary' : glossary,
        'message' : message,
        'langs' : langs
    }
    return render(request, 'app/settings_glossary.html', data)

def createGlossary(request):
    gauth = getGoogleAuth()
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
    return redirect('glossary')

def updateGlossary(request):
    gauth = getGoogleAuth()
    gc = gspread.authorize(gauth.credentials)

    # スプレッドシートのIDを指定してワークブックを選択
    workbook = gc.open_by_key(f['id'])
    worksheet = workbook.sheet1

    # A1のセルに入力
    worksheet.update_acell('A1', 'Hello World!')

    # 2行目の1~3列目に入力
    cell_list = worksheet.range(2, 1, 2, 3)
    cell_list[0].value = '連番'
    cell_list[1].value = '名前'
    cell_list[2].value = '電話番号'

    # スプレッドシートを更新
    worksheet.update_cells(cell_list)

    return render(request, 'app/settings_glossary.html')

@login_required
def glossarydetail(request, glossary_id):
    ug = UserGlossary.objects.filter(user=request.user.id).filter(id=glossary_id).first()
    glossary = {}
    if ug != None:
        gauth = getGoogleAuth()
        gc = gspread.authorize(gauth.credentials)
        workbook = gc.open_by_key(ug.fileid)
        worksheet = workbook.sheet1
        wklist = worksheet.get_all_values()
        glossary = json.dumps(wklist, cls=DjangoJSONEncoder)
    data = {
        'userglossary' : ug,
        'glossary' : glossary
    }
    return render(request, 'app/settings_glossarydetail.html', data)

@login_required
def tag(request):
    return render(request, 'app/settings_tag.html')

def getGoogleAuth():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth