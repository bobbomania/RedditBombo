from moviepy.editor import *
import data.config as config

import os

splitVideoDir = "./video/input/videosToSplit/"
outputClipsDir = "./video/input/bgVideos/"
splittedVideoDir = "./video/input/videosToSplit/splitVideos/"

clipDuration = 1.5*config.maxVideoDuration

def splitVideos():
    for videoFilePath in os.listdir(splitVideoDir):
        if (os.path.isdir(splitVideoDir + videoFilePath)):
            continue
        
        videoFile = VideoFileClip(splitVideoDir + videoFilePath)
        videoFileName = os.path.basename(videoFilePath)[:-4]

        for i in range( int(videoFile.duration/clipDuration) - 1 ):
            subvideoFilename = outputClipsDir + videoFileName + "%d.mp4" % (i)

            subvideoFile = videoFile.subclip(i*clipDuration, (i+1)*clipDuration)
            subvideoFile.write_videofile(subvideoFilename)
        
        os.rename(videoFilePath, splittedVideoDir + videoFileName[:-1] + ".mp4")

if __name__ == "__main__":
    splitVideos()