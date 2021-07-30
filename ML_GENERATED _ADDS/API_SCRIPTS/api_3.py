
import numpy as np
from botocore.exceptions import ClientError
import logging
import cv2 # extract frames from the videos
from PIL import Image  # to manipulate images
import os
import psycopg2
from PIL import Image
import re
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
#from google.colab.patches import cv2_imshow
import pickle
from tqdm import tqdm
import moviepy.editor
# Import everything needed to edit video clips
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, concatenate_audioclips, AudioClip, CompositeAudioClip
from flask import Blueprint, request
import boto3
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
Stich = Blueprint(name='api_3', import_name=__name__)


@Stich.route('/',methods=['GET'])
def hello():
    return '<h1> Hello Split stich</h1>'

@Stich.route('/stich', methods=["POST"])
def train():
    data = request.get_json()
    acc = data['acc']
    videos = data['videos']
    s3 = boto3.client ('s3')
    print('-------------',acc, videos)
    
    counter = 1
    final = []
    for video in videos:
        print('------===----- ',video)
        res = re.match(r'.*?com/(.*mp4)', video)
        name = res.group(1)
        print('-----------',name)

        path = os.getcwd()
        acc_path = os.path.join(path,acc)
        print(acc_path)
        if not os.path.exists(acc_path):
            os.makedirs(acc_path)
        
        try:
            s3.download_file('blkbox-machinelearning',name,'{}/vid_{}.mp4'.format(acc_path,counter))
            print('Downloaded')
        except Exception as e:
            print('############',e,'#########')
        
              
        video = VideoFileClip('{}/vid_{}.mp4'.format(acc,counter))
        print(video.size)
        #video = video.resize( (height,width))
        video = video.audio_fadein(2.0)
        video = video.audio_fadeout(2.0)
        final.append(video)
        counter += 1

    print('+++++ final',final)
        
    final_video= concatenate_videoclips(final)
    final_video.write_videofile(f'video_merge1.mp4')
    s3 = boto3.client('s3')
    s3.upload_file('video_merge1.mp4','blkbox-machinelearning','Model_files/{}/video_merge.mp4'.format(acc))
    
    url = 'https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/Model_files/{}/video_merge.mp4'.format(acc)
    return {'val':"success","url":url}

@Stich.route('/start_scenes', methods=["GET"])
def start():
    data = request.get_json()
    acc = data['acc']
    print('acc---------', acc)
    s3 = boto3.resource('s3')
    ## Bucket to use
    bucket = s3.Bucket('blkbox-machinelearning')
    
    path = "Model_files/{}/start".format(acc)
    contents = [_.key for _ in bucket.objects.all() if path in _.key]
    #print('-----------',contents)
    final_data = []
    url = 'https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/'
    for i in contents:
        final_data.append(url+i)
    
    os.system('rm -rf {}'.format(acc_path))

    return {"val":"success","output":final_data}