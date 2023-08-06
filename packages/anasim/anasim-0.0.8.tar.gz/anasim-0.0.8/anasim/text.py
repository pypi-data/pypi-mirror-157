import re
import string
def clean_text(text):
    text = text.lower()
    text = re.sub(';' , ' ; ' , text)
    text = re.sub(',' , ' , ' , text)
    text = re.sub('-' ,  ' - ' , text)
    text = re.sub('\d','',text) #odstranění čísel
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    return text


