from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from api_key import IBM_APIKEY, IBM_URL
import config
import logging


def translate(text):
    try:
        authenticator = IAMAuthenticator(config.IBM_APIKEY)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator
        )

        language_translator.set_service_url(config.IBM_URL)

        translation = language_translator.translate(
            text=text,
            model_id='en-ru').get_result()

        result = translation["translations"][0]["translation"]

        return result
        # return text
    except BaseException as be:
        logging.error(f"translator: {be}")


