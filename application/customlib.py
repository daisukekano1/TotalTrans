import requests
import json
import re
from pydrive.auth import GoogleAuth
from google.cloud import translate_v3 as translate
import os
from django.contrib.auth.decorators import login_required

GOOGLEAPI_KEY = 'AIzaSyD0CNmHW04AtsTTyYJSvcdf5i99MmPzUQ8'
project_id = "469662860857"
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

    def requestGoogleTranslation(text = "", glossary_id = "", lc_src = "", lc_tgt = ""):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(os.path.abspath(__file__)) +'\cred.json'
        client = translate.TranslationServiceClient()
        result = ""
        if glossary_id != "":
            glossary_path = client.glossary_path(project_id, 'us-central1', glossary_id)
            glossary_config = translate.types.TranslateTextGlossaryConfig(glossary=glossary_path)
            # glossary_config = translate.types.TranslateTextGlossaryConfig(glossary=glossary_path)
            response = client.translate_text(
                contents=[text],
                source_language_code= lc_src,
                target_language_code= lc_tgt,
                parent="projects/"+project_id+"/locations/us-central1",
                glossary_config=glossary_config
            )
            # response = translate.TranslateTextRequest(
            #     parent="projects/"+project_id+"/locations/us-central1",
            #     contents=[text],
            #     mime_type="text/plain",
            #     source_language_code= lc_src,
            #     target_language_code= lc_tgt,
            #     glossary_config=glossary_config
            # )
            for translation in response.glossary_translations:
                result = result + translation.translated_text
        else:
            response = client.translate_text(
                parent="projects/"+project_id+"/locations/"+project_location,
                contents=[text],
                mime_type="text/plain",
                source_language_code= lc_src,
                target_language_code= lc_tgt
            )
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
        response = client.get_supported_languages(parent="projects/"+project_id+"/locations/"+project_location)
        return response.languages

    def copyGlossaryToGoogleStrage(glossary_id):
        client = translate.TranslationServiceClient()
        parent="projects/"+project_id+"/locations/"+project_location
        name = client.glossary_path(project_id, gslocation, glossary_id)
        input_uri = "gs://"+gsbucketname+"/glossary.csv"
        gcs_source = {"input_uri": input_uri}
        input_config = {"gcs_source": gcs_source}
        return

    def createGlossaryInTransClient(glossary_id, lc_src, lc_tgt):
        client = translate.TranslationServiceClient()
        parent = "projects/"+project_id+"/locations/us-central1"
        name = client.glossary_path(project_id, "us-central1", glossary_id)
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
        request = {
            "parent": parent,
            "glossary":glossary
        }
        operation = client.create_glossary(request)
        return operation.metadata

    def getGlossary(glossary_id):
        client = translate.TranslationServiceClient()
        name = client.glossary_path(project_id, "us-central1", glossary_id)
        response = client.get_glossary(name)
        print(u"Glossary name: {}".format(response.name))
        print(u"Entry count: {}".format(response.entry_count))
        print(u"Input URI: {}".format(response.input_config.gcs_source.input_uri))
        return response

    def list_glossaries(glossary_id=""):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(os.path.abspath(__file__)) +'\cred.json'
        client = translate.TranslationServiceClient()
        parent = "projects/469662860857/locations/us-central1"
        # Iterate over all results
        request = {
            "parent": parent
        }
        for glossary in client.list_glossaries(request):
            print("Name: {}".format(glossary.name))
            print("Entry count: {}".format(glossary.entry_count))
            print("Input uri: {}".format(glossary.input_config.gcs_source.input_uri))

            # Note: You can create a glossary using one of two modes:
            # language_code_set or language_pair. When listing the information for
            # a glossary, you can only get information for the mode you used
            # when creating the glossary.
            for language_code in glossary.language_codes_set.language_codes:
                print("Language code: {}".format(language_code))
