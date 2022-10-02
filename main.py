# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:33:53 2022

@author: eller
"""

import modules.get_song_lyrics as gl
import modules.data_cleaning as dc
import modules.preprocess_lyrics as pl

lyrics = gl.import_data(overwrite=False)
dc.data_checks(lyrics)

lyrics_cleaned = dc.data_cleaning(lyrics)
dc.data_checks(lyrics_cleaned)

lyrics_cleaned['lyric_cleaned'] = lyrics_cleaned.copy()['lyric']
frequent_lines = pl.get_frequent_lines(lyrics_cleaned['lyric_cleaned'], 
                    word_count = 6, char_count = 20, freq = 10)
first_lines = pl.get_first_lines(lyrics_cleaned['lyric_cleaned'])
len(common_lines)
len(first_lines)


lyrics_cleaned['lyric_cleaned'] = pl.clean_lyrics(lyrics_cleaned['lyric_cleaned'],
             boiler = frequent_lines + first_lines)