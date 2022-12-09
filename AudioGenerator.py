import pyttsx3
import os
import data.config as config
import regex as re

from pydub import AudioSegment
AudioSegment.converter = "C:/Users/spont/Documents/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "C:/Users/spont/Documents/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/Users/spont/Documents/ffmpeg/bin/ffprobe.exe"

languages = { "en" : 8, "fr" : 5, "de" : 7, "es" : 3 }
 
#generates audio text to speech given an input text, rate of speech and voice (default is James)
class AudioGenerator(object):
    def __init__(self, textDisplayed, ttpRate=config.ttpRate):
        self.textDisplayed = textDisplayed
        self.ttpRate = ttpRate
        self.voiceId = languages.get(config.languageSetting.id)
        self.hasPause = config.subredditPreset.hasPause
        self.extraContent = ""

        self.totDuration = 0

        self.engine = pyttsx3.init(driverName='sapi5')  # object creation
        
        self.initialiseEngine()
    
    def initialiseEngine(self):
        self.engine.setProperty('rate', self.ttpRate)     # setting up new voice rate
        #engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

        """VOICE"""
        voices = self.engine.getProperty('voices')       #getting details of current voice
        self.engine.setProperty('voice', voices[self.voiceId].id)   #changing index, changes voices. 1 for female

    def primeText(self, text):
        
        text = text.replace("*", " ")
        text = re.sub('[\.\_\-]','', text)
        text = text.replace('etc', 'etcetera')

        return text
    
    
    def trimSilence(self, sound, silence_threshold=-50.0, chunk_size=10):
        trim_ms = 0 # ms

        assert chunk_size > 0 # to avoid infinite loop
        while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size

        return trim_ms

    def saveAudio(self, fileName, post):

        dirPath =  './video/temp/%s/' % fileName

        if not (os.path.isdir( dirPath )):
            os.mkdir(dirPath)
        
        #clear directory if not used
        else:
            config.emptyDirectory(dirPath)

        commentNb = 0
        allComments = AudioSegment.empty()

        #one second pause
        pauseAudio = AudioSegment.from_file( "./audio/constant audio/pause.mp3", format = 'mp3' )[:config.pauseLength*1000]

        for page in self.textDisplayed:

            pageContent = "".join([self.primeText(line) for line in page.lines])

            commentAudioPath = dirPath + 'audio%d.mp3' % commentNb
            self.engine.save_to_file(pageContent, commentAudioPath)
            self.engine.runAndWait()

            commentAudio =  AudioSegment.from_file( commentAudioPath )
             
            startTrim = self.trimSilence(commentAudio)
            endTrim = self.trimSilence(commentAudio.reverse())

            commentAudio = commentAudio[startTrim:-endTrim]
            
            if (page.isStartOfComment or len(allComments) > 0):
                commentAudio = pauseAudio + commentAudio

            allComments +=  commentAudio

            #accounts for pause
            page.duration = len(commentAudio)/1000
            self.totDuration += page.duration
            commentNb += 1

            #always pause btw first post and the rest of the content
            if (not self.hasPause):
                pauseAudio = AudioSegment.empty()

            pageIndex = self.textDisplayed.index(page) - 1

            #if too much text to still display and not enough time, display it all on a last page
            if self.totDuration >= config.maxVideoDuration:

                for page in self.textDisplayed[pageIndex:]:
                    if page.isStartOfComment:
                        break

                    for line in page.lines:
                        self.extraContent += line if line != "" else "\n"

                if self.extraContent == "":
                    break

                tempPost = post.copy()
                tempPost.text = self.extraContent
                page = config.setupTextDisplayed(tempPost, config.font, config.maxLines, 500).textDisplayed[0]
                page.duration = int(config.maxVideoDuration - self.totDuration - page.duration) + 3
                post.textDisplayed = post.textDisplayed[:pageIndex]
                post.textDisplayed.append(page)

                break

        #we don't need the audio snippets anymore
        config.emptyDirectory(dirPath)

        self.engine.stop()
        allComments.export(dirPath + fileName + '.mp3', format="mp3")

        return post
    
    def testAudio(self, testText):
        self.engine.say(testText)
        self.engine.runAndWait()
        self.engine.stop()

if __name__ == "__main__":
    text = "Hello." + config.guard + "my name is" + config.guard + "baba, etc."
    audioGen = AudioGenerator(None, lang="en")
    audioGen.testAudio(text)
