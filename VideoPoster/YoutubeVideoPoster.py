import http.client as httplib
import httplib2
import os
import random
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import argparse

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'C:/Users/spont/Documents/Projects/General/Python/RedditBombo2/data')
import config

if __name__ == "__main__":
    from VideoObject import getAllVideoObejcts
else:
    from VideoPoster.VideoObject import getAllVideoObejcts


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "./VideoPoster/client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload  https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "Config the client.json file, look at https://developers.google.com/youtube/v3/guides/uploading_a_video"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def getChannelCredentials():
    # run an OAuth flow; then obtain credentials data
    # relative to the channel the app's user had chosen
    # during that OAuth flow
    from google_auth_oauthlib.flow import InstalledAppFlow
    scopes = ['https://www.googleapis.com/auth/youtube', "https://www.googleapis.com/auth/youtube.force-ssl"]
    flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes)
    cred = flow.run_console()

    # build an YouTube service object such that to
    # be able to retrieve the ID of the channel that
    # the app's user had chosen during the OAuth flow
    from googleapiclient.discovery import build
    youtube = build('youtube', 'v3', credentials = cred)
    response = youtube.channels().list(
        part = 'id',
        mine = True
    ).execute()

    for channel in response['items']:
        channelId = channel['id']
        print(channelId)

        # save the credentials data to a JSON text file
        cred_file = f".\VideoPoster\credentials\{channelId}.json"
        with open(cred_file, 'w', encoding = 'UTF-8') as json_file:
            json_file.write(cred.to_json())

class YoutubeVideoPoster(object):
    def __init__(self, videos):
        self.videos = videos

    def get_authenticated_service(self, channelId):
        # read in the credentials data associated to
        # the channel identified by its ID 'channel_id'
        from google.oauth2.credentials import Credentials
        cred_file = f".\VideoPoster\credentials\{channelId}.json"
        credentials = Credentials.from_authorized_user_file(cred_file)

        # the access token need be refreshed when
        # the previously saved one expired already
        from google.auth.transport.requests import Request
        #assert credentials and credentials.valid and credentials.refresh_token
        if credentials.expired:
            credentials.refresh(Request())
            # save credentials data upon it got refreshed
            with open(cred_file, 'w', encoding = 'UTF-8') as json_file:
                json_file.write(credentials.to_json())

        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            credentials=credentials)

    def initialize_upload(self, youtube, options):
        tags = None
        if options.keywords:
            tags = options.keywords.split(",")

        body=dict(
            snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
            ),
            status=dict(
            privacyStatus=options.privacyStatus
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
        )

        self.resumable_upload(insert_request)

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        self.id = response['id']
                        print("Video id '%s' was successfully uploaded." % self.id)
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:/n%s" % (e.resp.status,
                                                                        e.content)
                else:
                    raise

            except RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)
        
    def addComment(self, youtube, commentText, ytVideoId,channelId):

        request = youtube.commentThreads().insert(
                part="snippet",
                body={
                "snippet": {
                    "channelId" : channelId,
                    "topLevelComment": {
                    "snippet": {
                        "textOriginal": commentText
                    }
                    },
                    "videoId": ytVideoId
                    }
                }
            )
        
        request.execute()
        
    def postVideos(self):
        for video in self.videos:
            self.postVideo(video)

    def postVideo(self, video):

        description = (
            'Uploading a Youtube Video.'
        )

        parser = argparse.ArgumentParser(
                description=description,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[argparser])

        parser.add_argument("--file", help="Video file to upload", default=video.videoPath)
        parser.add_argument("--title", help="Video title", default=video.videoTitle + " #" + video.videoTags.replace(","," #"))
        parser.add_argument("--description", help="Video description",default=video.videoDescription)
        parser.add_argument("--category", default="24",
        help="Numeric video category. " +
            "See https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=en&key=YOUR_API_KEY")
        parser.add_argument("--keywords", help="Video keywords, comma separated",
        default=video.videoTags)
        parser.add_argument("--safeSearch", help="video restrictions : none, moderate, strict", default="moderate")
        parser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
        default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
        
        args = parser.parse_args()

        if not os.path.exists(args.file):
            exit("Please specify a valid file using the --file= parameter.")

        youtube = self.get_authenticated_service(video.languageSetting.ytChannelId)
        try:
            self.initialize_upload(youtube, args)
        except HttpError as e:
            print("An HTTP error %d occurred:/n%s" % (e.resp.status, e.content))
    
        commentText = "Thank you all for watching!\n%sFor similar content, feel free to subscribe and drop a like; but more importantly, have a nice day!" % ("If you want more of this, check out this submission at this link:\n" + video.postLink + "\n" if len(video.postLink) > 0 else "")
        commentText = config.translateText(commentText, video.languageSetting.id)
        self.addComment(youtube, commentText,self.id,video.languageSetting.ytChannelId)
        
        if len(video.extraContent) > 0:
            commentText =  "Here's the rest of the submission :\n" + '"%s"\n' % video.extraContent + "\nSorry for cutting out the video, it couldn't all fit in the Shorts."
            commentText = config.translateText(commentText, video.languageSetting.id)
            self.addComment(youtube, commentText,self.id,video.languageSetting.ytChannelId)

if __name__ == '__main__':
    videos = getAllVideoObejcts()
    poster = YoutubeVideoPoster(videos)
    poster.postVideos()
    #getChannelCredentials()