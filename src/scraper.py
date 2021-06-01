#! python3
import praw
import pandas as pd
import datetime as dt

token_file = open("token.token","r")
credentials = []

for cred in token_file.readlines():
    credentials.append(cred[:-1])

print(credentials)


reddit = praw.Reddit(client_id='MeGGdun86G8oVQ', \
                     client_secret='2ACmje7EzUozWYsk3MHyV1ZxDzsqjg ', \
                     user_agent='RedBombo', \
                     username='Thing_Left', \
                     password='#Bobmaster01')
