"""
Created on Sat Aug 13 18:38:24 2022

@author: Louise Romaniuk
"""
import spotipy
import requests
import pandas as pd

from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials



client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                      client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

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
        all_tracks = sp.album_tracks(uri, limit=50, offset=0, market=None)
        
        for i in range(len(all_tracks['items'])):
            track = all_tracks['items'][i]['name']
            df = df.append({'artist': artist, 
                            'album': album,
                            'track': track}, ignore_index=True)
        
    return df


def append_album_tracks(albums):
    '''
    Given dataframe with album and artist names function adds column with 
    track names
    
    Parameters:
        df (DataFrame): df containing artist, album
        artist (str): artist name

    Returns:
        df (DataFrame): df containing artist, album and tracks
    '''
    
    tracks = pd.DataFrame(columns=['artist', 'album', 'track'])
    
    for i in range(len(albums)):
        tracks = tracks.append(get_album_tracks(albums['album'][i], albums['artist'][i]))
        print(i)
        
    albums = albums.merge(tracks, on=['artist', 'album'], how='left')
        
    return albums

albums = get_wiki_album_names()
append_album_tracks(albums)

