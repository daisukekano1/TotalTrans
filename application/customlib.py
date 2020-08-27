import requests
import json
import re
from pydrive.auth import GoogleAuth
from google.cloud import translate_v3 as translate
import os
from django.contrib.auth.decorators import login_required

GOOGLEAPI_KEY = 'AIzaSyD0CNmHW04AtsTTyYJSvcdf5i99MmPzUQ8'
project_id = "fifth-octane-287007"
project_location = "global"
gsbucketname = "honyakusiteglossary"
gslocation = "asia"

class GoogleApiLib:

    def requestGoogleTranslation2(originalText, lc_src, lc_tgt):
        url = "https://translation.googleapis.com/language/translate/v2"
        url += "?key=" + GOOGLEAPI_KEY

        url += "&q=" + originalText
        url += "&source=" + lc_src
        url += "&target=" + lc_tgt

        rr = requests.get(url)
        unit_aa = json.loads(rr.text)
        result = unit_aa["data"]["translations"][0]["translatedText"]
        return result

    def requestGoogleTranslation(text, glossary_id, lc_src, lc_tgt):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(os.path.abspath(__file__)) +'\cred2.json'
        client = translate.TranslationServiceClient()
        ret = GoogleApiLib.createGlossaryInTransClient(glossary_id, lc_src, lc_tgt)
        glossary = client.glossary_path(project_id, "asia", glossary_id)
        glossary_config = translate.types.TranslateTextGlossaryConfig(glossary=glossary)
        response = client.translate_text(
            parent="projects/"+project_id+"/locations/"+project_location,
            contents=[text],
            mime_type="text/plain",
            source_language_code= lc_src,
            target_language_code= lc_tgt,
            glossary_config=glossary_config
        )
        result = ""
        for translation in response.translations:
            result = result + translation.translated_text
        return result

    def getGoogleAuth(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return gauth

    def get_supported_languages(self):
        client = translate.TranslationServiceClient()
        response = client.get_supported_languages(parent="projects/"+project_id+"/locations/global")
        return response.languages

    def copyGlossaryToGoogleStrage(glossary_id):
        client = translate.TranslationServiceClient()
        parent="projects/"+project_id+"/locations/global"
        name = client.glossary_path(project_id, "global", glossary_id)
        input_uri = "gs://"+gsbucketname+"/glossary.csv"
        gcs_source = {"input_uri": input_uri}
        input_config = {"gcs_source": gcs_source}
        return

    def createGlossaryInTransClient(glossary_id, lc_src, lc_tgt):
        client = translate.TranslationServiceClient()
        parent = "projects/"+project_id+"/locations/global"
        name = client.glossary_path(project_id, "global", glossary_id)
        source_lang_code = lc_src
        target_lang_code = lc_tgt
        language_codes_set = translate.types.Glossary.LanguageCodesSet(
            language_codes=[source_lang_code, target_lang_code]
        )
        input_uri = "gs://"+gsbucketname+"/"+glossary_id+".csv"
        gcs_source = translate.types.GcsSource(input_uri=input_uri)
        input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)
        glossary = translate.types.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )
        operation = client.create_glossary(parent, glossary)
        return operation.metadata

    def getGlossary(glossary_id):
        client = translate.TranslationServiceClient()
        name = client.glossary_path(project_id, "global", glossary_id)
        response = client.get_glossary(name)
        return response