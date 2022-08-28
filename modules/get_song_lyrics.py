"""
Created on Sat Aug 13 18:38:24 2022

@author: Louise Romaniuk
"""
import spotipy
import requests
import time
import pandas as pd

from bs4 import BeautifulSoup
from lyricsgenius import Genius
from urllib.error import HTTPError
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                      client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager,
                     requests_timeout=10, retries=10)

def get_wiki_album_names():
    
    '''
    Returns information on all albums released in 2020 from wikipedia

    Returns:
            df (DataFrame): df containing artist, album and genre
    '''

    page = requests.get('https://en.wikipedia.org/wiki/List_of_2020_albums')
    html = BeautifulSoup(page.text, 'html.parser')
    tables = html.find_all('table', class_="wikitable plainrowheaders")
    
     # Defining of the dataframe
    df = pd.DataFrame(columns=['artist', 'album', 'genre'])
    
    # Collecting Ddata
    for table in tables:
        for row in table.tbody.find_all('tr')[1:]:    
            # Find all data for each column
            columns = row.find_all('td')
            
            if(columns != []):
                artist = columns[0].text.strip()
                album = columns[1].text.strip()
                genre = columns[2].text.strip()
        
                df = df.append({'artist': artist,
                                'album': album,
                                'genre': genre}, ignore_index=True)   

    return df

def get_album_tracks(album, artist):
    
    '''
    Given album and artist name function returns all the tracks on the album
    from the spotify API
    
    Parameters:
        album (str): album name
        artist (str): artist name

    Returns:
        df (DataFrame): df containing artist, album and tracks
    '''
    
    searchQuery = album + ' ' + artist
    searchResults = sp.search(q=searchQuery, limit = 1)
    
    df = pd.DataFrame(columns=['artist', 'album', 'track'])
    
    try:
        uri = searchResults['tracks']['items'][0]['album']['uri']
    except IndexError:
        print(f"Album '{album}' by artist '{artist}' not found with Spotify"
              + " API search")
    
    else:
        try:
            all_tracks = sp.album_tracks(uri, limit=50, offset=0, market=None)
        
        except requests.exceptions.Timeout:
            time.sleep(10)
            all_tracks = sp.album_tracks(uri, limit=50, offset=0, market=None)
        
        for i in range(len(all_tracks['items'])):
            track = all_tracks['items'][i]['name']
            df = df.append({'artist': artist, 
                            'album': album,
                            'track': track}, ignore_index=True)
        
    return df

def get_track_lyrics(track, artist):
    
    '''
    Given track and artist name function returns track lyrics from genius API
    
    Parameters:
        album (str): track name
        artist (str): artist name

    Returns:
        df (DataFrame): df containing artist, track and lyrics
    '''
    try:
        lyric = genius.search_song(track, artist).lyrics
    
    except AttributeError:
        lyric = None
        
    except HTTPError:
        time.sleep(10)
        lyric = genius.search_song(track, artist).lyrics
        
    except requests.exceptions.Timeout:
        time.sleep(10)
        lyric = genius.search_song(track, artist).lyrics
    
    d = {'artist': artist, 
         'track': track, 
         'lyric': lyric}
    
    df = pd.DataFrame(data = d, index=[0])
    
    return df


def add_new_column(df, column):
    '''
    Given dataframe with artist and album/track names, function adds column with 
    tracks/lyrics.
    
    Parameters:
        df (DataFrame): df containing artist, album/ tracks
        column (str): column to add to dataframe. Takes two inputs:
                        -track
                        -lyric

    Returns:
        df (DataFrame): df with specified column
    '''
    t0 = time.time()
    
    if column == "track":
        join_column = 'album'
    if column == "lyric":
        join_column = 'track'

    values = pd.DataFrame(columns=['artist', join_column, column])
    
    for i in range(len(df)):
        if column == "track":
            values = values.append(get_album_tracks(df[join_column][i], df['artist'][i]))
        if column == "lyric":
            values = values.append(get_track_lyrics(df[join_column][i], df['artist'][i]))
        print(str(i)+"/"+str(len(df)))
    
    df = df.merge(values, on=['artist', join_column], how='left')
    
    t1 = time.time() - t0
    print("Time elapsed: ", t1, " seconds")
    
    return df


albums = get_wiki_album_names()
len(albums)
albums_and_tracks = add_new_column(albums, 'track')
tracks_and_lyrics = add_new_column(albums_and_tracks, 'lyric')
