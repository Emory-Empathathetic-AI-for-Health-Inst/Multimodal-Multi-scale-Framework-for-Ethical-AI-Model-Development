import pandas as pd
import numpy as np
import re
import dateparser
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')
tqdm.pandas()


## removal of duplicate sentences within an interval
def remove_duplicate_sentences_within_interval(txt):
    txt = txt.replace('||', '|')
    sents = txt.split('|')
    sents = [" ".join(s.split()) for s in sents]
    sents = [s.lstrip(' ').rstrip(' ') for s in sents]
    sents = [re.sub(r'<[^>]*>', '', s) for s in sents]  ## removing text between < and >
    ## removal of duplicate sentences
    sents_w_no_duplicates = []
    for s in sents:
        new_sents = s.split('.')
        new_sents = [s.lstrip(' ').rstrip(' ') for s in new_sents]
        for ss in new_sents:
            if ss not in sents_w_no_duplicates:
                sents_w_no_duplicates.append(ss)
    return '|'.join(sents_w_no_duplicates)


## removal of duplicate sentences across intervals
def remove_duplicate_sentences_across_intervals(curated):
    '''
    This function removes duplicate sentences across interval for a patient based on the following criteria:
        - retains a sentence in 3 consecutive intervals
        - i.e. removing duplicate sentences across intervals - it sees across all intervals for patient and retains a sentence only in the first appeared interval and two consecutive intervals, removes in all future intervals
    '''
    curated['TEXT_processed'] = curated['TEXT'].copy()
    pats = curated['MRN'].unique()
    for p in pats:
        temp = curated[curated['MRN'] == p]
        ind = temp.index.tolist()
        
        sents_in_intervals = {}

        # find where each sentence appears
        for i in ind:
            txt = curated.loc[i, 'TEXT']
            if pd.isna(txt):
                continue
            sents = txt.split('|')
            sents = [s.strip() for s in sents]
            for s in sents:
                if s not in sents_in_intervals:
                    sents_in_intervals[s] = []
                sents_in_intervals[s].append(i)

        # find where to keep each sentence
        sents_retain_intervals = {}
        for s, appearances in sents_in_intervals.items():
            keep = []
            if appearances:
                keep.append(appearances[0])
                count = 1
                for j in range(1, len(appearances)):
                    if appearances[j] == appearances[j - 1] + 1 and count < 3:
                        keep.append(appearances[j])
                        count += 1
                    else:
                        break
            sents_retain_intervals[s] = set(keep)

        for i in ind:
            txt = curated.loc[i, 'TEXT']
            if pd.isna(txt):
                curated.loc[i, 'TEXT_processed'] = ''
                continue
            sents = txt.split('|')
            sents = [s.strip() for s in sents]
            new_sents = []
            for s in sents:
                if i in sents_retain_intervals.get(s, set()) and len(s)>0:
                    new_sents.append(s)
            curated.loc[i, 'TEXT_processed'] = '|'.join(new_sents)

    curated = curated.drop('TEXT', axis=1)
    curated = curated.rename(columns = {'TEXT_processed':'TEXT'})

    return curated


## removing sentences that have dates beyond the current interval
date_patterns = [
        r'\b\d{1,2}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{2,4}\b',                     
        r'\b\d{1,2}\s*[-/]\s*\w{3,9}\s*[-/]\s*\d{2,4}\b',                     
        r'\b\w{3,9}\s+\d{4}\b',                                              
        r'\b\d{1,2}\s*[-/]\s*\d{4}\b',                                       
        r'\b\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{1,2}\b',                      
        r'\b\d{1,2}(st|nd|rd|th)?\s+\w{3,9}\s+\d{4}\b',                      
        r'\b\w{3,9}\s+\d{1,2},\s*\d{4}\b',                                   
        r'\b\d{1,2}(st|nd|rd|th)?\s+of\s+\w{3,9},\s*\d{4}\b',                
        r'\b\d{4}\s+\w{3,9}\s+\d{1,2}\b',                                    
        r'\b\d{1,2}\.\d{1,2}\.\d{2,4}\b',                                    
        r'\b\d{4}\.\d{1,2}\.\d{1,2}\b',                                      
        r'\b(Q[1-4]|[1-4](st|nd|rd|th)?\s+Quarter)\s+\d{4}\b',               
        r'\b(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day,\s+\w{3,9}\s+\d{1,2},\s*\d{4}\b',
        r'\b(19[8-9][0-9]|20[0-2][0-9]|2025)\b',
        r'\b\d{1,2}\s*[A-Za-z]{3}\s*\d{2}\b',
        r'\b\d{1,2}/\d{2,4}\b',
    ]

def extract_date(sentence):
    for pattern in date_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            date_str = match.group().strip()
            try:
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    parsed_date = parsed_date.replace(tzinfo=None)
                    return True, parsed_date
            except:
                pass
    return False, None

def filtering_sentences_with_old_date(text, st_date, ed_date):
    sents = text.split('|')
    st_date = pd.to_datetime(st_date).replace(tzinfo=None)
    ed_date = pd.to_datetime(ed_date).replace(tzinfo=None)
    new_sents = []
    for s in sents:
        found, ext_date = extract_date(s)
        # if found and st_date <= ext_date <= ed_date:  ## to remove all sentences beyond the current interval
        if found and st_date - timedelta(days=365) <= ext_date <= ed_date:   ## retain sentences if the date in sentence is within 1 year of current interval
            new_sents.append(s)
        if not found:   ## if 'false', it means that the sentence does not have any date and hence it has to be retained.
            new_sents.append(s)
    return '|'.join(new_sents)

def process_each_row(row):
    return filtering_sentences_with_old_date(row['TEXT'], row['ST_DATE'], row['ED_DATE'])

def parallellization_filtering_sentences_with_old_date(df):
    with Pool(cpu_count()) as pool:
        results = pool.map(process_each_row, [row for i, row in df.iterrows()])
    return results




def curated_text_postprocessing(curated):
    '''
    This function cleans the curated text. It performs the following:
        - removes duplicate sentences within an interval
        - removes duplicate sentences across intervals of a patient
        - removes sentences that fall beyond the current interval - first identifies the sentences that have dates mentioned and if the date is mentioned it checks the date with current interval. If the sentence is beyond the current interval, it will be removed.
        - removes sentences that have phrases like "status post", "demographic information".
    '''
    print("length of input curated notes:", len(curated))
    curated['TEXT'].replace('', np.nan, inplace=True)
    curated = curated[curated['TEXT'].notna()]
    print("Number of rows to be processed (after removing null rows): ", len(curated))
    curated['TEXT'] = curated['TEXT'].apply(remove_duplicate_sentences_within_interval)

    curated['TEXT_processed'] = curated['TEXT']
    
    ## removal of sentences across intervals
    curated = remove_duplicate_sentences_across_intervals(curated)

    ## removal of sentences based on extracted date
    curated['ST_DATE'] = pd.to_datetime(curated['ST_DATE'])
    curated['ED_DATE'] = pd.to_datetime(curated['ED_DATE'])
    curated['TEXT_cleaned_2'] = parallellization_filtering_sentences_with_old_date(curated)
    curated = curated.drop('TEXT', axis=1)
    curated = curated.rename(columns = {'TEXT_cleaned_2':'TEXT'})

    ## removal of sentences that have words like "status post", "demographic information"
    curated['TEXT'] = curated['TEXT'].str.replace('s/p', "status post", case=False)
    phrases_to_check = ["status post", "demographic information"]
    for w in phrases_to_check:
        indices = curated[curated['TEXT'].str.contains(w, case=False, na=False)].index.tolist()
        for i in indices:
            sents = curated.loc[i, 'TEXT'].split('|')
            new_sents = []
            for s in sents:
                if w in s.lower():
                    found, ext_date = extract_date(s)
                    if not found:   ## remove sentence only if it doesnt have date. if date is present, it will be current interval only as we have already removed other interval date sentences
                        continue
                new_sents.append(s)
            if len(new_sents)==0:
                curated.loc[i, 'TEXT'] = '|'.join(sents)
            else:
                curated.loc[i, 'TEXT'] = '|'.join(new_sents)
    return curated


