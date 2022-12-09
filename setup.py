from VideoPoster.YoutubeVideoPoster import getChannelCredentials
from VideoSplitter import splitVideos
from MusicSplitter import splitMusic 

#sets up basic settings
if __name__ == "__main__":
    try:
        getChannelCredentials()
    except:
        print("You haven't set up your credentials files correctly. Check out README.txt file.")
        
    splitVideos()
    splitMusic()