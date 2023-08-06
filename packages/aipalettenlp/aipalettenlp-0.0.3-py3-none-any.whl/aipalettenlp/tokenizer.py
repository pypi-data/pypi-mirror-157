import nltk
nltk.download('stopwords')
import jieba 

from pythainlp.ulmfit import *
from fastai.text import *
from nltk.tokenize import word_tokenize
from janome.tokenizer import Tokenizer as jp_Tokenizer
from pykotokenizer import KoSpacing
from pyvi import ViTokenizer,ViPosTagger
from somajo import SoMaJo

tokenizer_languages = ['english','french','german','italian','portuguese','spanish','swedish',
                       'turkish','russian','mandarin','thai','japanese','korean','vietnamese']
# use nltk word_tokenize
nltk_lang = ['english', 'french', 'italian', 'portuguese',
             'spanish', 'swedish', 'turkish', 'russian']

# use tokenizers from other packages
nonnltk_lang = ['mandarin', 'thai', 'japanese', 'korean', 'vietnamese','german']

jt = jp_Tokenizer()
kt = KoSpacing()

def tokenize(text,language):
    tokenize_text = ''

    if language == 'mandarin':
        tokenize_text = jieba.cut(text, cut_all=False)
        try:
            tokenize_text = [str(word) for word in tokenize_text]
        except Exception as e:
            print(text)
            print(tokenize_text)
            raise e
            
    elif language == 'thai':
        tt = Tokenizer(tok_func = ThaiTokenizer, lang = 'th', pre_rules = pre_rules_th, post_rules=post_rules_th)
        tokenizer = TokenizeProcessor(tokenizer=tt, chunksize=10000, mark_fields=False)
        tokenize_text = tokenizer.tokenizer.process_text(text, ThaiTokenizer)
        
    elif language == 'japanese':
        tokenize_text = [token.node.surface for token in jt.tokenize(text)]
        
    elif language == "korean":
        tokenize_text = kt(text).replace('.','').split(' ')
        
    elif language == "vietnamese":
        tokenize_text = ViPosTagger.postagging(ViTokenizer.tokenize(text))[0]

    elif language == "german":
        tokenizer = SoMaJo("de_CMC", split_camel_case=True)
        sentences = tokenizer.tokenize_text(text)
        tokenize_text = []
        for sentence in sentences:
            for token in sentence:
                    tokenize_text.append(token)
        
    else:
        tokenize_text = word_tokenize(text.lower())

    return {"tokenized_text":tokenize_text}