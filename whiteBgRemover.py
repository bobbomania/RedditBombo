from PIL import Image
from numpy import array 

import os

import cv2

def removeBgImage(image, color=(255,255,255)):
    img = image.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if 30 > item[0] - color[0] >= 0 and 30 > item[1] - color[1] >= 0 and 30 > item[2] - color[2] >= 0:
            newData.append((color[0], color[1], color[2], 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def removeBgFromVideo(videoPath, color=(255,255,255)):
    video = cv2.VideoCapture(videoPath)

    videoOutputDir = './video/input/constantVideos/addons/' + videoPath.split("/")[-1][:-4] + "/"

    if not (os.path.isdir(videoOutputDir)):
        os.mkdir(videoOutputDir)

    for i in range(int(video.get(7))):
        ret, frame = video.read()
        if ret:
            # Convert the image to RGB (OpenCV uses BGR)  
            cv2_im_rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)  
            
            # Pass the image to PIL  
            pil_im = Image.fromarray(cv2_im_rgb)  
            pil_im = removeBgImage(pil_im, color)

            frame = cv2.cvtColor(array(pil_im), cv2.COLOR_RGB2BGRA)
            #frame = cv2.resize(frame, (int(frame.shape[0]*0.5), int(frame.shape[1]*0.5)))

            cv2.imwrite(videoOutputDir + str(i) + ".png", frame)

    video.release()   
    cv2.destroyAllWindows()

if __name__ == "__main__":
    videoPath = "./video/input/images/ball.mp4"
    color = (0,0,0)
    
    if len(color) == 0:
       color = (255,255,255)
       
    #try:
    removeBgFromVideo(videoPath, color)
    #except:
      # print(f"{videoPath} has not been found.")