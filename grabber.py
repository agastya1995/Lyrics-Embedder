import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT
from mutagen.id3._util import ID3NoHeaderError
import json
import re


def hasID3Tags(songPath):
    '''
    Checks if ID3 tags exist. Returns True if they do and False if they don't
    '''
    try:
        ID3(songPath)
        return True
    except(ID3NoHeaderError):
        return False
    

def songDetails(songPath):
    '''
    Returns the artist, title and lyrics (if any) of the song. Ensure that the song has artist and user tags (use the hasID3Tags function).
    '''

    # Two variables for EasyID and ID3. Not good python code but easy to understand
    easyTags = EasyID3(songPath)
    tags = ID3(songPath)
    usltPattern = re.compile(r'USLT.*',re.DOTALL) # To match lyrics key

    try:
        artist = easyTags['artist'][0].lower().strip()
        title = easyTags['title'][0].lower().strip()
    except(KeyError):
        return None
    
    # Remove special characters
    artist = re.sub(re.compile(r'[^A-Za-z0-9\s]'), '', artist)
    title = re.sub(re.compile(r'[^A-Za-z0-9\s]'), '', title)

    # Get lyrics, using regex pattern
    for key in tags.keys():
        match = re.search(usltPattern, key)
        if match is not None:
            lyrics = tags[match.group()]
            break
        else:
            lyrics = None
             
    return artist, title, lyrics


def lyricsApi(artist, title, apiKey):
    '''
    Returns lyrics from Orion's api based on the artist and the title
    '''

    url = f'https://orion.apiseeds.com/api/music/lyric/{artist}/{title}?apikey={apiKey}'
    response = requests.get(url).text
    details = json.loads(response)
    
    if details.get('result', False ): # Run only if lyrics are available
        lyrics = details['result']['track']['text']
        return lyrics
    else:
        return None


def lyricsEmbedder(songPath, lyrics):
    '''
    Embed lyrics to the song
    '''
    tags = ID3(songPath)
    tags["USLT"] = USLT(encoding=3, text=lyrics, lang='eng')
    tags.save()


def checkApiKey(key):
    '''
    A quick check to see if the api entered is correct or not. Returns False if incorrect and true if correct
    '''
    url = f'https://orion.apiseeds.com/api/music/lyric/adele/hello?apikey={key}'
    response = requests.get(url).text
    details = json.loads(response)
    if details.get('succes') == False:
        return False
    else:
        return True




    