from googletrans import Translator

translator = Translator()

def translate(text):
    try:
        return translator.translate(text, dest="ru").text
    except:
        return text