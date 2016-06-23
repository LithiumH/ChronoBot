import distance
import string
from stop_words import get_stop_words

stop_words = get_stop_words('english')
exclude = set(string.punctuation)

def similarity(mystring1, mystring2):
    mystring1 = ''.join(ch for ch in mystring1 if ch not in exclude)
    mystring2 = ''.join(ch for ch in mystring2 if ch not in exclude)
    list1 = mystring1.split(" ")
    list2 = mystring2.split(" ")
    for word in list1:
        if word in stop_words:
            list1.pop(word)
    for word in list2:
        if word in stop_words:
            list2.pop(word)
    return distance.levenshtein(list1, list2, normalized=True)
