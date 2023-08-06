import pyttsx3
import requests


def speak(word,a,b):
    engine = pyttsx3.init()


    rate = engine.getProperty('rate')
    volume = engine.getProperty('volume')
    engine.setProperty('rate', rate+a)
    engine.setProperty('volume', volume+b)

    engine.say(word)
    engine.runAndWait()
def fanyi_speak(word,a,b):
    #a = "hello"

    string = word#str(input("请输入一段要翻译的文字："))
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i':string
    }
    url = "http://fanyi.youdao.com/translate"
    r = requests.get(url,params=data)
    result = r.json()
    #print(result)
    translate_result = result['translateResult'][0][0]["tgt"]
    print(translate_result)
    engine = pyttsx3.init()


    rate = engine.getProperty('rate')
    volume = engine.getProperty('volume')
    engine.setProperty('rate', rate+a)
    engine.setProperty('volume', volume+b)

    engine.say(translate_result)
    engine.runAndWait()