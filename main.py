# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:33:53 2022

@author: eller
"""

import modules.get_song_lyrics as gl
import modules.data_cleaning as dc

lyrics = gl.import_data(overwrite=False)
dc.data_checks(lyrics)

lyrics_cleaned = dc.data_cleaning(lyrics, 
                                  overwrite_step1 = False,
                                  overwrite_step2 = False,
                                  overwrite_step3 = False,
                                  overwrite_step4 = True)

lyrics_cleaned['word_count'].plot(kind = 'hist', bins = 100)
lyrics_cleaned['char_count'].plot(kind = 'hist', bins = 100)

