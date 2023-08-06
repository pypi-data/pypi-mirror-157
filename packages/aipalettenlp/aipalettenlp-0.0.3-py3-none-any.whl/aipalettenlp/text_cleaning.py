import re
import nltk
import demoji
import emoji
nltk.download('stopwords')

def hashtags(text):
    '''extract a list of hashtags'''
    hashtags_list = []
    split_text = re.findall(r"\w+|#\w+|@\w+|[!\"$%&'()*+,-./:;<=>?[\]^`{|}~]", text) #split based on punctuation and whitespace 
    
    # remove all the hashtags at the end of the caption
    for part in reversed(split_text): 
        if part.startswith('#'):
            split_text.remove(part)
            hashtags_list.append(part[1:])
            continue
        else:      
            break
    return {"hashtags":list(reversed(hashtags_list))}
    
# ----------------------------------------------------
# Utility functions 
def replace_hashtags(text):
    '''remove the hashtags '#' within the main caption''' 
    new_list = []
    split_text = re.findall(r"\w+|#\w+|@\w+|[!\"$%&'()*+,-./:;<=>?[\]^`{|}~]", text) #split based on punctuation and whitespace 
    
    # remove all the hashtags at the end of the caption
    for part in reversed(split_text): 
        if part.startswith('#'):
            split_text.remove(part)
            continue
        else:      
            break
    # remove '#' from the main caption and join the elements together
    for part in split_text:
        if part.startswith('#'):
            new_list.append(part[1:])
        else:
            new_list.append(part)
    
    return ' '.join(new_list)


def replace_usernames(text):
    '''define a function to detect mentions and replace it with <username>'''
    cleanedText = re.sub(r'(?<![@\w])@(\w{1,30})',"<username>",text)
    return cleanedText


SINGULAR_RULES = [
    ['(?i)(.)ae$' , '\\1a'],
    ['(?i)(.)itis$' , '\\1itis'],
    ['(?i)(.)eaux$' , '\\1eau'],
    ['(?i)(quiz)zes$' , '\\1'],
    ['(?i)(matr)ices$' , '\\1ix'],
    ['(?i)(vert|ind)ices$' , '\\1ex'],
    ['(?i)^(ox)en' , '\\1'],
    ['(?i)(alias|status)es$' , '\\1'],
    ['(?i)([octop|vir])i$' , '\\1us'],
    ['(?i)(cris|ax|test)es$' , '\\1is'],
    ['(?i)(shoe)s$' , '\\1'],
    ['(?i)(o)es$' , '\\1'],
    ['(?i)(bus)es$' , '\\1'],
    ['(?i)([m|l])ice$' , '\\1ouse'],
    ['(?i)(x|ch|ss|sh)es$' , '\\1'],
    ['(?i)(m)ovies$' , '\\1ovie'],
    ['(?i)ombies$' , '\\1ombie'],
    ['(?i)(s)eries$' , '\\1eries'],
    ['(?i)([^aeiouy]|qu)ies$' , '\\1y'],
    # Certain words ending in -f or -fe take -ves in the plural (lives, wolves).
    ["([aeo]l)ves$", "\\1f"],
    ["([^d]ea)ves$", "\\1f"],
    ["arves$", "arf"],
    ["erves$", "erve"],
    ["([nlw]i)ves$", "\\1fe"],   
    ['(?i)([lr])ves$' , '\\1f'],
    ["([aeo])ves$", "\\1ve"],
    ['(?i)(sive)s$' , '\\1'],
    ['(?i)(tive)s$' , '\\1'],
    ['(?i)(hive)s$' , '\\1'],
    ['(?i)([^f])ves$' , '\\1fe'],
    
    ['(?i)(^analy)ses$' , '\\1sis'],
    ['(?i)((a)naly|(b)a|(d)iagno|(p)arenthe|(p)rogno|(s)ynop|(t)he)ses$' , '\\1\\2sis'],
    ['(?i)(.)opses$' , '\\1opsis'],
    ['(?i)(.)yses$' , '\\1ysis'],
    ['(?i)(h|d|r|o|n|b|cl|p)oses$' , '\\1ose'],
    ['(?i)(fruct|gluc|galact|lact|ket|malt|rib|sacchar|cellul)ose$' , '\\1ose'],
    ['(?i)(.)oses$' , '\\1osis'],
    
    ['(?i)([ti])a$' , '\\1um'],
    ['(?i)(n)ews$' , '\\1ews'],
    ['(?i)(?<![s|u|\'])s$' , ''],
];
SINGULAR_UNINFLECTED = ["bison", "bream", "breeches", "britches", "carp", "chassis", "clippers", "cod", "contretemps", "corps", "debris", "diabetes", "djinn", "eland", "elk", "flounder", "gallows", "graffiti", "headquarters", "herpes", "high-jinks", "homework", "innings", "jackanapes", "mackerel", "measles", "mews", "mumps", "news", "pincers", "pliers", "proceedings", "rabies", "salmon", "scissors", "series", "shears", "species", "swine", "trout", "tuna", "whiting", "wildebeest"]
SINGULAR_UNCOUNTABLE = ["advice", "bread", "butter", "cheese", "electricity", "equipment", "fruit", "furniture", "garbage", "gravel", "happiness", "information", "ketchup", "knowledge", "love", "luggage", "mathematics", "mayonnaise", "meat", "mustard", "news", "progress", "research", "rice", "sand", "software", "understanding", "water"]
SINGULAR_IE = ["algerie", "auntie", "beanie", "birdie", "bogie", "bombie", "bookie", "cookie", "cutie", "doggie", "eyrie", "freebie", "goonie", "groupie", "hankie", "hippie", "hoagie", "hottie", "indie", "junkie", "laddie", "laramie", "lingerie", "meanie", "nightie", "oldie", "^pie", "pixie", "quickie", "reverie", "rookie", "softie", "sortie", "stoolie", "sweetie", "techie", "^tie", "toughie", "valkyrie", "veggie", "weenie", "yuppie", "zombie"]
SINGULAR_IRREGULAR = {
    "men" : "man",
    "people" : "person",
    "children" : "child",
    "sexes" : "sex",
    "moves" : "move",
    "teeth" : "tooth",
    "geese" : "goose",
    "feet" : "foot",
    "zoa" : "zoon",
    "atlantes" : "atlas", 
    "atlases" : "atlas", 
    "beeves" : "beef", 
    "brethren" : "brother", 
    "children" : "child", 
    "corpora" : "corpus", 
    "corpuses" : "corpus", 
    "kine" : "cow", 
    "ephemerides" : "ephemeris", 
    "ganglia" : "ganglion", 
    "genii" : "genie", 
    "genera" : "genus", 
    "graffiti" : "graffito", 
    "helves" : "helve",
    "leaves" : "leaf",
    "loaves" : "loaf", 
    "monies" : "money", 
    "mongooses" : "mongoose", 
    "mythoi" : "mythos", 
    "octopodes" : "octopus", 
    "opera" : "opus", 
    "opuses" : "opus", 
    "oxen" : "ox", 
    "penes" : "penis", 
    "penises" : "penis", 
    "soliloquies" : "soliloquy", 
    "testes" : "testis", 
    "trilbys" : "trilby", 
    "turves" : "turf", 
    "numena" : "numen", 
    "occipita" : "occiput",
    "smoothies": "smoothie", # food irregulars 
    "brownies": "brownie"
}
EXCEPTIONS = ["cookies", "fries", "chips", "crisps", "noodles", "crackers", "ramen", "rooibos"]
# Prepositions are used to solve things like
# "mother-in-law" or "man-at-arms"
PLURAL_PREPOSITIONS = ["about", "above", "across", "after", "among", "around", "at", "athwart", "before", "behind", "below", "beneath", "beside", "besides", "between", "betwixt", "beyond", "but", "by", "during", "except", "for", "from", "in", "into", "near", "of", "off", "on", "onto", "out", "over", "since", "till", "to", "under", "until", "unto", "upon", "with"]


def singular(word, custom={}):
    if word in custom.keys():
        return custom[word]
    
    # Recursion of compound words (e.g. mothers-in-law). 
    if "-" in word:
        words = word.split("-")
        if len(words) > 1 and words[1] in PLURAL_PREPOSITIONS:
            return singular(words[0], custom)+"-"+"-".join(words[1:])
    lower_cased_word = word.lower()
    
    if lower_cased_word in EXCEPTIONS:
        return word
    
    for w in SINGULAR_UNINFLECTED:
        if w.endswith(lower_cased_word):
            return word
    for w in SINGULAR_UNCOUNTABLE:
        if w.endswith(lower_cased_word):
            return word
    for w in SINGULAR_IE:
        if lower_cased_word.endswith(w+"s"):
            return w
    for w in SINGULAR_IRREGULAR.keys():
        match = re.search('('+w+')$',word, re.IGNORECASE)
        if match:
            return re.sub(
                '(?i)'+w+'$', 
                SINGULAR_IRREGULAR[w], word)
    for rule in range(len(SINGULAR_RULES)):
        match = re.search(SINGULAR_RULES[rule][0], word, re.IGNORECASE)
        if match:
            groups = match.groups()
            for k in range(0,len(groups)):
                if groups[k] == None:
                    SINGULAR_RULES[rule][1] = SINGULAR_RULES[rule][1].replace('\\'+str(k+1), '')
            return re.sub(
                SINGULAR_RULES[rule][0], 
                SINGULAR_RULES[rule][1], word)
    return word

#remove_emoji function is not working
def remove_emoji(text, language=None):
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00003000-\U0000303f"  # japanese punctuation  
            u"\U0000ffe0-\U0000ffef"  # japanese punctuation part2
            u"\U00002700-\U000027BF"  # Dingbats 2700—27BF
            u"\U00002600-\U000026BF"  # misc. symbols
            u"\U0000FF00-\U0000FF0F"  # fullwidth punctuations
            u"\U000025A0-\U000025FF"  # blocks                 
                            "#+"
                            "&+"
                            "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', demoji.replace(text))
    return text


def remove_punctuations(text):
    text = re.sub(r'[^\w\s]','', text)
    return text


def remove_numbers(text):
    ''' Removes numbers and any characters inbetween numbers'''
    text = re.sub("\d\w*\d|\d*$|^\d*","", text) 
    return text
    
    
def remove_stopwords(text, language, warning=True):
    try:
        stopwords_set = set(nltk.corpus.stopwords.words(language))
        filtered_words = [word.lower() for word in text.split() if word.lower() not in stopwords_set]
        text = " ".join(filtered_words)
        return text
    
    except OSError:
        if warning:
            print("Language stopwords database not found! Stopwords not removed.")
        return spacing_fix(text)

    
def spacing_fix(text):
    text = " ".join(text.split())
    return text


def delete_all_measurements(text):
    measurement_list = ["ml", "xl", "l", "s", "m", "kg", "g", "r", "lb", "oz", "large", "small", "medium", "xxl", "jumbo", "tiny", "big packet", "sachet", "gm", "litre", "liter", "family-sized", "family-size"]
    measurement_variant_list = []
        
    for measurement in measurement_list:
        measurement_variant_list.append(measurement)
        measurement_variant_list.append(measurement.upper())
        measurement_variant_list.append(measurement.title())
    measurement_variant_list = sorted(measurement_variant_list, key=len, reverse=True)
    
    for search_term in measurement_variant_list:
        text = re.sub(f"^\s*{search_term}\s|\s{search_term}\s*$|^{search_term}$","", text)
        text = re.sub(f"\s{search_term}\s"," ", text)
    return text


def cleantext(text, language):
    
    # Remove irrelevant components of text
    text = replace_hashtags(text)
    text = replace_usernames(text)
    text = remove_emoji(text)
    text = remove_punctuations(text)
    text = remove_numbers(text)
    text = delete_all_measurements(text)
    text = singular(text)
    text = remove_stopwords(text,language)
    
    # Filter text that are too short
    if len(text)<=2:
        return ''
    else:
        return {"clean_text":text}


def text_length(text,language):
    textobj = cleantext(text,language)
    return {"text_length":len(textobj["clean_text"])}