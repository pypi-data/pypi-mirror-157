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
    dictpin = {"000": " ", "101": "ا", "102": "ب", "103": "پ", "104": "ت", "105": "ث", "106": "ج", "107": "چ",
               "108": "ح", "109": "خ", "165": "د", "111": "ذ", "112": "ز", "113": "ر", "114": "ژ", "115": "س",
               "116": "ش", "117": "ص", "118": "ض", "119": "ط", "120": "ظ", "121": "ع", "122": "غ", "123": "ف",
               "124": "ق", "125": "ک", "126": "گ", "127": "ل", "128": "م", "129": "ن", "169": "و", "131": "ه",
               "132": "ی", "201": "a", "202": "b", "203": "c", "204": "d", "205": "e", "206": "f", "207": "g",
               "208": "h", "209": "i", "265": "j", "211": "k", "212": "l", "213": "m", "214": "n", "215": "o",
               "216": "p", "217": "q", "218": "r", "219": "s", "267": "t", "221": "u", "222": "v", "223": "w",
               "224": "x", "225": "y", "226": "z",
               }
    dictnip = {" ": "000", "ا": "101", "ب": "102", "پ": "103", "ت": "104", "ث": "105", "ج": " 106", "چ": "107",
               "ح": "108", "خ": "109", "د": "165", "ذ": "111", "ز": "112", "ر": "113", "ژ": "114", "س": "115",
               "ش": "116", "ص": "117", "ض": "118", "ط": "119", "ظ": "167", "ع": "121", "غ": "122", "ف": "123",
               "ق": "124", "ک": "125", "گ": "126", "ل": "127", "م": "128", "ن": "129", "و": "169", "ه": "131",
               "ی": "132", "a": "201", "b": "202", "c": "203", "d": "204", "e": "205", "f": "206", "g": "207",
               "h": "208", "i": "209", "j": "265", "k": "211", "l": "212", "m": "213", "n": "214", "o": "215",
               "p": "216", "q": "217", "r": "218", "s": "219", "t": "267", "u": "221", "v": "222", "w": "223",
               "x": "224", "y": "225", "z": "226", "õ": "215"
               }
    t = kalameh
    try:
        int(kalameh[0])
        for i in range(0, len(kalameh) // 3):
            t = t.replace(kalameh[3 * i:(3 * i) + 3], dictpin[kalameh[3 * i:(3 * i) + 3]])
        return t
    except:
        for i in range(0, len(kalameh)):
            try:
                t = t.replace(kalameh[i], dictnip[kalameh[i]])
            except:
                if kalameh[i] == "[" or kalameh[i] == "(" or kalameh[i] == "{":
                    for k in range(i, len(kalameh)):
                        if kalameh[k] == "}" or kalameh[k] == "]" or kalameh[k] == ")":
                            for g in range(i, k):
                                t = t.replace(kalameh[i:k], "")
                            break
                        t = t.replace(kalameh[i], "")
                else:
                    t = t.replace(kalameh[i], "")

        return t
