
import os
#os.system("start cmd /K cd C:\\Users\\gurdit\\Desktop\\BLK_WORK\\viddo")
import subprocess
import pandas as pd
from pathlib import Path
#cmp=subprocess.Popen('cmd /k "cd C:\\Users\\gurdit\\Desktop\\BLK_WORK\\viddo & scenedetect -i HoV_CreativeWorkshopConcept1Liveaction_V33399_30_English_Portrait_IMG=P.mp4 -o result detect-content -t 30 detect-threshold -t 12 split-video" ')
image_dir = Path('C:\\Users\\gurdit\\Desktop\\BLK_WORK\\viddo')
filepaths = pd.Series(list(image_dir.glob(r'**/*.mp4')), name='Filepath').astype(str)
a=filepaths
print(a[0].split('\\')[-1])
counter=1
for i in range(0,len(a)):
    name=a[i].split('\\')[-1]
    cmp=subprocess.Popen('cmd /k "cd C:\\Users\\gurdit\\Desktop\\BLK_WORK\\viddo & scenedetect -i {} -o result_{} detect-content -t 30 detect-threshold -t 12 split-video"'.format(name,counter))
    counter+=1

