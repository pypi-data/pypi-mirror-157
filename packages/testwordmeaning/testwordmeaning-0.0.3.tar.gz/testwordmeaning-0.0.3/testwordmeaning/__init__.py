import requests
from bs4 import BeautifulSoup

def Word(kalameh):
    try:
        return "\n" + " " + "\n" + "واژه‌ای یافت نشد." + "\n" != BeautifulSoup(
            requests.get("https://vajehyab.com/?q=" + str(kalameh)).text, "html.parser").find("div",
                                                                                              class_="search-container").get_text()
    except:
        if kalameh != " " and "":
            print("Check your internet connection")
            return False
        else:
            return False


def list_words(list_kalameh):
    p = 0
    if type(list_kalameh) != list:
        list_kalameh = list(str(list_kalameh))
    for i in range(0, len(list_kalameh)):
        if Word(list_kalameh[i - p]) == False:
            list_kalameh.pop(i - p)
            p += 1

    return list_kalameh


def Pin(kalameh):
    dictpin = {
        "00": " ",
        "01": "ا",
        "02": "ب",
        "03": "پ",
        "04": "ت",
        "05": "ث",
        "06": "ج",
        "07": "چ",
        "08": "ح",
        "09": "خ",
        "65": "د",
        "11": "ذ",
        "12": "ز",
        "13": "ر",
        "14": "ژ",
        "15": "س",
        "16": "ش",
        "17": "ص",
        "18": "ض",
        "19": "ط",
        "20": "ظ",
        "21": "ع",
        "22": "غ",
        "23": "ف",
        "24": "ق",
        "25": "ک",
        "26": "گ",
        "27": "ل",
        "28": "م",
        "29": "ن",
        "69": "و",
        "31": "ه",
        "32": "ی",
    }
    dictnip = {
        " ":"00",
        "ا":"01",
        "ب":"02",
        "پ":"03",
        "ت":"04",
        "ث":"05",
        "ج":"06",
        "چ":"07",
        "ح":"08",
        "خ":"09",
        "د":"65",
        "ذ":"11",
        "ز":"12",
        "ر":"13",
        "ژ":"14",
        "س":"15",
        "ش":"16",
        "ص":"17",
        "ض":"18",
        "ط":"19",
        "ظ":"67",
        "ع":"21",
        "غ":"22",
        "ف":"23",
        "ق":"24",
        "ک":"25",
        "گ":"26",
        "ل":"27",
        "م":"28",
        "ن":"29",
        "و":"69",
        "ه":"31",
        "ی":"32",
    }
    t = kalameh
    try:
        int(kalameh)
        for i in range(0,len(kalameh)//2):
            t = t.replace(kalameh[2 * i:2*i+2], dictpin[kalameh[2 * i:2*i+2]])
        return t
    except:
        for i in range(0,len(kalameh)):
            try:t = t.replace(kalameh[i], dictnip[kalameh[i]])
            except: pass
        return t