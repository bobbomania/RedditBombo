import os.path
import setup

abs_path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
folderPath = '/'.join(abs_path.split('/')[0:-1])

#if no setup file exists create one
if not os.path.isfile( folderPath + r'/src/setup.txt' ): setup.start()
