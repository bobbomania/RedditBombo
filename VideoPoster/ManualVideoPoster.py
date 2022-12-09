import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pyautogui
import pyperclip
from PIL import ImageGrab

if __name__ == "__main__":
    import VideoObject as VideoObject
else:
    import VideoPoster.VideoObject as VideoObject


mailAddress = "redditbombo@gmail.com"
password = "#Bobmaster01"


class ManualVideoPoster(object):
    def __init__(self, videos):
        self.videos = videos
        pyautogui.hotkey('win','ctrl','right')

    def postAllYoutubeVideos(self):
        self.postYoutubeVideos(self.videos)

    def postYoutubeVideos(self, videos):

        self.browser = uc.Chrome(use_subprocess=True)
        self.browser.maximize_window()

        ytChannel = "https://studio.youtube.com/channel/UC-_DHfN1Sp4I3bSN3VjYttw/videos"

        self.browser.get(ytChannel)
        self.browser.switch_to.window(self.browser.current_window_handle)
        pyautogui.click()

        #logs-in into youtube studio, the \\n is to "enter" these in the search boxes
        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(mailAddress + "\n")
        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.NAME, 'password'))).send_keys(password + "\n")

        try:
            for video in videos:

                #clicks upload video button     
                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'create-icon'))).click()
                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'text-item-0'))).click()

                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'select-files-button'))).click()

                time.sleep(2)
                pyautogui.write(video.videoPath) 
                pyautogui.press('enter')

                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'textbox'))).send_keys(video.videoTitle + "")
                
                descriptionBox = WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'description-textarea')))
                descriptionBox.find_elements(By.ID,'textbox')[0].send_keys(video.videoDescription)

                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'toggle-button'))).click()
                
                tagsBox = WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'tags-container')))
                tagsBox.find_elements(By.ID, 'text-input')[0].send_keys(video.videoTags)

                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'step-badge-3'))).click()

                #until the video is not uploaded
                px = ImageGrab.grab().load()

                #while the verify button is disabled
                while px[468, 932] == (96,96,96):
                    px = ImageGrab.grab().load()
                
                time.sleep(5)
                WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.ID, 'done-button'))).click()
                time.sleep(10)

                self.browser.get(ytChannel)
        
        except:
            print("Couldn't post %d videos, daily limit reached." % videos.index(video))

        self.browser.quit()

    def postAllTikTokVideos(self):
        self.postTikTokVideos(self.videos)

    def postTikTokVideos(self, videos):
        self.browser = uc.Chrome(use_subprocess=True)
        self.browser.maximize_window()

        tiktokChannel = "https://www.tiktok.com/upload/"

        #self.browser.get(googleLoginPage)
        self.browser.get(tiktokChannel)
        self.browser.switch_to.window(self.browser.current_window_handle)

        pyautogui.click()

        window_before = self.browser.window_handles[0]

        WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Continue with Google']"))).click()
        
        time.sleep(5)
        window_after = self.browser.window_handles[1]
        self.browser.switch_to.window(window_after)

        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(mailAddress + "\n")
        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.NAME, 'password'))).send_keys(password + "\n")
        time.sleep(5)

        self.browser.switch_to.window(window_before)

        try:
            for video in videos:
                time.sleep(20)

                pyautogui.scroll(1_000)

                pyautogui.moveTo(500,600)
                pyautogui.click()

                time.sleep(2)
                pyautogui.write(video.videoPath) 
                pyautogui.press('enter')

                time.sleep(10)
                pyautogui.moveTo(780,375)
                pyautogui.click()

                tiktokTitle = video.videoTitle + "\n #" + video.videoTags.replace(",","\n #") + "\n"

                #pyautogui doesn't like to write '#'
                pyperclip.copy('#')
                for chr in tiktokTitle:
                    if chr == '#':
                        pyautogui.hotkey('ctrl', 'v')
                    elif chr == '\n':
                        time.sleep(1)
                        pyautogui.press('enter')
                    else:
                        pyautogui.write(chr)

                pyautogui.scroll(-1_000)
                pyautogui.moveTo(950,340)

                px = ImageGrab.grab().load()
                #while the upload button is disabled
                while px[950, 340] == (235,235,235):
                    px = ImageGrab.grab().load()

                pyautogui.click()
                time.sleep(20)
                
                self.browser.get(tiktokChannel)
        
        except:
            print("Couldn't post %d videos, daily limit reached." % videos.index(video))

        self.browser.quit()
    
    def returnToMainDesktop(self):
        pyautogui.hotkey('win','ctrl','left')

if __name__ == "__main__":

    videosToPost = VideoObject.getAllVideoObejcts()
    poster = ManualVideoPoster(videosToPost)

    poster.postTikTokVideo()
    poster.returnToMainDesktop()