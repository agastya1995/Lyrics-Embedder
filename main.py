from grabber import lyricsApi, lyricsEmbedder, songDetails, hasID3Tags, checkApiKey
import os
import sys
from pathlib import Path
import datetime
import re


print('''Embed lyrics to your songs. To get started, create an account on APIseeds.
 After creating the account, you will get an api key. Use this key in the next step''')

apiKey = input('Enter your api key: ')
folder = input('Enter Song Folder Path: ')
overwrite_lyrics = input('Do you wish to overwrite existing lyrics?\ny or n\n')

# To ensure the path format is correct
if folder.startswith('"'):
    folder = re.sub('"|\'', '', folder)
folder = os.path.abspath(folder)

# Check the validity of the api
if checkApiKey(apiKey) is False:
    print('Wrong API key entered. Please check your key and try again.')
    sys.exit()

if 'n' in overwrite_lyrics:
    overwrite_lyrics = False
else:
    overwrite_lyrics = True

lyric_writing_status = {}

print('Adding lyrics... Please wait')


# Loop over the folder, check if the metadata is there, and finally add lyrics. The status is added to the lyrics_writing_status dict.
for a, b, c in os.walk(folder):
    for files in c:
        if files[-4:] == ".mp3":
            song = os.path.join(a, files)
            lyric_writing_status[song] = None
            
            # Check for tags.
            if hasID3Tags(song):
                details = songDetails(song)
            else:
                lyric_writing_status[song] = 'No ID3 Tags Found'
                continue
            
            if details is None:
                lyric_writing_status[song] = 'No Metadata Found'
                continue
            
            artist, title, lyrics = details
    
            if overwrite_lyrics is False:
                if lyrics != None:
                    lyric_writing_status[song] = 'Lyrics Already Added'
                    continue
            
            if (overwrite_lyrics ==True) or (lyrics==None):
                # Get lyrics of the song, check if lyrics have been returned and then embed them into the song
                lyrics = lyricsApi(artist, title, apiKey)
                if lyrics == None:
                    lyric_writing_status[song] = 'Lyrics Not Found'
                    continue
                else:
                    lyricsEmbedder(song, lyrics)
                    lyric_writing_status[song] = 'Lyrics Successfully Added'

current_time = datetime.datetime.now()
time_stamp =  str(current_time.now().now())

time_stamp = re.sub(r'-|:|\s|\.|\d*$', r'_', time_stamp)

with open('log_' + time_stamp+ '.csv', 'w') as f:
    print('Song Path, Status', file=f)
    for k, v in lyric_writing_status.items():
        # If there are commas in the song path, then change it
        k = re.sub(r',', r'_', k)
        print(k,',', v, file=f)

print('Completed')
