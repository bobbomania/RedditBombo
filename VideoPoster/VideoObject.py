import os

class VideoObject(object):
    def __init__(self, videoPath, videoTitle, videoDescription, videoTags, languageSetting ,postLink="", extraContent=""):
        self.videoPath = videoPath
        self.videoTitle = videoTitle
        self.videoDescription = videoDescription
        self.videoTags = videoTags
        self.postLink = "https://www.reddit.com" + postLink
        self.extraContent = extraContent
        self.languageSetting = languageSetting

def getAllVideoObejcts():

    videoObjects = []

    mainDir = os.getcwd()
    videoOutputPath = mainDir + "\\video\\output\\"

    import sys        
    sys.path.insert(0, mainDir + "\\data")       
    
    import config 

    for file in os.listdir( videoOutputPath ):

        videoNumber = ''.join([ char if char.isdigit() else "" for char in file[:-4] ])
        videoObjects.append(VideoObject( videoOutputPath + file, "%s " % config.subredditPreset.specialTitle, config.publicVideoDescription, config.videoTags, config.languageSetting))


    return videoObjects

if __name__ == "__main__":
    getAllVideoObejcts()