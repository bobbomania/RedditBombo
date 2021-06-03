#! python3
import os
import praw
import pyttsx3
import itertools


class subredditFinder:
    def __init__(self,subredditName,minCommentNb,minUpvotes, avgLetters):

        self.subreddit_NAME = subredditName

        #the minimum number of comments in a subreddit
        self.min_comment_Nb = minCommentNb
        
        #the minimum amount of upvotes for a subreddit
        self.minUpvotes = minUpvotes

        #the rate of speech of the tts
        self.RATE = 150

        #the final list with the comments and the submission and its body content
        self.final_list = []
        self.final_script = ""

        
        #average number of letters/word in english
        self.AVG_Letters = avgLetters
        
    def getTTS(self):
        #total duration of the tts
        total_time = 0

        #the path of the folder of the reddit Bombo
        data_setup = open('setup.txt','r').readlines()

        #folder path from data setup file
        folderPath = data_setup[0]

        #the language index from pyttsx3
        langIndex = data_setup[1]

        #script for the tts
        self.final_script = ""

        #insitialising the tts engine
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', self.RATE)
        tts_engine.setProperty('voice', tts_engine.getProperty('voices')[langIndex].id)

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
                
            self.final_script += commentBundleBody + ".........."
            total_time += (len(commentBundleBody)/self.AVG_Letters)/self.RATE

            #if the length of the video is more than 10min
            if total_time > 10:
                break
                
            #find slurs and remove any repeated letters for tts

        #checking for swear words
        #to refine with a better list
        ##for slur in slurs:
        ##    #if the isolated slur is present replace it with a space
        ##    if (' ' + slur + ' ') in final_script.lower():
        ##        final_script = final_script.replace(slur,' '*len(slur))
        ##        
        print(self.final_script)
        print(f'{folderPath}/output/tts/{self.subreddit_NAME} {len(os.listdir( folderPath + "/output/tts/" ))}.mp3')
        tts_engine.save_to_file(self.final_script, f'{folderPath}/output/tts/{self.subreddit_NAME}{len(os.listdir( folderPath + "/output/tts/" ))}.mp3')
        tts_engine.runAndWait()

        return self.final_list

askReddit = subredditFinder("AskReddit",40,1_000,4.7)
askReddit.getTTS()



