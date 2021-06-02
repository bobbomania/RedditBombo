#! python3
import praw
import pyttsx3
import itertools


subreddit_NAME = "AskReddit"
min_comment_Nb = 20
minUpvotes = 1_000
RATE = 150

#average number of letters/word in english
AVG_Letters = 4.7

#total duration of the tts
total_time = 0

#list containing all the comment objects + submission
final_list = []

#script for the tts
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
    print(submission.title)
    comments = submission.comments
    
    if len(comments) > min_comment_Nb and submission.score > minUpvotes:
        final_list.append([submission])
        final_script += submission.title
        break


#finding interesting comments from the submission
for comment in comments:

    #the Comment Object/ Objects as it can take into account a reply
    commentBundle = [[]]
    commentBundleBody = ''
    
    #if the comment in less than 30 words long look for relevant replies
    if len(comment.body)/AVG_Letters < 30:
        try:
            commentBundle = [comment,comment.replies[0]]
        except:
            commentBundle = [comment]
            continue
    else:
        commentBundle = [comment]

    final_list.append(commentBundle)

    for e in commentBundle:
        #removes adjacent repeated letters and \n
        commentBundleBody += ''.join(c[0] for c in itertools.groupby(e.body.strip('\n')))
        
    final_script += commentBundleBody
    total_time += (len(commentBundleBody)/AVG_Letters)/RATE

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
print(final_script)

