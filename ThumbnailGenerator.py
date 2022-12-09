from keybert import KeyBERT
from nltk.corpus import wordnet as wn

import data.config as config
from RedditScraper import RedditPost, RedditScraper

import pixabay.core

from os import listdir
from PIL import Image, ImageDraw, ImageOps, ImageFont
import numpy as np

from string import ascii_lowercase, punctuation, capwords
from random import choice, random

thumbnailSize = (1280,720)
maxImageSize = (600,720)

titleSize = (800, thumbnailSize[1]*0.2)

#the 0.95 signifies the padding of the text from the bottom
textHeight = (thumbnailSize[1] - titleSize[1]) * 0.90
textSize = (thumbnailSize[0] - maxImageSize[0] + 100, textHeight)

thumbnailPath = "./video/input/thumbnails/"
maskPath = thumbnailPath + "thumbnail_mask.png"

bgPath = "./video/input/images/reddit_bg/background.png"
arrowPath = thumbnailPath + "arrow.png"

outputDir = "./video/input/thumbnails/final_thumbnails/"


def getSearchWords(text, wordsNumber, removeAdverbs=True):
    kw_model = KeyBERT()

    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, wordsNumber))
    searchableKeywords = []

    for keyword in keywords:
        words = keyword[0].split(" ")
        searchableWords = ""

        for word in words:
            wordSets = wn.synsets(word)
            if len(wordSets) == 0:
                continue

            if not removeAdverbs or wordSets[0].pos() != "r":
                searchableWords += word + " "
        
        if len(searchableWords) > 0:
            searchableKeywords.append(searchableWords[:-1].lower())

    return searchableKeywords

def getImageFromPixabay(keywords, path):
    # init pixabay API
    px = pixabay.core("29630361-e62986869ff254df8299d07f4")

    # search for space
    image = px.query(keywords)

    if len(image) == 0:
        return False

    print(f"{len(image)} images found.")

    image[0].download(path, "largeImage")

    return True

def getThumbnailImage(text, tempThumbnailPath):

    for wordsNumber in range(2,0,-1):
        keywords = getSearchWords(text, wordsNumber)
        print(keywords)

        for keyword in keywords:
            if (getImageFromPixabay(keyword, tempThumbnailPath)):
                return True
    
    return False

def adjacentPixelColored(index, w, array):
    for xShift in range(-1, 1, 1):
        for yShift in range(-1, 1, 1):
            if (xShift or yShift):
                try:
                    if array[index + w*yShift + xShift][3] != 0:
                        return True
                except:
                    continue
    
    return False

def addThumbnailImageOnBg(imagePath, bgImage):
    thumbnailCenterImage = Image.open(imagePath)

    w,h = thumbnailCenterImage.size

    pixRGBA = list(thumbnailCenterImage.getdata())

    if len(pixRGBA[0]) == 4: 
        colPair = [float('inf'),0]
        rowPair = [float('inf'),0]

        outlinePixelValue = (255,255,255,255)
        outlineWidth = 10

        thumbnailCenter = [0,0]
        totColoredPixels = 0

        newImage = [(0,0,0,0) for _ in range(len(pixRGBA))]

        for pixelIndex in range(len(pixRGBA)):
            if pixRGBA[pixelIndex][3] != 0:
                newImage[pixelIndex] = pixRGBA[pixelIndex]

                x = pixelIndex%w
                y = pixelIndex//w

                if x < colPair[0]:
                    colPair[0] = x
                elif x > colPair[1]:
                    colPair[1] = x

                if y < rowPair[0]:
                    rowPair[0] = y
                elif y > rowPair[1]:
                    rowPair[1] = y

                thumbnailCenter[0] += x
                thumbnailCenter[1] += y

                totColoredPixels += 1

            else:
                if adjacentPixelColored(pixelIndex, w, pixRGBA):
                    for xShift in range(-outlineWidth, outlineWidth, 1):
                        for yShift in range(-outlineWidth, outlineWidth, 1):
                            try:
                                newPixelIndex = pixelIndex + w*yShift + xShift
                                if pixRGBA[newPixelIndex][3] == 0:
                                    newImage[newPixelIndex] = outlinePixelValue
                            except:
                                continue
        
                else:
                    newImage[pixelIndex] = pixRGBA[pixelIndex]
        
        thumbnailCenter = (int(thumbnailCenter[0] / totColoredPixels), int(thumbnailCenter[1]/ totColoredPixels))
        
        thumbnailCenterImage.putdata(newImage)
        thumbnailCenterImage = thumbnailCenterImage.crop((colPair[0],rowPair[0],colPair[1], rowPair[1]))
        
        h = rowPair[1] - rowPair[0]
        w = colPair[1] - colPair[0]

    else:
        thumbnailCenterImage.putalpha(255)
        thumbnailCenter = (thumbnailSize[0]*1.2, thumbnailSize[1]*0.75)

    wThumbnail, hThumbnail = thumbnailCenterImage.size
    
    #if rectangular enough, then fade the pic instead of resize
    if wThumbnail/hThumbnail > 1.0:

        thumbnailCenterImage.putalpha(255)

        pixels = thumbnailCenterImage.load()

        xStart = textSize[0]/thumbnailSize[0]*0.7
        xEnd = 1.0

        for x in range(int(wThumbnail*xStart), int(wThumbnail*xEnd)):
            alphaValue = int( 255 * ( (x - int(wThumbnail*xStart)) / (wThumbnail * (xEnd - xStart))))

            for y in range(hThumbnail):
                pixels[x, y] = pixels[x, y][:3] + (alphaValue,)

        for x in range(int(wThumbnail*xStart), -1, -1):
            for y in range(hThumbnail):
                pixels[x, y] = pixels[x, y][:3] + (0,)
        

        wIm, hIm = thumbnailCenterImage.size
        thumbnailCenterImage = thumbnailCenterImage.resize( ( int(wIm*thumbnailSize[1]/hIm), thumbnailSize[1] ) )

        thumbnailCenterImage = ImageOps.mirror(thumbnailCenterImage)

        if wIm > thumbnailSize[0]:
            thumbnailCenterImage = thumbnailCenterImage.crop((0, 0, thumbnailSize[0], thumbnailSize[1]))

        thumbnailCenterImage = ImageOps.mirror(thumbnailCenterImage)
        thumbnailCenter = (thumbnailSize[0]*1.2, thumbnailSize[1]*0.75)

        wThumbnail, hThumbnail = thumbnailCenterImage.size

        newDim = (thumbnailSize[0] if thumbnailSize[0] < wThumbnail else wThumbnail,
            thumbnailSize[1] if thumbnailSize[1] < hThumbnail else hThumbnail)

    else:
        newDim = (maxImageSize[0], int(h*maxImageSize[0]/w)) if w > h else (int(w*maxImageSize[1]/h), maxImageSize[1])
        thumbnailCenterImage = thumbnailCenterImage.resize(newDim)

    thumbnailPos = (bgImage.size[0] - newDim[0], (bgImage.size[1] - newDim[1]))
    bgImage.paste(thumbnailCenterImage, thumbnailPos, thumbnailCenterImage)

    if random() > 0.5:
        arrowheadPos = (716, 364)
        arrow = Image.open(arrowPath)

        arrowWidth = 300
        arrowResizeFactor = arrowWidth / arrow.size[0]
        arrowHeight = int(arrowResizeFactor * arrow.size[1])

        arrow = arrow.resize((arrowWidth, arrowHeight))

        arrowheadPos = (arrowResizeFactor * arrowheadPos[0], arrowResizeFactor * arrowheadPos[1])

        bgImage.paste(arrow, ( int( 0.75 * thumbnailCenter[0] + thumbnailPos[0] - arrowheadPos[0] - arrowWidth), int( 1.25 * thumbnailCenter[1] + thumbnailPos[1] - arrowheadPos[1] - arrowHeight ) ), arrow)

    return bgImage

def circle(draw, center, radius, fill):
    draw.ellipse((center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1, center[1] + radius - 1), fill=fill, outline=None)

def addSubredditTitle(bgImage, redditScraper):

    subredditTitle, iconPath = redditScraper.getSubredditIcon()

    subredditTitle = "r/" + subredditTitle

    iconWidth = int(titleSize[0] * 0.1)
    iconHPadding = int((titleSize[1] - iconWidth)//2)
    iconWPadding = 50

    subredditIcon = Image.open(iconPath).convert('RGB')
    subredditMask = Image.open(maskPath).convert('L')

    subredditIcon = subredditIcon.resize((iconWidth, iconWidth))

    subredditMask = ImageOps.fit(subredditMask, subredditIcon.size, centering=(0.5, 0.5))
    subredditIcon.putalpha(subredditMask)   

    bgImage.paste( subredditIcon, (iconWPadding, iconHPadding), subredditIcon )

    awardWidth = 50
    awardPadding = 10

    fontW, fontH = config.font.getsize(ascii_lowercase)

    fontW /= len(ascii_lowercase)

    wPadding = int(iconWPadding*1.5 + iconWidth)

    redditAwardsDir = "./video/input/reddit_awards/"

    awards = [ 
        Image.open( redditAwardsDir + choice(listdir(redditAwardsDir)) ).convert("RGBA"), #random award
        Image.open(redditAwardsDir + "gid_2.png").convert("RGBA"),   #gold award
        Image.open(redditAwardsDir + "gid_3.png").convert("RGBA")  #diamond award
    ]

    titleWidth = (titleSize[0] - wPadding) * 0.8 - (awardPadding + awardWidth)*len(awards)
    fontSize =  (titleWidth / len(subredditTitle)) * ( fontH / fontW )

    if fontSize > iconWidth:
        fontSize = iconWidth

    font = config.setFont(fontSize)

    draw = ImageDraw.Draw(bgImage)
    draw.text((wPadding, iconWPadding - fontSize//3), subredditTitle, font=font, fill=(255,255,255))

    wPadding += int(font.getsize(subredditTitle)[0])

    for awardIndex, award in enumerate(awards):
        award = award.resize((awardWidth, awardWidth))

        bgImage.paste(award, ( wPadding + (awardWidth + awardPadding)*awardIndex + awardWidth, int(titleSize[1] - awardWidth)//2 ), award)

    lineColor = (128,128,128)
    lineWidth = 4

    lineCoords = [(iconWPadding//2, titleSize[1] - iconHPadding//2),(titleSize[0], titleSize[1] - iconHPadding//2)]

    draw.line(lineCoords, fill=lineColor, joint="curved", width=lineWidth)

    circle(draw, (lineCoords[0][0], lineCoords[0][1]), lineWidth / 2, lineColor)
    circle(draw, (lineCoords[1][0], lineCoords[1][1]), lineWidth / 2, lineColor)

    return bgImage, iconWPadding

#to add highlights
def addSubmissionText(submissionText, bgImage, xPadding):

    testPost = RedditPost(None)
    testPost.text = submissionText
    
    tempBoxWidth = config.boxWidth

    config.boxWidth = textSize[0]

    for lineCount in range(4, 100):
        font = ImageFont.truetype("ELEPHNT.TTF", int(textSize[1]/(lineCount+1)))

        textDisplayed = config.setupTextDisplayed(testPost, font, lineCount, 1_000, leaveFirstPost=True).textDisplayed
        if len(textDisplayed) == 1:
            break

    config.boxWidth = tempBoxWidth

    fontHighlight = ImageFont.truetype("ELEPHNT.TTF", int(textSize[1]/(lineCount+1)))
    highlightColor = (245,0,0)
    
    textColor = (255,255,255)

    keywords = getSearchWords(submissionText, 1, False)[:3]
 
    draw = ImageDraw.Draw(bgImage)  

    wordHeight = font.getsize("I")[1] + 10

    yPadding = int( (thumbnailSize[1] - titleSize[1] - textSize[1])//2  )

    for lineCount, line in enumerate(textDisplayed[0].lines):
        wordPadding = xPadding
        
        for word in line.split(" "):
            if word == "":
                continue

            checkWord = word.lower()
            
            punctIndex = 1
            while word[-punctIndex] in punctuation:
                punctIndex += 1
            
            punctIndex -= 1
            if word[-punctIndex] in punctuation:
                checkWord = checkWord[:-punctIndex]
            
            if checkWord in keywords:
                currentFont = fontHighlight
            else:
                currentFont = font

            if len(checkWord) != len(word):
                wordWidth, _ = currentFont.getsize(word[:-punctIndex])

                draw.text((wordPadding,titleSize[1] + lineCount*wordHeight + yPadding), word[:-punctIndex] , font=currentFont, fill=(highlightColor if checkWord in keywords else textColor))
                wordPadding += wordWidth

                currentFont = font

                wordWidth, _ = currentFont.getsize(word[-punctIndex:] + " ")
                draw.text((wordPadding,titleSize[1] + lineCount*wordHeight + yPadding), word[-punctIndex:] + " " , font=currentFont, fill=(textColor))
                wordPadding += wordWidth

            else:
                wordWidth, _ = currentFont.getsize(word + " ")

                draw.text((wordPadding,titleSize[1] + lineCount*wordHeight + yPadding), word + " " , font=currentFont, fill=(highlightColor if checkWord in keywords else textColor))
                wordPadding += wordWidth

    return bgImage

if __name__ == "__main__":

    redditScraper = RedditScraper(True)
    #redditScraper.findPosts()
    redditScraper.addBestPost("wvu1qe")

    text = redditScraper.bestPost.getFullText()

    bgImage = Image.open(bgPath)
    bgImage = bgImage.resize(thumbnailSize)

    thumbnailNumber = str( len(listdir(thumbnailPath + "/temp")) + 1 )
    tempThumbnailPath = thumbnailPath + f"/temp/{thumbnailNumber}.png"

    if not getThumbnailImage(text, tempThumbnailPath):
       getImageFromPixabay("woman", tempThumbnailPath)

    bgImage = addThumbnailImageOnBg(tempThumbnailPath, bgImage)
    bgImage, xPadding = addSubredditTitle(bgImage, redditScraper)
    bgImage = addSubmissionText(capwords(redditScraper.bestPost.post.title), bgImage, xPadding)

    bgImage.show()
    bgImage.save(outputDir + thumbnailNumber + ".png")