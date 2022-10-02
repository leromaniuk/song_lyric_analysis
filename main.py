# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:33:53 2022

@author: eller
"""

import modules.get_song_lyrics as gl
import modules.data_cleaning as dc

lyrics = gl.import_data(overwrite=False)
dc.data_checks(lyrics)

lyrics_cleaned = dc.data_cleaning(lyrics, overwrite_step1 = True, overwrite_step2 = True)
dc.data_checks(lyrics_cleaned)

lyrics_cleaned['lyric_cleaned'] = lyrics_cleaned.copy()['lyric']
frequent_lines = dc.get_frequent_lines(lyrics_cleaned['lyric_cleaned'], 
                    word_count = 6, char_count = 20, freq = 10)
first_lines = dc.get_first_lines(lyrics_cleaned['lyric_cleaned'])
len(frequent_lines)
len(first_lines)


lyrics_cleaned = lyrics_cleaned.loc[0:10]
lyrics_cleaned['lyric_cleaned'] = dc.clean_lyrics(lyrics_cleaned['lyric_cleaned'],
             boiler = frequent_lines + first_lines)






