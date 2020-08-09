#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gengo import Gengo
from application.models import Language

GENGO_SANDBOX_FLG = True
GENGO_URL = 'http://api.sandbox.gengo.com/v2/translate/jobs'
GENGO_PUBLIC_KEY = 'kq|NlLCoLWWaal-LTbdyFV$zXIbomiu|vPlBfevP6HGeJXXdTpgBN2JYkAMCHJh|'
GENGO_PRIVATE = 'vuqb9x2yEEL~WD0SPbe3f~RVU[e}6|Y$ZwAyo2Qu$slZ}gS(p}q|3iIfmm[hqHT9'

gengo = Gengo(
    public_key=GENGO_PUBLIC_KEY,
    private_key=GENGO_PRIVATE,
    sandbox=GENGO_SANDBOX_FLG,
    debug=True
)
languageMatrix = gengo.getServiceLanguageMatrix()
for lang in Language.objects.all():
    if lang['lc'] in languageMatrix['response']['sources']:
        t2 = Language.objects.filter(lc=lang['lc']).first()
        t2.validFlag = 1
        t2.save()
    else:
        t2 = Language.objects.filter(lc=lang['lc']).first()
        t2.validFlag = 0
        t2.save()
