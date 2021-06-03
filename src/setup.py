import pyttsx3
import os

def start():
    #languages desired
    languages = ['English (United States)']

    #initialises pyttsx3
    engine = pyttsx3.init()

    #gets folder path
    abs_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
    folderPath = '/'.join(abs_path.split('/')[0:-1])

    #opens the setup.txt for writing
    setupFile = open(folderPath + '/src/setup.txt','w')

    #function yielding the index for the language
    def yieldIndex(lang):
        index = 0

        #looping for every voice
        for voice in engine.getProperty('voices'):        
            if lang in voice.name:
                return str(index)

            index += 1

    #writing the path of the folder on the first line of the file
    setupFile.write(folderPath + '\n')

    #writing the index of the language in languages
    for lang in languages:
        setupFile.write(yieldIndex(lang))

    #closes the file
    setupFile.close()
