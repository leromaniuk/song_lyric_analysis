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

