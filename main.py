import data.config as config

from AudioGenerator import AudioGenerator
from RedditScraper import RedditScraper
from VideoGenerator import VideoGenerator

from VideoPoster.VideoPoster import VideoPoster
from VideoPoster.ManualVideoPoster import ManualVideoPoster

from time import time
from os import getcwd
from random import choice

from VideoPoster.VideoObject import VideoObject
#TODO:
#test pauses btw comments
#clean directories every week and refresh token

#main class of the program, that allows to create and post a video.
class main(object):
    def __init__(self, nbOfVideos):

        self.videos = []

        for videoNumber in range(nbOfVideos):
            config.subredditPreset = choice(config.subredditPresets)
            config.subredditPreset.specialTitle = config.translateText(config.subredditPreset.specialTitle, config.languageSetting.id)

            self.timeSearching = time()
    
            redditScraper = RedditScraper(True)

            redditScraper.findPosts()
            
            self.timeSearching = time() - self.timeSearching
            
            self.timeSpent = time()

            redditFileName = "%s_%d" % (config.subredditPreset.name, redditScraper.postNumber)
            audioFileName = redditFileName + '_audio'

            audioGenerator = AudioGenerator(redditScraper.bestPost.textDisplayed)
            redditScraper.bestPost = audioGenerator.saveAudio(audioFileName, redditScraper.bestPost)

            if audioGenerator.totDuration <= config.videoDuration:
                config.videoDuration = audioGenerator.totDuration

            videoTitle = redditFileName + '_video_' + config.languageSetting.id

            VideoGenerator(
                videoTitle, 
                redditScraper.bestPost,
                "./video/temp/%s/%s.mp3" % (audioFileName, audioFileName),
                redditScraper.bestPost.textDisplayed,
            )

            #flush the temp folder
            config.emptyDirectory('./video/temp/')
            self.timeSpent = time() - self.timeSpent

            self.timeUploading = time()

            #max. length 100
            publicVideoTitle = "%s " % (config.subredditPreset.specialTitle)

            if (publicVideoTitle[-1] == '"'):
                publicVideoTitle = publicVideoTitle[:-3] + "..."

            fullVideoPath = '%s/video/output/%s.mp4' % ( getcwd() ,videoTitle)
            fullVideoPath = fullVideoPath.replace("/", "\\")

            self.videos.append(VideoObject(fullVideoPath, publicVideoTitle, config.publicVideoDescription, config.videoTags, config.languageSetting, redditScraper.bestPost.post.permalink, audioGenerator.extraContent))
            print("Video Number %d." % videoNumber)

        #uncomment if you have valid credentials
        #self.postVideos()
    
    #posts the videos once they are generated
    def postVideos(self):
        videoPoster = VideoPoster(self.videos)
        videoPoster.postYoutubeVideos()

        #working on increasing reliabilty
        #manualVideoPoster = ManualVideoPoster(self.videos)
        #manualVideoPoster.postAllTikTokVideos()
        #manualVideoPoster.returnToMainDesktop()
        
    #prints out useful info regarding the performance of the program
    def printInfo(self):
        print("The program took: %ds to find the content for a video, %ds to generate the video and %ds to upload the video. A total of %ds, for a %ds video with a resolution of %dx%dpx. \n\n\n\n\n" % 
            (self.timeSearching, self.timeSpent, time() - self.timeUploading, self.timeSpent + self.timeSearching + time() - self.timeUploading, config.videoDuration, config.videoAspect[0], config.videoAspect[1]))

if __name__ == "__main__":
    main(1).printInfo()