import requests

def fanyi(word):

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