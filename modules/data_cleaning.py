# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 21:13:58 2022

@author: eller
"""

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
    
    return data
