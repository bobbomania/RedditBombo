import cv2
from PIL import ImageFont, ImageDraw, Image 
from numpy import array 

from moviepy.editor import *
from moviepy.video.fx.all import crop, resize

import os, random
from math import floor, ceil

import data.config as config

from time import time
import numpy as np

topImagePath = './video/input/images/reddit_bg/pfp_bar.png'
midImagePath = './video/input/images/reddit_bg/mid_bar.png'
underImagePath = './video/input/images/reddit_bg/under_bar.png'

loadingBarMidPath = './video/input/images/loading_bar/mid.png'
loadingBarSidePath = './video/input/images/loading_bar/side.png'

bgImagePath = './video/input/images/reddit_bg/background.png'

logoPath = "./video/input/images/a_pear.png"

introVideo = './video/input/constantVideos/intro.mp4'
bgVideosPath = "./video/input/bgVideos/"
bgMusicPath = "./audio/music/"

aspectRatio = config.videoAspect[0] / config.videoAspect[1]

class AddOn(object):
    def __init__(self, videoPath, startTime, position, audioPath, audioStartTime,scaleFactor=(1.0, 1.0), isTransparent=True, centerX=0):
        self.setupVideo(videoPath)
        self.startTime = startTime

        if centerX != 0:
            position = ( int(position[0] + (centerX - self.videoWidth)//2 ), position[1] )

        self.position = position
        if len(audioPath) != 0:
            self.audio = AudioFileClip(audioPath)

        self.audioStartTime = startTime + audioStartTime
        self.scaleFactor = scaleFactor
        self.isTransparent = isTransparent
    
    def setupVideo(self, videoPath):
        self.video = []
        self.videoWidth = 0

        list_of_files = sorted( os.listdir(videoPath), key = lambda x : int(x[:-4]))

        for videoFrameFile in list_of_files:
            videoFrame = cv2.imread(videoPath + videoFrameFile, cv2.IMREAD_UNCHANGED)

            if not self.videoWidth:
                self.videoWidth = videoFrame.shape[1]

            self.video.append(videoFrame)
        
        self.video = iter(self.video)

addOnVideoPath = "./video/input/constantVideos/addons/"
addOnAudioPath = "./audio/constant audio/addons/"

class VideoGenerator(object):
    def __init__(self, videoTitle, post,
    audioFile, textDisplayed, boxWidth=267):
        self.videoTitle = videoTitle
        self.duration = config.videoDuration

        self.textDisplayed = textDisplayed

        self.simplifiedBackground = config.subredditPreset.simplifiedBackground
        self.maxBoxHeight = config.subredditPreset.maxBoxHeight
        self.boxWidth = boxWidth

        self.post = post

        self.videoFileName = './video/output/%s.mp4' % (videoTitle)
        self.tempFileName = './video/temp/%s.mp4' % (videoTitle)

        self.getBackgroundVideo()
        self.getBackgroundVideoInfo() 

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video = cv2.VideoWriter(self.tempFileName, fourcc, self.fps, self.dimensions)

        self.newWidth = aspectRatio * self.dimensions[1]
        self.xShift = (self.dimensions[0] - self.newWidth)/2

        self.addOns = [ 
            #add one if wanted
            #AddOn(addOnVideoPath + "subscribe/", config.videoDuration//2, (int(self.xShift), 50), addOnAudioPath + "ding.mp3", 3, scaleFactor=(1,1), centerX=self.newWidth)
        ]

        a = time()
        self.addText(post.text)
        print("time to add text to video: %d" % (time()-a))
        clipToClose = self.addAudio(audioFile)
        #self.addMisc()

        self.videoClip = crop(self.videoClip, x1 = floor(self.xShift), x2 = ceil(self.xShift + self.newWidth))
        self.videoClip = self.videoClip.resize(config.videoAspect)

        self.videoClip.write_videofile(self.videoFileName)
        clipToClose.close()
    
    def getBackgroundVideo(self):

        randomBgVideoFileName = random.choice(os.listdir(bgVideosPath))
        videoClip = VideoFileClip( bgVideosPath + randomBgVideoFileName)

        #in the case that the music clip is too short for the video
        if (videoClip.duration < self.duration):
            totDuration = videoClip.duration

            videoClipName = randomBgVideoFileName[:-5]
            videoClipNumber = int(randomBgVideoFileName[-5])

            smallerVideoClips = [videoClip]

            while totDuration < self.duration:
                videoClipNumber += 1
                newVideoPath = "%s%s%d.mp4" % (bgVideosPath, videoClipName, videoClipNumber)

                if not (os.path.exists(newVideoPath)):
                    videoClipNumber = 0
                    newVideoPath = "%s%s%d.mp4" % (bgVideosPath, videoClipName, videoClipNumber)
                    
                newVideo = VideoFileClip(newVideoPath)

                if (totDuration + newVideo.duration > self.duration):
                    newVideo.set_duration(self.duration - totDuration)
                
                smallerVideoClips.append(newVideo)
                totDuration += newVideo.duration

                newVideo.close()
            
            videoClip = concatenate_videoclips(smallerVideoClips)
            
            videoClip.write_videofile(self.tempFileName[:-4] + "_clips.mp4" )
            self.videoBackground = cv2.VideoCapture(self.tempFileName[:-4] + "_clips.mp4")
        
        else:
            self.videoBackground = cv2.VideoCapture(bgVideosPath + randomBgVideoFileName)
        
    def getBackgroundVideoInfo(self):
        width  = self.videoBackground.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = self.videoBackground.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    
        self.dimensions = (int(width), int(height))

        self.fps = self.videoBackground.get(cv2.CAP_PROP_FPS)
        
        bgFrameCount = int ( self.videoBackground.get(cv2.CAP_PROP_FRAME_COUNT) )
        self.totalFrames = int( self.fps * self.duration )

        if (self.totalFrames > bgFrameCount):
            self.totalFrames = int(bgFrameCount) 

    def addText(self, text):

        pageCounter = 0
        lineCounter = 0

        font = self.textDisplayed[pageCounter].font

        fontColor = (173,173,191)
        fontColor = (217,217,218)

        #padding inside the text box, from the left
        left_padding = 40
        #padding inside the text box, from the right
        right_padding = 70

        if self.simplifiedBackground:
            left_padding = self.boxWidth*0.125
            right_padding = left_padding

        outerBoxWidth = int(self.boxWidth + left_padding + right_padding)

        innerBoxHeight = int(self.textDisplayed[pageCounter].lineNumber*font.size*1.35)

        dim = (outerBoxWidth, innerBoxHeight)
        bgImage, height_top, height_bottom = self.createBgImage(dim, self.post.pfps[pageCounter][1], self.post.pfps[pageCounter][0], self.post.upvotes[pageCounter], self.post.awards[pageCounter], False)   
        
        outerBoxHeight = int(innerBoxHeight + height_top + height_bottom)

        #in frames
        timeAllowed = self.textDisplayed[pageCounter].duration * self.fps

        logo = cv2.imread(logoPath)
        loadingBar = self.createLoadingBar(0)

        for i in range (self.totalFrames):

            timeAllowed -= 1

            text = ""
            ret, frame = self.videoBackground.read()

            if frame.shape[0] != self.dimensions[1] or frame.shape[1] != self.dimensions[0]:
                continue

            logoPadding = 20

            logoOverlayed = circularOverlay( logo, frame[logoPadding:logoPadding+logo.shape[0], int(self.xShift)+logoPadding:int(self.xShift)+logoPadding+logo.shape[1]], logo.shape[0]//2, transparency=0.5 )

            frame = overlayImages(frame, logoOverlayed, (logoPadding + int(self.xShift), logoPadding))
            frame = overlayImages(frame, bgImage, ((self.dimensions[0] - outerBoxWidth )//2,(self.dimensions[1] - outerBoxHeight )//2))
            frame = overlayImages(frame, loadingBar, (int(self.xShift), ( self.dimensions[1] - loadingBar.shape[0] )))

            for addOn in self.addOns:
                if i/self.fps > addOn.startTime:
                    addOnFrame = next(addOn.video, False)

                    if not isinstance(addOnFrame, bool):
                        if addOn.scaleFactor != (1,1):
                            addOnWidth, addOnHeight, _ = addOnFrame.shape
                            addOnFrame = cv2.resize(addOnFrame, (int(addOnWidth*addOn.scaleFactor[0]), int(addOnHeight*addOn.scaleFactor[1])))
                        
                        if addOn.isTransparent:
                            frame = transparentOverlay(frame, addOnFrame, addOn.position)
                        

            loadingBar = self.createLoadingBar(i)

            for lineCount in range(lineCounter + 1):
                text += self.textDisplayed[pageCounter].lines[lineCount] + "\n"
            
            text.strip("\n")

    
            if ret:

                frame, _ = cv2DrawText( frame, text, ( (self.dimensions[0]-outerBoxWidth)//2 + left_padding, (self.dimensions[1] + height_top - height_bottom - innerBoxHeight)//2 + 5), self.textDisplayed[pageCounter].font, fontColor )
                self.video.write(frame)

            if lineCounter < len(self.textDisplayed[pageCounter].lines) - 1:
                lineCounter += 1
            
            elif pageCounter < len(self.textDisplayed) - 1 and timeAllowed < 0:
                lineCounter = 0
                pageCounter += 1

                timeAllowed = self.textDisplayed[pageCounter].duration * self.fps
                
                innerBoxHeight = int(self.textDisplayed[pageCounter].lineNumber*font.size*1.35)

                dim = (outerBoxWidth, innerBoxHeight)
                bgImage, height_top, height_bottom = self.createBgImage(dim, self.post.pfps[pageCounter][1], self.post.pfps[pageCounter][0], self.post.upvotes[pageCounter], self.post.awards[pageCounter], self.simplifiedBackground)   
                
                outerBoxHeight = int(innerBoxHeight + height_top + height_bottom)

            #if no more content end the video
            elif pageCounter == len(self.textDisplayed) - 1 and timeAllowed < 0:
                self.duration = i/self.fps
                break            
                
        # release the cap object
        self.video.release()
        self.videoBackground.release()

    def createBgImage(self, dim, pfpPath, authorName, upvoteCount, awardPaths, simplifiedBackground=False):

        underPadding = 60 

        if simplifiedBackground:
            bgImage = cv2.imread(bgImagePath)
            bgImage = cv2.resize(bgImage, (dim[0], int(dim[1]*1.5)), interpolation = cv2.INTER_AREA)

            return bgImage, dim[1]*0.25, dim[1]*0.25
        
        if (dim[0] < underPadding):
            dim = (underPadding, dim[1])
            
        if (dim[1] < 80):
            dim = (dim[0], 80)

        textHeight = dim[1]

        topImage = cv2.imread(topImagePath)
        midImage = cv2.imread(midImagePath)
        underImage = cv2.imread(underImagePath)

        pfp = cv2.imread(pfpPath)
        mask_fg = cv2.imread("./video/input/images/reddit_bg/mask_fg.png")

        if (pfp.shape[0] != 38 or pfp.shape[1] != 38):
            pfp = cv2.resize(pfp, (38,38), interpolation = cv2.INTER_AREA)

        pfp = circularOverlay(pfp, mask_fg, 19)

        #adds and centers the pfp
        pfpPadding = (topImage.shape[0] - pfp.shape[0])//2 
        topImage = overlayImages(topImage, pfp, (pfpPadding, pfpPadding))

        fontSize = topImage.shape[0]*0.25

        if len(authorName) > 15:
            fontSize *= 15/len(authorName)


        # use a truetype font, adds author name 
        font = ImageFont.truetype("verdana.ttf", int(fontSize)) 

        textPadding = pfpPadding + int(pfp.shape[1]*1.5)
        topImage, textSize = cv2DrawText( topImage, authorName + " · ", (textPadding, (topImage.shape[0] - fontSize)//2), font, (215,218,220) )

        textPadding += textSize

        awardSide = 13
        awardsInRow = 5

        #max. number of rows is 2
        numberOfRows = min(2, len(awardPaths)//awardsInRow + 1)

        awardPadding = int(topImage.shape[0] - fontSize//2)//2

        if (len(awardPaths) > awardsInRow):
            awardPaths = awardPaths[:awardsInRow*numberOfRows]
            awardPadding = awardSide + 2

        maxRowWidth = int(1.5*awardsInRow*awardSide)

        #make the award's background to the color of the background
        for awardIndex, awardPath in enumerate(awardPaths):

            currentRow = awardIndex // awardsInRow

            award = cv2.imread(awardPath,cv2.IMREAD_UNCHANGED)
            mask_fg = cv2.resize(mask_fg, (award.shape[1],award.shape[0]), interpolation = cv2.INTER_AREA)

            alpha_channel = award[:, :, 3]
            _, mask = cv2.threshold(alpha_channel, 0, 255, cv2.THRESH_BINARY)  # binarize mask
            
            color = award[:, :, :3]
            award = cv2.bitwise_or(color, color,mask=mask)

            award[mask == 0] = mask_fg[0,0,0]
            award = cv2.resize(award, (awardSide,awardSide), interpolation = cv2.INTER_AREA)
            
            topImage = overlayImages(topImage, award, (textPadding + int(1.5*awardSide*awardIndex)%maxRowWidth,(awardPadding + currentRow*int(awardSide*1.2))))

        dim = ( dim[0], dim[1] + topImage.shape[0] + midImage.shape[0] )

        #accounting for the midsection where the bottom bar shows up into
        numberOfMidSections = ceil(textHeight / midImage.shape[0])

        sections = [midImage for _ in range(numberOfMidSections)]
        sections.insert(0,topImage)

        fullBackground = cv2.vconcat(sections)

        #resizes the bottom bar to show it in full on the screen
        croppedWidth = int(dim[0]/dim[1] * fullBackground.shape[0])

        fontSize = int(underImage.shape[0]*0.5)
        font = ImageFont.truetype("verdana.ttf", fontSize)

        #adds upvotes
        underImage, _ = cv2DrawText( underImage, upvoteCount, (34, 5), font, (215,218,220) )
        underImage = cv2.resize(underImage, (croppedWidth - underPadding, int( (croppedWidth - underPadding)*underImage.shape[0]/underImage.shape[1])), interpolation = cv2.INTER_AREA)
        
        #crops the image to match the same width dimensions
        fullBackground = overlayImages(fullBackground, underImage, (underPadding//2, fullBackground.shape[0] - midImage.shape[0]//2))

        #adjusts the aspect ration width wise
        fullBackground = fullBackground[:fullBackground.shape[0], :croppedWidth]
        fullBackground = cv2.resize(fullBackground, dim, interpolation = cv2.INTER_AREA)

        return fullBackground, topImage.shape[0], int(midImage.shape[0] * (dim[0]/dim[1]))

    def createLoadingBar(self, step):
        loadingBarMid = cv2.imread(loadingBarMidPath)
        loadingBarSide = cv2.imread(loadingBarSidePath)

        numberOfMidSections = ceil((self.newWidth * step/self.totalFrames) / loadingBarMid.shape[1])

        midSections = [ loadingBarMid for _ in range(numberOfMidSections) ]
        midSections.append(loadingBarSide)

        return cv2.hconcat(midSections)

    #maybe move it to AudioGenerator.py
    def addAudio(self, audioSrc):
        
        self.videoClip = VideoFileClip(self.tempFileName)

        ttsClip = AudioFileClip(audioSrc)
        if (ttsClip.duration > self.duration):
            ttsClip = ttsClip.set_duration(self.duration)
        
        randomBgMusicFileName = random.choice(os.listdir(bgMusicPath))
        musicClip = AudioFileClip(bgMusicPath + randomBgMusicFileName)

        #in the case that the music clip is too short for the video
        if (musicClip.duration < self.duration):
            totDuration = musicClip.duration

            musicClipName = randomBgMusicFileName[:-5]
            musicClipNumber = int(randomBgMusicFileName[-5])

            smallerMusicClips = [musicClip]

            while totDuration < self.duration:
                musicClipNumber += 1
                newMusicPath = "%s%s%d.mp3" % (bgMusicPath, musicClipName, musicClipNumber)

                if not (os.path.exists(newMusicPath)):
                    musicClipNumber = 0
                    newMusicPath = "%s%s%d.mp3" % (bgMusicPath, musicClipName, musicClipNumber)
                    
                newMusic = AudioFileClip(newMusicPath)

                if (totDuration + newMusic.duration > self.duration):
                    newMusic.set_duration(self.duration - totDuration)
                
                smallerMusicClips.append(newMusic)
                totDuration += newMusic.duration

                newMusic.close()
            
            musicClip = CompositeAudioClip(smallerMusicClips)
        
        else:
            musicClip = musicClip.set_duration(self.duration)

        musicClip = musicClip.volumex(0.10)

        #arbritrary, just so 1min duration is a 2sec fadeout
        musicClip = musicClip.audio_fadeout(self.duration*2/60)

        completeAudio = CompositeAudioClip([ttsClip, musicClip])
        self.videoClip.audio = completeAudio

        return ttsClip
    
    def addMisc(self):
        if random.random() > 0.5:
            return

        introClip = VideoFileClip(introVideo)
        
        self.videoClip = concatenate_videoclips([introClip, self.videoClip])

def cv2DrawText(image, text, pos, font, fontColor):
    # Convert the image to RGB (OpenCV uses BGR)  
    cv2_im_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)  
    
    # Pass the image to PIL  
    pil_im = Image.fromarray(cv2_im_rgb)  
    
    draw = ImageDraw.Draw(pil_im)  

    draw.text(pos, text , font=font, fill=fontColor)

    # Get back the image to OpenCV  
    return cv2.cvtColor(array(pil_im), cv2.COLOR_RGB2BGR), font.getsize(text)[0]

def circularOverlay(image, bg, radius, transparency=1.0):

    bg = cv2.resize(bg, (image.shape[1], image.shape[0]), interpolation = cv2.INTER_AREA)

    mask = np.zeros(image.shape[:2], dtype="uint8")
    cv2.circle(mask, (radius, radius), radius, 255, -1)

    # get first masked value (foreground)
    fg = cv2.bitwise_or(image, image, mask=mask)

    # get second masked value (background) mask must be inverted
    mask = cv2.bitwise_not(mask)
    bk = cv2.bitwise_or(bg, bg, mask=mask)

    out = cv2.bitwise_or(fg, bk)

    # combine foreground+background
    return cv2.addWeighted(bg,transparency,out,transparency,0) if transparency != 1.0 else out

def overlayImages(image, overlay, position):

    if image.shape[2] == 4:
        image = cv2.cvtColor(array(image), cv2.COLOR_BGRA2BGR)
    
    if overlay.shape[2] == 4:
        overlay = cv2.cvtColor(array(overlay), cv2.COLOR_BGRA2BGR)

    image[position[1] : position[1] + overlay.shape[0],
            position[0] : position[0] + overlay.shape[1] ] = overlay
    
    return image

def transparentOverlay(bg, fg, pos):
    for x in range(fg.shape[1]):
        for y in range(fg.shape[0]):
            pixel = fg[y, x]
            if pixel[3] != 0:
                bg[pos[1] + y, pos[0] + x] = pixel[:3]
    
    return bg
