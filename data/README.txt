This project aims to produce a short format video, and post it onto either Youtube or TikTok, provided the correct credentials.

To procure yourself of the credentials for Youtube posting, you should need to have an approved 
project by the Google credentials team, see here for more information : https://developers.google.com/youtube/registering_an_application
Once you have these credentials, you can add them at \VideoPoster\credentials\ directory.

For both websites, you will need an account, and put that account's information (such as the Youtube's ChannelID or TikTok's channel link)
in the file 'data.json' in the /data/ directory.

Once done with this, you can add your own background videos in '\video\input\videosToSplit' and your own background music in 'audio\musicToSplit'.
Thus, you can change the logos, banners, and intro to your liking; the ones provided are examples for the user.

Finally, run the 'setup.py' file to setup your credentials for automatic posting on youtube, and to automatically split the background videos
and music files into more manageable pieces.

Make sure you have Firefox on your machine, so that 'geckodriver.exe' can function normally; otherwise modify the code to make it suitable to Google Chrome.