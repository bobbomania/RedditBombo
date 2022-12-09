import time
from main import main

from VideoPoster.VideoPoster import VideoPoster
from VideoPoster.ManualVideoPoster import ManualVideoPoster

tiktokSchedule = {
    "id" : "tk",
    "Mon" : (6,16,22),
    "Tue" : (2,4,9.),
    "Wed" : (7,8,23),
    "Thu" : (9,12.,7),
    "Fri" : (5.,13,15),
    "Sat" : (11,19,20),
    "Sun" : (7,8,16)
}

youtubeSchedule = {
    "id" : "yt",
    "Mon" : (18,19,20,21),
    "Tue" : (18,19,20,21),
    "Wed" : (18,19,20,21),
    "Thu" : (18,19,20,21),
    "Fri" : (18,19,20,21),
    "Sat" : (18,19,20,21),
    "Sun" : (18,19,20,21)
}

schedules = [tiktokSchedule, youtubeSchedule]
currentSchedules = []

class schedulePoster(object):
    def __init__(self, nbVideos):
        self.nbVideos = nbVideos
    
    def postInSchedule(self):
        while True:
            currentDay = time.asctime()[:3]
            
            #get the schedule in function of the day
            for schedule in schedules:
                currentSchedules.append((schedule.get("id"),schedule.get(currentDay)))

            videos = main(self.nbVideos).videos
            videoPoster = VideoPoster(videos)
            manualVideoPoster = ManualVideoPoster(videos)

            postingTimes = []

            #get the posting times of each platform, from earliest to latest
            for videoIndex in range(len(videos)):

                for currentSchedule in currentSchedules:
                    postingTimes.append(( currentSchedule[0], *self.getPostingTime(currentSchedule[1], videoIndex)))
                
            postingTimes.sort( key=lambda x : x[1] )

            for postingTime in postingTimes:
                #difference in hour makes it so that it posts at the correct hour,
                #we ignore the minute difference tho
                timeToWait = postingTime[1] - int(time.asctime().split(" ")[3].split(":")[0])
                timeToWait = 3600 * timeToWait if timeToWait > 0 else 0

                time.sleep(timeToWait) if timeToWait > 0 else None

                print("Video #%d got posted on : %s." % (postingTime[2], time.ctime()))

                videoToPost = videos[postingTime[2]]

                if postingTime[0] == "yt":
                    videoPoster.postYoutubeVideo(videoToPost)
                
                elif postingTime[0] == "tk":
                    manualVideoPoster.postTikTokVideos([videoToPost])          
                    manualVideoPoster.returnToMainDesktop()

            pastDay = currentDay

            #check every minute if the day has passed
            while currentDay == pastDay:
                currentDay = time.asctime()[:3]
                time.sleep(60)

                # match postingTime[0]:
                #     case "yt":
                #         videoPoster.postYoutubeVideo()
                #     case _:
                #         print("Invalid platform id, can't post the video.")

                #post at correct platform

    def getPostingTime(self, platformSchedule, index):
        platformIndex = index if index < len(platformSchedule) else len(platformSchedule) - 1
        return platformSchedule[platformIndex], index

if __name__ == "__main__":
    schedulePoster(5).postInSchedule()