try:
    from VideoPoster.YoutubeVideoPoster import YoutubeVideoPoster
except:
    from YoutubeVideoPoster import YoutubeVideoPoster
    
class VideoPoster(object):
    def __init__(self, videos):
        self.videos = videos
    
    def postYoutubeVideos(self):
        YoutubeVideoPoster(self.videos).postVideos()
        
    def postYoutubeVideo(self, video):
        YoutubeVideoPoster([video]).postVideos()


if __name__ == "__main__":
    VideoPoster("C:/Users/spont/Documents/Projects/General/Python/RedditBombo2/video/input/constantVideos/intro.mp4","name of cool video", "this is the cool description #shorts", "reddit,askreddit,shorts").postYoutubeVideo()