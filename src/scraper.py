#! python3
import praw
import pyttsx3


subreddit_NAME = "AskReddit"
min_comment_Nb = 1_000
RATE = 150

#average number of letters/word in english
AVG_Letters = 4.7

#total duration of the tts
total_time = 0
final_script = ""



#insitialising the tts engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', RATE)
tts_engine.setProperty('voice', tts_engine.getProperty('voices')[2].id)

#getting the slurs in string format from the file
slurs = [word[:-1] for word in open(r"C:\Users\GT\Desktop\Projects\RedditBombo\utilities\meanies.txt","r").readlines()]


#credentials are in the file for security purposes
token_file = open(r"C:\Users\GT\Desktop\Projects\RedditBombo\utilities\token.token","r")
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
subreddit = reddit.subreddit(subreddit_NAME)

#getting the hottest 5 threads
hot_subreddit = subreddit.hot(limit=5)

#finding a submission with enough comments to make content with
for submission in hot_subreddit:
    comments = submission.comments

    if len(comments) > min_comment_Nb:
        break

for comment in comments:
    final_script += comment.body
    total_time += (len(comment.body)/AVG_Letters)/RATE

    #if the length of the video is more than 10min
    if total_time > 10:
        break

print(final_script)












    
