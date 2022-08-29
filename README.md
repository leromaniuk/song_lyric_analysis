# Song Lyric Analysis
The aim of this project is to predict song's genres from their lyrics.

### Getting Started

To run code from this repository, required package imports are found in the yml file.
Collecting data for analysis will require developer accounts with both Spotify and Genius. After creating accounts, you will be provided a client_id and client_secret needed to access data from the API. Below is guidance for how to set up the accounts:
* [Spotify](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/)
* [Genius](https://docs.genius.com/#/getting-started-h)

### Collecting data

Model is run on tracks from albums released in 2020.
1.	To collect list of all album and artist names I used Beautiful Soup to scrape the Wikipedia page https://en.wikipedia.org/wiki/List_of_2020_albums. 
2.	Using the album and artist names I could retrieve album tracks from the Spotify API using the python package spotipy.
3.	After collecting track names, I used the python package lyricsGenius to collect lyrics using artist and track names.
Final pandas dataframe contains over 14 000 tracks with lyrics.
