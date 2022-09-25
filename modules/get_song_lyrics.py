"""
Created on Sat Aug 13 18:38:24 2022

@author: Louise Romaniuk
"""
import spotipy
import requests
import time
import os
import pandas as pd

from bs4 import BeautifulSoup
from lyricsgenius import Genius
from spotipy.oauth2 import SpotifyClientCredentials

from modules import constant_paths as cp

sp = spotipy.Spotify(client_credentials_manager = 
                         SpotifyClientCredentials(
                             client_id = cp.SPOTIFY_CLIENT_ID,
                             client_secret = cp.SPOTIFY_CLIENT_SECRET),
                         requests_timeout=10, retries=10)
    
genius = Genius(cp.GENIUS_ACCESS_TOKEN)

def import_data(overwrite=False):
    '''
    Opens csv with artist, album, tracks, lyrics information
    if file not found or overwrite is specified function creates csv
    
    Parameters:
        overwrite (bool): Select True to create and overwrite csv
    Returns:
            df (DataFrame): pd dataframe with artist, album, tracks, lyrics
    '''
    
    if os.path.exists(cp.DATA_PATH + "lyrics_2020.csv") == False\
    or overwrite == True:
        
        print("collecting 2020 album names")
        albums = get_wiki_album_names()
        print("collecting artist genres from Spotify API")
        albums_and_genres = add_new_column(albums, 'artist_genres')
        print("collecting album tracks from Spotify API")
        albums_and_tracks = add_new_column(albums_and_genres, 'track')
        print("collecting track lyrics from Genius API")
        tracks_and_lyrics = add_new_column(albums_and_tracks, 'lyric')
        
        try:
            tracks_and_lyrics.to_csv(cp.DATA_PATH + "lyrics_2020.csv")
            print("file written: " + cp.DATA_PATH + "lyrics_2020.csv")
        except Exception as e:
            print(str(e))
            df = tracks_and_lyrics
    else:
        df = pd.read_csv(cp.DATA_PATH + "lyrics_2020.csv")
  
    return df
    


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

def get_artist_genres(album, artist):
    
    '''
    Given album and artist name function returns the artist genres
    from the spotify API
    
    Parameters:
        album (str): album name
        artist (str): artist name

    Returns:
        df (DataFrame): df containing artist, album and artist genres
    '''
    
    searchQuery = album + ' ' + artist
    searchResults = sp.search(q=searchQuery, limit = 1)
    
    df = pd.DataFrame(columns=['artist', 'album', 'artist_genres', 'artist_uri'])
        
    try:
        artist_uri = searchResults['tracks']['items'][0]['artists'][0]['uri']
    except IndexError:
        print(f"Album '{album}' by artist '{artist}' not found with Spotify"
              + " API search")
    
    else:
        retries = 0
        while retries < 2:
            try:
                genre = sp.artist(artist_uri)['genres']
            
            except requests.exceptions.Timeout:
                print("Timeout error wait 10 seconds and retry, attempt: " + retries)
                time.sleep(10)
                retries = retries + 1
                continue
            break
            
        df = df.append({'artist': artist, 
                        'album': album,
                        'artist_genres': genre,
                        'artist_uri': artist_uri}, ignore_index=True)
         
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
    
    df = pd.DataFrame(columns=['artist', 'album', 'track', 'track_uri'])
        
    try:
        uri = searchResults['tracks']['items'][0]['album']['uri']
    except IndexError:
        print(f"Album '{album}' by artist '{artist}' not found with Spotify"
              + " API search")
    
    else:
        retries = 0
        while retries < 2:
            try:
                all_tracks = sp.album_tracks(uri, limit=50, offset=0, market=None)
            
            except requests.exceptions.Timeout:
                print("Timeout error wait 10 seconds and retry, attempt: " + retries)
                time.sleep(10)
                retries = retries + 1
                continue
            break
            
        for i in range(len(all_tracks['items'])):
            track = all_tracks['items'][i]['name']
            track_uri = all_tracks['items'][i]['uri']
            df = df.append({'artist': artist, 
                            'album': album,
                            'track': track,
                            'track_uri': track_uri}, ignore_index=True)
         
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
    retries = 0
    while retries < 5:
        try:
            lyric = genius.search_song(track, artist).lyrics
        
        except AttributeError:
            lyric = None
            break
        
        except Exception as e:
            print(str(e))
            if retries < 4:
                time.sleep(10)
                retries = retries + 1
                continue
            else:
                print(f"Unable to collect lyrics for Track '{track}' by " +
                      "artist '{artist}', save as None value")
                lyric = None
                break    
        break
    
    if lyric is not None:
        lyric = (lyric[:30000] + ' [TRUNCATED]') if len(lyric) > 30000 else lyric
        
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
    
    if column == "artist_genres":
        join_column = 'album'
    if column == "track":
        join_column = 'album'
    if column == "lyric":
        join_column = 'track'

    values = pd.DataFrame(columns=['artist', join_column, column])
    
    for i in range(len(df)):
        if column == "artist_genres":
            values = values.append(get_artist_genres(df[join_column][i], df['artist'][i]))
        if column == "track":
            values = values.append(get_album_tracks(df[join_column][i], df['artist'][i]))
        if column == "lyric":
            values = values.append(get_track_lyrics(df[join_column][i], df['artist'][i]))
        print(str(i)+"/"+str(len(df)))
    
    df = df.merge(values, on=['artist', join_column], how='left')
    
    t1 = time.time() - t0
    print("Time elapsed: ", t1, " seconds")
    
    return df
