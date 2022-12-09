import praw
import data.config as config
from praw.models import MoreComments

import os
import urllib.request

sortingFunctionTypes = { 
    0 : 'hot',
    1 : 'top',
    2 : 'new',
    3 : 'rising',
    4 : 'controversial'
}   

timeFilters = {
    0 : "all",
    1 : "day",
    2 : "hour",
    3 : "month",
    4 : "week",
    5 : "year"
}

threadsUsedDir = "./data/subredditThreads/%s/" % config.subredditPreset.name

subredditSortingInfo = "--%s-%s-%s" % (sortingFunctionTypes.get(config.subredditPreset.sortingType),timeFilters.get(config.subredditPreset.timeFrame), config.languageSetting.id)

threadsUsedPath = (threadsUsedDir + "threadsUsed%s.txt") % (subredditSortingInfo)
threadsNotUsedPath = (threadsUsedDir + "threadsUnused%s.txt") % (subredditSortingInfo)

#if the directories to store the threads data is non-existent, set it up.
if not (os.path.isdir(threadsUsedDir)):
    os.mkdir(threadsUsedDir)

#setup of files within that directory
if not (os.path.exists(threadsUsedPath)):
    threadsUsed = open(threadsUsedPath, "w")
    threadsUsed.close()

#setup of files within that directory
if not (os.path.exists(threadsNotUsedPath)):
    threadsUnused = open(threadsNotUsedPath, "w")
    threadsUnused.close()

#censors a word. e.g: fudge --> f*dge
def censorWord(word):

    censoredWord = ""

    vowelsCounted = 0
    for chr in word:
        if (chr in "aeiou"):
            vowelsCounted += 1

            #every odd vowel
            if (vowelsCounted%2):
                censoredWord += "*"
                continue

        censoredWord += chr
    
    return censoredWord

#makes sure that text uses only ascii characters (can use .translate, but it doesn't allow for some liberties)
def asciifyText(text):
    asciiText = ""
    upperNext = False

    for chrIndex, chr in enumerate(text):
        chrValue = ord(chr)

        #removes all non-ascii characters except ord('¦') == 166
        if chrValue < 128 or chrValue == 166:

            #add proper punctuation and capitalization
            if chr == "?" or chr == "!" or chr == ".":
                if ( chrIndex != len(text) - 1 and not text[chrIndex + 1].isupper() ):
                    upperNext = True

            #capitalization
            if upperNext or chrIndex == 0:
                asciiText += chr.upper()
                upperNext = False

            else:
                asciiText += chr

        
        # weird apostrophe
        elif chrValue == 8217:
            asciiText += "'"

        #accents allowed
        elif chr in "àùûâæüÿçéèêëïîôœ":
            asciiText += chr
        
    return asciiText

#prepares a title by ascii-fying it
# nd removing all text after the last ? e.g: hello?world -> hello?
def prepTitle(title):
    title = asciifyText(title)
    questionMarkIndex = 0
    for questionMarkIndex in range(len(title)):
        if (title[-questionMarkIndex] == "?"):
            break

    return title if questionMarkIndex == 1 or questionMarkIndex == len(title)-1 else title[:-questionMarkIndex+1]

#compacts a number to mimic reddit's upvote numbers
def compactedNumber(number, suffix):
    #rudimentary but does the job
    if number < 1_000:
        return str(number)
    
    if number < 10_000:
        return "%.1f%s" % ( number/1_000, suffix )
    
    if number < 100_000:
        return "%s%s" % ( str(number)[:2] + "." + str(number)[2], suffix )

    if number < 1_000_000:
        return "%s%s" % ( str(number/1_000)[:3], suffix )

    if (suffix == 'k'):
        new_suffix = 'm'
    else:
        new_suffix = 'b'

    return compactedNumber(number/1000, new_suffix)

#gets the information from reddit about the best post with the best comments to post on yt
#verbose dictates whether we get info about the posts on the terminal or not
class RedditScraper(object):
    def __init__( self, verbose, postLimit=200):
        
        self.reddit = praw.Reddit(client_id='nfQRZlBLyLI9EmuUet7ZGQ', client_secret='p5rP0TI75B_89hDZL1CYXytIbh7xaQ', user_agent='bomboRombo')
        self.verbose = verbose

        self.minUpvotes = config.subredditPreset.minUpvotes

        self.lang = config.languageSetting.id
        self.useComments = config.subredditPreset.useComments

        self.badWordsList = []
        self.loadBadWords()

        #don't pay attention to this
        self.usedFileLines = open(threadsUsedPath, "r").readlines()
        self.unusedFileLines = open(threadsNotUsedPath, "r").readlines()

        self.postNumber = len(self.usedFileLines)
        self.threadsUsed = self.postNumber + len(self.unusedFileLines)

        self.subreddit = self.reddit.subreddit(config.subredditPreset.name)
        self.sortingType = sortingFunctionTypes.get(config.subredditPreset.sortingType)
        self.timeFilter = timeFilters.get(config.subredditPreset.timeFrame)

        self.postLimit = postLimit
    
    def getSubredditIcon(self):
        return self.retrieveIcon(self.subreddit, -1, True)

    def addBestPost(self, id):
        
        submission = self.reddit.submission(id=id)
        
        self.bestPost = RedditPost(submission)

        self.findTextFromBestPost()
        self.cleanText()

        self.bestPost.text = self.textToRead

        self.bestPost = config.setupTextDisplayed(
            self.bestPost, config.font, config.subredditPreset.numberOfLines, 
            config.subredditPreset.numberOfSentences
        )

    def findPosts(self):
        sortingFunction = getattr(self.subreddit, self.sortingType)

        #hot, new and rising don't have a time filter
        try:
            self.posts = sortingFunction(limit=self.postLimit+self.threadsUsed, time_filter=self.timeFilter)
        except TypeError as e:
            self.posts = sortingFunction(limit=self.postLimit+threadsUsed)
        
        self.posts = list(self.posts)[self.threadsUsed:]

        self.findBestPost()
        self.findTextFromBestPost()
        self.cleanText()

        self.bestPost.text = self.textToRead

        self.bestPost = config.setupTextDisplayed(
            self.bestPost, config.font, config.subredditPreset.numberOfLines, 
            config.subredditPreset.numberOfSentences
        )
 
    def loadBadWords(self):
        file = open("./data/badWords.txt", "r")
        self.badWordsList = [ line.strip("\n") for line in file.readlines() ]

    #checks if the post is good enough/valid for video
    def checkValidity(self,redditPost):

        post = redditPost.post

        if not self.useComments:
            wordCount = len((prepTitle(post.title) + " " + post.selftext).split(" "))
            ratio = wordCount / (config.ttpRate * config.videoDuration/60)
            #add the extra time thingy here
            if ratio > 0.66 and ratio < 1 and (post.score > 200 or post.stickied):
                return True
            else:
                return False

        comments = post.comments

        if not (len(comments) > config.maxCommentNb*2 and 
                post.score > self.minUpvotes):

            return False


        for comment in comments:

            if (isinstance(comment, MoreComments)):
                break

            if len(comment.body.split(" ")) > config.ttpRate/config.maxCommentNb and (comment.score > self.minUpvotes//5 or comment.stickied) and not ("i am a bot" in comment.body.lower()) and comment.body.count("http") < 2:
                redditPost.comments.append(comment)

            #rep:3, coeff:0.8
            #ignore atm, bonus thingy 
            # if len(comment.replies) > 0:
            #     if (comment.replies[0].score > comment.score*0.0):
            #         redditPost.comments.append([comment, comment.replies[0]])
            
            #for safety
            if len(redditPost.comments) > config.maxCommentNb:
                return True

        return False

    def isPostNotUsed(self, post):
        #just for testing
        #return True

        postTitle = prepTitle(post.title)

        for thread in self.usedFileLines:

            if (thread.strip('\n') == postTitle):
                return False
        
        for thread in self.unusedFileLines:
            if (thread.strip('\n') == postTitle):
                return False

        return True
        
    #finds the most interesting post 
    def findBestPost(self):

        self.bestPost = None

        #gets best post
        for post in self.posts:
            redditPost = RedditPost(post)
            postTitle = prepTitle(post.title)

            if self.verbose:
                print('\nPost : %s, Upvotes: %s' % (postTitle, post.score))

            if ( self.isPostNotUsed(post) ):
                if (self.checkValidity( redditPost )):
                    self.bestPost = redditPost

                    file = open(threadsUsedPath, "a")
                    file.write(postTitle + '\n')
                    file.close()

                    return
            
                else:
                    file = open(threadsNotUsedPath, "a")
                    file.write(postTitle + '\n')
                    file.close()

        print("Post matching the conditions hasn't been found.")
        
    #gets the comment content of the post in question
    def findTextFromBestPost(self):

        if (self.bestPost == None):
            return None

        self.textToRead = config.translateText(prepTitle(self.bestPost.post.title), self.lang) + config.guard
        maxTextLength = config.averageNumberOfLetters * ( config.ttpRate * config.videoDuration/60 )

        self.addSubmissionData(self.bestPost.post, 0)

        if not self.useComments:
            self.textToRead += config.translateText(self.bestPost.post.selftext, self.lang)

            self.addSubmissionData(self.bestPost.post, 1)

            if (self.verbose):
                print( self.textToRead.replace(config.guard, '\n--'))

            return

        for commentNumber in range(len(self.bestPost.comments)):

            comment = self.bestPost.comments[commentNumber]

            if ( isinstance(comment, list) ):
                text = ""

                #simple guard atm
                for subCommentIndex, subComment in enumerate(comment):
                    self.addSubmissionData(subComment, commentNumber + subCommentIndex + 1)

                    text += config.translateText(subComment.body, self.lang)
                    text += config.guard
                
                    if subCommentIndex > 0:
                        text += config.guard[-1]

                    if (len(self.textToRead + text) < maxTextLength):
                        self.textToRead += text 
                        self.textToRead += config.guard

            #fix this
            elif ((len(self.textToRead + comment.body) - len(config.guard)*commentNumber) < maxTextLength):
                
                self.addSubmissionData(comment, commentNumber+1)
                
                self.textToRead += config.translateText(comment.body, self.lang)
                self.textToRead += config.guard
            

        if (self.verbose):
            print( self.textToRead.replace(config.guard, '\n--'))

            return
    
    def addSubmissionData(self, submission, submissionId):
        self.bestPost.upvotes.append( compactedNumber( submission.score, 'k' ))
        
        self.bestPost.pfps.append( self.retrieveIcon(submission.author, submissionId) )

        awardPath = "./video/input/reddit_awards/"
        allAvailableAwards = [ awardFileName[:-4] for awardFileName in os.listdir(awardPath) ]

        self.bestPost.awards.append([])

        sortedAwardings = [award for award in sorted(submission.all_awardings, key=lambda award: award.get("coin_price"))]
        sortedAwardings.reverse()

        #get the awards, if the award isn't already saved, download it
        for award in sortedAwardings:
            if not (award.get("id") in allAvailableAwards):
                urllib.request.urlretrieve(award.get("icon_url"), awardPath + award.get("id") + ".png")

            self.bestPost.awards[-1].append(awardPath + award.get("id") + ".png")

    def retrieveIcon(self, prawObj, submissionId, isSubreddit=False):
        pfpPath = "./video/temp/pfp_%d.png" % ( submissionId )

        authorName = "unknown_redditor"
        try:
            authorName = prawObj.display_name if isSubreddit else prawObj.name
        except:
            None

        if not os.path.exists(pfpPath) or isSubreddit:
            try:
                urllib.request.urlretrieve(prawObj.icon_img, pfpPath)
            except:
                pfpPath = "./video/input/images/reddit_bg/test_pfp.png"
        
        return (authorName, pfpPath)

    def cleanText(self):

        #ante is before in latin
        # anteTextToRead = self.textToRead
        # self.textToRead = ""

        # for word in anteTextToRead.split(" "):
        #     #if a word is really similar to a bad word (1 chr difference too)
        #     if any(( (badWord in word) and abs(len(word) - len(badWord)) <= 1 ) for badWord in self.badWordsList):
        #         self.textToRead += censorWord(word)
        #     else:
        #         self.textToRead += word
            
        #     self.textToRead += " "
        
        self.textToRead = asciifyText(self.textToRead)

class RedditPost:
    def __init__(self, post):
        self.post = post

        self.comments = []
        self.pfps = []
        self.upvotes = []
        self.awards = []

        textDisplayed = []
    
    def copy(self):
        copy = RedditPost(self.post)
        copy.comments = self.comments
        copy.pfps = self.pfps
        copy.upvotes = self.upvotes
        copy.awards = self.awards
        copy.textDisplayed = self.textDisplayed

        return copy
    
    def getFullText(self):
        fullText = ""
        for page in self.textDisplayed:
            for line in page.lines:
                fullText += line + " "
            
            fullText += "\n"
        
        return fullText

if __name__ == "__main__":
    config.subredditPreset = config.subredditPresets[0]
    redditScraper = RedditScraper(True).findPosts()
