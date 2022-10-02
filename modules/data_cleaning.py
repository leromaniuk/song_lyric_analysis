# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 21:13:58 2022

@author: eller
"""

import string
import spacy
import re
import itertools

import pandas as pd 

from nltk.tokenize import word_tokenize
from spacy.language import Language
from spacy_langdetect import LanguageDetector


from modules import constant_paths as cp


def data_checks(df):
    '''
    Function prints simple data checks for collected pd dataframe
        - counts track duplicates
        - counts missing traks and lyrics
    
    Parameters:
        df (DataFrame): df containing artist, album/ tracks
    '''
    print("data shape: ")
    print(df.shape)
    
    print("missing track values: ")
    print(df['track'].isna().sum())
    print("missing lyric values: ")
    print(df['lyric'].isna().sum())
    
    print("duplicated tracks: ")
    print(df\
          .duplicated(subset=["album", "artist", "track"], keep='first')\
          .sum())
        
def data_cleaning(data):
    '''
    Function provides basic cleaning for collected dataframe 
        - removes rows with track duplicates
        - removes rows with missing tracks or lyrics
    
    Parameters:
        df (DataFrame): df containing artist, album/ tracks

    Returns:
        df (DataFrame): cleaned df
    '''
    
    data = data.drop_duplicates(subset=["album", "artist", "track"], keep='first')
    
    data = data.dropna(subset=['track'])
    data = data.dropna(subset=['lyric'])
    
    data = data.reset_index(drop = True)
    
    frequent_lines = get_frequent_lines(data['lyric'], 
                    word_count = 6, char_count = 20, freq = 10)
    
    first_lines = get_first_lines(data['lyric'])
                                       
    print("number of frequent lines removed: ", len(frequent_lines))
    print("number of first lines removed: ", len(first_lines))
    
    data['lyric_cleaned'] = data.copy()['lyric']
    data['lyric_cleaned'] = clean_lyrics(data['lyric_cleaned'],
             boiler = frequent_lines + first_lines)
    
    data = lyric_lang(data, 'lyric_cleaned')
    
    return data



def separate_lines(doc):
    """
    Function splits document into a list of strings at each line
    Where a line is defined as a character string of any length beginning 
    with an uppercase letter and ending with a new line.
    
    Parameters:
        doc (str): character string

    Returns:
        doc (list): list of strings

    """

    doc = re.sub('(?<=\n)(\s{1}|[A-Z]{1})', r'_SPLIT_\1', doc)
    doc = re.split('_SPLIT_', doc)
    doc = [x.strip() for x in doc]

    return doc

def get_first_lines(doc_series):
    """
    Function to find the first lines from a series of text. 
    
    Parameters:
        doc_series (series): series of strings

    Returns:
        first_lines (list): list of strings
    
    """
    
    lines = doc_series.map(lambda x: separate_lines(x))
    
    first_lines = [item[0] for item in lines]
    
    return first_lines


def get_frequent_lines(doc_series, word_count = 6, char_count = 20, freq = 10):
    """
    Function to find the most frequently occuring lines in a series of text. 
    
    Parameters:
        doc_series (series): series of strings
        word_count (int): minimum words in a line
        char_count (int): minimum characters in a line
        freq (int): minimum frequency for lines to include in final list.

    Returns:
        remove (list): list of strings
    
    """
    
    # split text into a list of sentences
    lines = doc_series.map(lambda x: separate_lines(x))
    
    # create one long list of sentences
    lines = list(itertools.chain.from_iterable(lines))
    
    # create a pd dataframe of the sentences
    lines = pd.DataFrame(lines, columns=["str"])
    
    # Add word count column
    lines['word_count'] = lines['str'].apply(lambda x: len(str(x).split(" ")))

    # Add character count column
    lines['char_count'] = lines['str'].str.len()
    
    # filter to remove all sentences with less or equal to set number of words and characters
    lines = lines[lines['word_count'] >= word_count]
    lines = lines[lines['char_count'] >= char_count]
    
    # Find most frequent sentences across the corpus
    standard_text_freq = lines['str'].value_counts()
    
    # find sentences to remove from the corpus
    remove = standard_text_freq[standard_text_freq >= freq]
    
    # convert series to a list
    remove = list(remove.index.values)
    
    return remove

def clean_lyrics(doc_series, boiler = None):
    """
    Function clean song lyric text. This will clean html, UTF-8, punctuation, 
    correct spacing, contactions and remove list of common phrases.
    
    Parameters:
        doc_series (series): series of strings
        boiler (list): list of lines to remove from the lyric.

    Returns:
        doc_series (series): cleaned input series
    
    """
    
    if boiler is None:
        boiler = [' ']
    
    # remove common phrases
    doc_series = doc_series.str.replace(r'|'.join(map(re.escape, boiler)), ' ')
    
    doc_series = doc_series.str.replace('’',"'")
    
    # remove text in squarte brackets
    doc_series = doc_series.str.replace('\[(.*?)\]','')
    
    # remove excess spaces and leading/ trailing spaces
    doc_series = doc_series.str.replace('\s+',' ').str.strip()
    
    # remove paragraphs
    doc_series = doc_series.str.replace('\r',' ')
    doc_series = doc_series.str.replace('\n',' ')
    
    # Replace UTF-8 with ASCII
    UTF8 = pd.read_excel(cp.PROJECT_PATH + "config/text_replacements.xlsx",
              sheet_name = "UTF-8")
    for i in range(len(UTF8)):
        doc_series = doc_series.str.replace(UTF8["UTF-8"][i], UTF8["ASCII"][i])

    # Replace HTML encoding
    html = pd.read_excel(cp.PROJECT_PATH + "config/text_replacements.xlsx",
              sheet_name = "html")
    for i in range(len(html)):
        doc_series = doc_series.str.replace(html["html"][i], html["ASCII"][i])
    
    # Split punctuation when not spaced properly
    doc_series = doc_series.str.replace(r'([a-z])([A-Z])', r'\1 \2')
    
    # convert all text to lower case
    doc_series = doc_series.str.lower()
    
    # Concatenate a fairly comprehensive list
    prefix = pd.read_excel(cp.PROJECT_PATH + "config/text_replacements.xlsx",
              sheet_name = "prefix")
    for i in range(len(prefix)):
        regex = r'(\b' + prefix["prefix"][i] + ')\s?[-]\s?(\w*\b)'
        doc_series = doc_series.str.replace(regex, r'\1\2')
    
    # remove all numbers
    doc_series = doc_series.str.replace('\d+', ' _NUMBER_ ')
    
    # Remove contractions
    doc_series = doc_series.str.replace(r"won't", "will not")
    doc_series = doc_series.str.replace(r"can't", "cannot")
    doc_series = doc_series.str.replace(r"ain't", "is not")
    doc_series = doc_series.str.replace(r"n't", " not")
    doc_series = doc_series.str.replace(r"'re", " are")
    doc_series = doc_series.str.replace(r"'s", " is")
    doc_series = doc_series.str.replace(r"'d", " would")
    doc_series = doc_series.str.replace(r"'ll", " will")
    doc_series = doc_series.str.replace(r"'t", " not")
    doc_series = doc_series.str.replace(r"'ve", " have")
    doc_series = doc_series.str.replace(r"'m", " am")
    doc_series = doc_series.str.replace(r"'cause", "because")
    doc_series = doc_series.str.replace(r"in'", "ing")
    doc_series = doc_series.str.replace(r"n'", "and")
    doc_series = doc_series.str.replace(r"'round", "around")
    
    
    # remove excess spaces and leading/ trailing spaces
    doc_series = doc_series.str.replace('\s+', ' ').str.strip()
    
    # add correct spacing after punctuation
    doc_series = doc_series.str.replace(r'([a-zA-Z]{3})([.,;:!?//])([a-zA-Z])', r'\1\2 \3')

    # remove embed text
    doc_series = doc_series.str.replace('embed', '')
    
    # remove punctuation
    doc_series = doc_series.str.replace('[.,;:!?\//""]', '')
    doc_series = doc_series.str.replace('-', ' ')
    doc_series = doc_series.str.replace("'", '')
    doc_series = doc_series.str.replace("[()]", '')
    doc_series = doc_series.str.replace('\\\w+', '')
    
    # remove excess spaces and leading/ trailing spaces
    doc_series = doc_series.str.replace('\s+', ' ').str.strip()
    
    # convert all text to lower case
    doc_series = doc_series.str.lower()
    
    return doc_series


def get_lang_detector(nlp, name):
    return LanguageDetector()


def lyric_lang(df, column = 'lyrics_cleaned'):
    """
    Function detects language of text in specificed column and returns
    df with two new columns containing language and language probability
    
    Parameters:
        df (dataframe): dataframe containing at least one text column.
        column (str): text column name.

    Returns:
        df (dataframe): pandas dataframe with language information
    
    """
    
    nlp = spacy.load("en_core_web_sm")
    Language.factory("language_detector", func=get_lang_detector)
    nlp.add_pipe('language_detector', last=True)
    
    lang_df = pd.DataFrame(columns=['language', 'language_score'])
    
    for text in df[column]:
        doc = nlp(text)
        language = doc._.language["language"]
        language_score = round(doc._.language["score"], 3)
        lang_df = lang_df.append({'language': language, 
                        'language_score': language_score}, ignore_index=True)
    df = df.join(lang_df, how = 'left')
    
    return df

