from moviepy.editor import *
import data.config as config

import os

splitMusicDir = "./audio/musicToSplit/"
outputClipsDir = "./audio/music/"
splittedMusicDir = "./audio/musicToSplit/splitMusic/"

clipDuration = 1.5*config.maxVideoDuration

def splitMusic():
    for musicFileDir in os.listdir(splitMusicDir):
        if (os.path.isdir(musicFileDir)):
            continue
        
        musicFile = AudioFileClip(splitMusicDir + musicFileDir)
        musicFileName = os.path.basename(musicFileDir)[:-4]

        for i in range( int(musicFile.duration/clipDuration) - 1 ):
            subMusicFilename = outputClipsDir + musicFileName + "%d.mp3" % (i)

            subMusicFile = musicFile.subclip(i*clipDuration, (i+1)*clipDuration)
            subMusicFile.write_audiofile(subMusicFilename)
        
        os.rename(musicFileDir, splittedMusicDir + musicFileName)

if __name__ == "__main__":
    splitMusic()