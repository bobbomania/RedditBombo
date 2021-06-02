#! python3
import os
import praw
import pyttsx3
import itertools


class subredditFinder:
    def __init__(self,subredditName,minCommentNb,minUpvotes, avgLetters):

        self.subreddit_NAME = subredditName
        self.min_comment_Nb = minCommentNb
        self.minUpvotes = minUpvotes
        self.RATE = 150

        self.final_list = []
        self.final_script = ""

        
        #average number of letters/word in english
        self.AVG_Letters = avgLetters
        
    def getTTS(self):
        #total duration of the tts
        total_time = 0

        #the path of the folder of the reddit Bombo
        folderPath = '\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[0:-1])

        #script for the tts
        self.final_script = ""

        #insitialising the tts engine
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', self.RATE)
        tts_engine.setProperty('voice', tts_engine.getProperty('voices')[2].id)

        #getting the slurs in string format from the file
        slurs = [word[:-1] for word in open(folderPath + "\\utilities\\meanies.txt","r").readlines()]


        #credentials are in the file for security purposes
        token_file = open(folderPath + "\\utilities\\token.token","r")
        credentials = []

        for cred in token_file.readlines():
            credentials.append(cred[:-1])

        #creating reddit connection
        reddit = praw.Reddit(client_id=credentials[0], \
                             client_secret=credentials[1], \
                             user_agent=credentials[2], \
                             username=credentials[3], \
                             password=credentials[4])

        #finding subreddit
        subreddit = reddit.subreddit(self.subreddit_NAME)

        #getting the hottest 5 threads
        hot_subreddit = subreddit.hot(limit=5)

        #finding a submission with enough comments to make content with
        for submission in hot_subreddit:
            print(submission.title)
            comments = submission.comments
            
            if len(comments) > self.min_comment_Nb and submission.score > self.minUpvotes:
                self.final_list.append([submission])
                self.final_script += submission.title
                break


        #finding interesting comments from the submission
        for comment in comments:

            #the Comment Object/ Objects as it can take into account a reply
            commentBundle = [[]]
            commentBundleBody = ''
            
            #if the comment in less than 30 words long look for relevant replies
            if len(comment.body)/self.AVG_Letters < 30:
                try:
                    commentBundle = [comment,comment.replies[0]]
                except:
                    commentBundle = [comment]
                    continue
            else:
                commentBundle = [comment]

            self.final_list.append(commentBundle)

            for e in commentBundle:
                #removes adjacent repeated letters and \n
                commentBundleBody += ''.join(c[0] for c in itertools.groupby(e.body.strip('\n')))
                
            self.final_script += commentBundleBody
            total_time += (len(commentBundleBody)/self.AVG_Letters)/self.RATE

            #if the length of the video is more than 10min
            if total_time > 10:
                break
                
            #to do adding spacing and punctuation to tts
            #find slurs and remove any repeated letters for tts

        #checking for swear words
        #to refine with a better list
        ##for slur in slurs:
        ##    #if the isolated slur is present replace it with a space
        ##    if (' ' + slur + ' ') in final_script.lower():
        ##        final_script = final_script.replace(slur,' '*len(slur))
        ##        
        print(self.final_script)


askReddit = subredditFinder("AskReddit",40,1_000,4.7)
askReddit.getTTS()



