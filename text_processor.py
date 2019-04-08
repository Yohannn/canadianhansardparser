import os
import sys
import argparse
import re
import csv
import json
import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from collections import defaultdict

# data to be exported after parsing.
data_mp_count = {}
data_mp_terms = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
data_subtopic_terms = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
data_date_terms = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

termtype_lst = ["religious", "anxiety", "optimistic", "terror"]

scan_limit  = 10
# location of the data - to be modified accordingly.
# temp location for testing.
data_dir = '/Users/Yohan/Desktop/Course/csc494-project/data/lipad'
# '/w/256/dilipad/yohan/lipad/lipad' - for in cs server.
# /Users/Yohan/Desktop/Course/csc494-project/data/lipad - //-/ for local directory.

# lemmatizer to be used for counting.s
lemmatizer = WordNetLemmatizer()

def create_regex(t_filename):
    """
    This function reads a file that contains a list of terms that we wish to put
    into regular expression.
    Then return compiled pattern of regular expression.
    
    t_filename: name of the file with list of words to read. 
                This file must be inside the directory 'terms' that is in the 
                same location as this program. 
    """
    abs_filepath = sys.path[0] + '/terms/' + t_filename 
    regex_words = ""
    with open(abs_filepath) as tf:

        for line in tf:

            word = line.strip('\n')

            # flag for optimistic words starting with 
            if word[-1] == '*':
                word = '\\b' + word + '\\w*'

            regex_words += (word + '|')
    
    regex_words = "(?<=\\b)(" + regex_words[:-1] + ")(?=\\b)"

    # return re.compile(regex_words, flags=re.IGNORECASE)
    return regex_words

# Compilation of regex for list of words.
pattern_reli = re.compile(create_regex('religious.txt'))
pattern_anx = re.compile(create_regex('anxiety.txt'))
pattern_opt = re.compile(create_regex('optimistic.txt'))
pattern_dhs = re.compile(create_regex('DHS.txt'))

def find_terms(speech_text, name, party, riding, date, subtopic):
    """
    @param str speech_text: speech text obtained from csv file.
    This function does the following:
        1) Convert every words in speech_text into standard form using NLTK WordNetLemmatizer.
        2) Use regular expression to count the lists of words of interest.
    """

    def get_wn_pos(treebank_tag):
        """
        Given word treebank_tag obtained from pos_tag, return equivalent WordNet pos tag.
        """

        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN 
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else: return wordnet.NOUN 
        
    
    total_words = len(speech_text.split())
    # Create new lemmatized version of speech_text.
    # tokenize into words
    tokens = [word for sent in nltk.sent_tokenize(speech_text) for word in nltk.word_tokenize(sent)] 
     
    # remove stopwords for efficiency. //-/
    stop_eng = stopwords.words('english')
    tokens = [token for token in tokens if token not in stop_eng]

    # Use POS to put in lemmatize the entire text.
    tokens_tagged = nltk.pos_tag(tokens)
    tokens_lemmatized = [lemmatizer.lemmatize(word, get_wn_pos(tb_tag)) for word, tb_tag in tokens_tagged]
    preprocessed_text = ' '.join(tokens_lemmatized)

    # Count religious, anxiety, optimistics, DHS terms.
    reli_found = pattern_reli.findall(preprocessed_text)
    anxie_found = pattern_anx.findall(preprocessed_text)
    opt_found = pattern_opt.findall(preprocessed_text)
    dhs_found = pattern_dhs.findall(preprocessed_text)
    words_found = [reli_found, anxie_found, opt_found, dhs_found]

    i = 0
    while (i < len(termtype_lst)):
        term_type = termtype_lst[i]
        term_found = words_found[i]

        update_dict_terms(name, subtopic, date, term_type, term_found)
      
        i += 1

    relig_count = len(reli_found)
    anxie_count = len(anxie_found)
    opt_count = len(opt_found)
    dhs_count = len(dhs_found)

    # count words used for each term category and update dictionary according to requirements.
    updatedict_mp_count(name, party, riding, relig_count, anxie_count, opt_count, dhs_count, total_words)
    # by date
    

    # return total_words, relig_count, anxie_count, opt_count, dhs_count


def update_dict_terms(name, subtopic, date, term_type, word_lst):
    """
    populate them with words.

    @name str: name of an mp.
    @term_type str: one of "religious", "anxiety", "optimistic", "terror".
    @words_found list(str): list of words found from speech text.

    {<name>: {"religious": {<word1>: 3, <word2>: 3},
             "anxiety": {<word1>: 3, <word2>: 3}
             "optimistic": {<word1>: 3, <word2>: 3}
             "terror": {<word1>: 3, <word2>: 3}}
    }
    """
    global data_mp_terms
    global data_date_terms
    global data_subtopic_terms
    
    for each_word in word_lst:
        data_mp_terms[name][term_type][each_word] += 1
        data_date_terms[date][term_type][each_word] += 1
        data_subtopic_terms[subtopic][term_type][each_word] += 1

def updatedict_mp_count(name, party, riding, reli_count, anxi_count, opt_count, dhs_count, total_count):
    """
    Add new entry or update the entries by adding counts.
    """
    # updating mps_count.json
    global data_mp_count
    
    if name not in data_mp_count:
        data_mp_count[name] = {'party': party, "riding": riding, 'religious': reli_count, 'anxiety': anxi_count, 
                            'optimistic': opt_count, 'terror': dhs_count, 'total words': total_count}
    else:
        data_mp_count[name]['religious'] += reli_count
        data_mp_count[name]['anxiety'] += anxi_count
        data_mp_count[name]['optimistic'] += opt_count
        data_mp_count[name]['terror'] += dhs_count
        data_mp_count[name]['total words'] += total_count
        

    # updating name_opid.json
    # if name not in nameopid_dict:
    #     nameopid_dict[name] = opid
    



def main(flag, scope):
    """
    int years_back: Gives scope for how much data is to be processed.
                    years_back == 10 processes last 10 years of data i.e. from 2018 to 2008
    Extract and store relevant entries in csv and export in JSON. 
    Following is the structure of two jsons files to be exported.
    > mps_count.json:
    {<name>: {party: <str>, religious: <int>, anxiety: <int>, DHS: <int>}

    > name_opid.json:
    {<name of mp>: opid}
    
    """
    for dirName, subdirs, files in os.walk(data_dir):

        # Accessing the most recent data frist.            
        subdirs.sort(key=lambda x: int(x), reverse=True)
        files.sort(reverse=True)
        
        
        if os.path.basename(dirName) == 'lipad':

            # option1: scanning specific year.
            if flag == 0:
                subdirs[:] = [str(scope)]
            # option2: scanning last x years.
            else: 
                subdirs[:] = subdirs[:scope]

        # extract the full file names.
        for filename in files:

            date = filename[:-4] 

            # Progress checker.
            full_filename = os.path.join(dirName, filename)
            print("Processing file: {}.".format(full_filename))

            with open(full_filename, encoding='utf-8') as proc_file:
    
                csv_reader = csv.reader(proc_file)

                next(csv_reader) #skips the fist line.                
                for row in csv_reader:
                                
                    speaker_opid = row[4] 

                    if speaker_opid == "":
                        continue

                    speaker_name = row[13]
                    speaker_party = row[11]
                    speaker_riding = row[12]
                    speech_text = row[10]
                    subtopic = row[8]

                    find_terms(speech_text, speaker_name, speaker_party, speaker_riding, date, subtopic)

    # export in json.
    if flag == 0:
        scope_marker = 's_' + str(scope)
    else: # if flag == 1:
        scope_marker = 'l_' + str(scope)

    jsonData_dir = os.getcwd() + '/processedData/'
    if not os.path.exists(jsonData_dir):
        os.makedirs(jsonData_dir)
    
    with open(jsonData_dir + 'mps_count_' + scope_marker + '.json', 'w') as fout:
        json.dump(data_mp_count, fout, sort_keys=True, indent=4, separators=(',', ': '))

    with open(jsonData_dir + 'mps_terms_' + scope_marker + '.json', 'w') as fout:
        json.dump(data_mp_terms, fout, sort_keys=True, indent=4, separators=(',', ': '))

    with open(jsonData_dir + 'date_terms_' + scope_marker + '.json', 'w') as fout:
        json.dump(data_date_terms, fout, sort_keys=True, indent=4, separators=(',', ': '))
    
    with open(jsonData_dir + 'subtopic_terms_' + scope_marker + '.json', 'w') as fout:
        json.dump(data_subtopic_terms, fout, sort_keys=True, indent=4, separators=(',', ': '))

    # with open(jsonData_dir + 'mps_opid_' + scope_marker + '.json', 'w') as fout:
    #     json.dump(name_opid, fout, sort_keys=True, indent=4, separators=(',', ': '))

        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='This is a text parsing program for Canadian Hansard Data in csv format')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-s", "--specific", help="specific year to scan data.", type=int)
    group.add_argument("-l", "--last", 
                        help="scans past years specified within scan limit. To scan more than current scan limit, modify scan_limit.", type=int)

    args = parser.parse_args()

    if args.last is None:
        # 0  for specific.
        flag = 0
        scope = args.specific
    else:
        # 1 for last x years option.
        flag = 1
        scope = args.last

    main(flag, scope)
