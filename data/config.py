from PIL import ImageFont
from random import choice, random
from regex import sub
from googletrans import Translator

import json

#program with immutable constants

class subredditPreset(object):
    name:str
    specialTitle:str
    useComments:bool
    sortingType:int
    postLimit:int
    numberOfLines:int
    numberOfSentences:int
    maxBoxHeight:int
    simplifiedBackground:bool
    hasPause:bool
    timeFrame:int
    minUpvotes:int
    extraTime:int

    def __init__(self, name, specialTitle, useComments, sortingType, postLimit, numberOfLines, numberOfSentences, maxBoxHeight, simplifiedBackground, hasPause, timeFrame=4, minUpvotes=100, extraTime=0):
        self.name = name
        self.specialTitle = specialTitle
        self.useComments = useComments
        self.sortingType = sortingType
        self.postLimit = postLimit
        self.numberOfLines = numberOfLines
        self.numberOfSentences = numberOfSentences
        self.maxBoxHeight = maxBoxHeight
        self.simplifiedBackground = simplifiedBackground
        self.hasPause = hasPause
        self.timeFrame = timeFrame
        self.minUpvotes = minUpvotes

        #extra time used only in conjunction with no comments
        self.extraTime = extraTime

askRedditPreset = subredditPreset("AskReddit", "Asking reddit...",True, 1, 100, 13, 5, 200, False, True)
trueOffMyChestPreset = subredditPreset("TrueOffMyChest", "I got a secret...", False, 1, 100, 4, 2, 75, True, False)
confessionsPreset = subredditPreset("confessions", "I got a confession...", False, 1, 100, 4, 2, 75, True, False)
aitaPreset = subredditPreset("AmItheAsshole", "I think I'm right...", False, 1, 100, 4, 2, 75, True, False, timeFrame=5, minUpvotes=0, extraTime=15)
tifuPreset = subredditPreset("TIFU", "Today I f***** up...", False, 1, 100, 4, 2, 75, True, False, timeFrame=5, minUpvotes=0, extraTime=15)

subredditPresets = [askRedditPreset, trueOffMyChestPreset, confessionsPreset, tifuPreset]
subredditPreset = choice(subredditPresets)
subredditPreset = subredditPresets[0]

class LanguageSetting(object):

    id:str
    font:str
    specialCharacters:str
    canASCII:bool
    ytChannel:str
    tiktokChannel:str
    ytChannelId:str

    def __init__(self, id, specialCharacters, ytChannelId, tiktokChannel,font="verdana", canASCII=True):
        self.id = id
        self.font = font
        self.specialCharacters = specialCharacters
        self.canASCII = canASCII
        self.ytChannel = f"https://www.youtube.com/channel/{ytChannelId}"
        self.tiktokChannel = tiktokChannel
        self.ytChannelId = ytChannelId

languagesSettings = {}

langFile = open('./data/data.json')
for lang in json.load( langFile )["languages"]:
    languagesSettings[lang["languageId"]] = LanguageSetting(lang["languageId"], lang["font"], lang["channelID"], lang["tiktokPage"]) 

languageSetting = languagesSettings.get("en")

def translateText(text, lang):
    if lang == "en":
        return text

    translator = Translator()
    return translator.translate(text, src="en",dest=lang).text

#avg number of letters in a word
averageNumberOfLetters = 5

#how many words/minute are spoken
ttpRate = 170

#how many seconds the video lasts
videoDuration = 100
maxVideoDuration = 58

#the duration of a pause between comments
pauseLength = 0.3

maxCommentNb = 15

boxWidth = 267

maxLines = 25

videoAspect = (720, 1280)

#what to put after each comment, a space needs to preceed the guard! (for l.143 in VideoGenerator.py)
guard = " ¦¦¦¦¦¦¦"

publicVideoDescription = '''
            This is a project of mine, where I want to make a video better than the others. However, as you may notice, it is far from it.... Which is why, for these initial videos, I'd like for internet people to do what they know best : criticize. The more mistakes in the format, voice, pacing, editing.. etc. you notice, the better it will come out. So please, be mean.


            Thanks to ElTioKaDH for the parkour, at https://www.youtube.com/watch?v=NvjJTARxR0I
            #shorts #shortsvideo #reddit #askreddit
        '''

publicVideoDescription = translateText(publicVideoDescription, languageSetting.id)
subredditPreset.specialTitle = translateText(subredditPreset.specialTitle, languageSetting.id)

videoTags = f"reddit,shorts,askreddit,stories,fyp,{languageSetting.id}"

import os

def emptyDirectory(dir):
    for file in os.listdir(dir):
        filePath = os.path.join(dir, file)

        if os.path.isdir(filePath):
            emptyDirectory(filePath)
            os.rmdir(filePath)

        else:
            os.remove(filePath)
                

def setFont(fontSize):
    return ImageFont.truetype("verdana.ttf", int(fontSize))  

fontSize = subredditPreset.maxBoxHeight / subredditPreset.numberOfLines  
# use a truetype font  
font = setFont(fontSize)

def setupTextDisplayed(bestPost, font, numberOfLines, numberOfSentences, leaveFirstPost=False):

    bestPost.textDisplayed = []
    pageIndex = 0

    if bestPost.text == "":
        return bestPost

    for comment in bestPost.text.split(guard):
        if (len(comment) == 0):
            continue

        textOnPage = []

        lineLength = 0
        lineContent = ""

        totalPageCount = 0

        nbSentences = 0
        isFirstPage = True

        #preps comment so that bugs don't happen with \n
        comment = sub("[\n]+","\n ",comment)

        for word in comment.strip(guard[-1]).split(' '):

            if "." in word:
                nbSentences += 1
            
            #for variety
            if random() > 0.9 and len(textOnPage) > 1:
                nbSentences += 1

            if word == "":
                continue
            
            wordSize = font.getsize(word + '  ')[0]

            #if there's a breakline, then skip a line, by pretending that
            #the current word occupies the entire line
            if ("\n" in word):
                word = word.replace("\n", "")
                wordSize = boxWidth - lineLength

            if (lineLength + wordSize) < boxWidth:

                lineContent += word + ' '
                lineLength += wordSize

            ##if there is too much text on the screen, make a new page
            ##and add a new duration for the new comment
            #however only if it's not the title
            else:
                if (len(textOnPage) >= numberOfLines - 1 or nbSentences >= numberOfSentences) and (leaveFirstPost or len(bestPost.textDisplayed) > 0):
                    textOnPage.append(lineContent)

                    page = Page(textOnPage, totalPageCount)
                    
                    page.isStartOfComment = isFirstPage
                    isFirstPage = False

                    bestPost.textDisplayed.append(page)
                    
                    if len(bestPost.pfps) > 0 and len(bestPost.upvotes) > 0 and len(bestPost.awards) > 0:
                        bestPost.pfps.insert(pageIndex, bestPost.pfps[pageIndex])
                        bestPost.upvotes.insert(pageIndex, bestPost.upvotes[pageIndex])
                        bestPost.awards.insert(pageIndex, bestPost.awards[pageIndex])

                    pageIndex += 1

                    textOnPage = []
                    totalPageCount = 0
                    nbSentences = 0

                #todo long words
                elif lineContent == "":

                    maxSize = int(boxWidth/wordSize * len(word)) - 1

                    textOnPage.append(word[:maxSize] + "-")
                    word = "-" + word[maxSize:]

                else:
                    textOnPage.append(lineContent)
                
                lineContent = word + ' '
                lineLength = wordSize
            
            totalPageCount += 1
        
        textOnPage.append(lineContent)
        page = Page(textOnPage, totalPageCount)

        bestPost.textDisplayed.append(page)
        pageIndex += 1

    if bestPost.textDisplayed[-1].totalWords == 0:
        bestPost.textDisplayed.pop()
    
    return bestPost


class Page:
    def __init__(self, lines, totalWords):
        self.lines = lines
        self.totalWords = totalWords
        self.lineNumber = len(lines) 
        self.duration = 0
        self.isStartOfComment = False
        self.font = font