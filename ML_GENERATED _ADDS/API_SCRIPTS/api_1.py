import numpy as np
import cv2 # extract frames from the videos
from PIL import Image  # to manipulate images
import os
import psycopg2

from tensorflow.keras.applications import DenseNet201
from tensorflow.keras.preprocessing.image import load_img,img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.applications.imagenet_utils import preprocess_input

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

import pickle
import moviepy.editor
# Import everything needed to edit video clips
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, concatenate_audioclips, AudioClip, CompositeAudioClip

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


from scenedetect import VideoManager, SceneManager
from scenedetect.video_splitter import split_video_ffmpeg
from scenedetect.detectors import ContentDetector

import os, time, glob, psycopg2, re

import pandas as pd
from pathlib import Path
import shutil


import boto3
from pathlib import Path
from flask import Blueprint, jsonify, request

bucket = 'blkbox-machinelearning'
url = 'https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/'
No_of_frames = 10

Train = Blueprint(name='api_1', import_name=__name__)

@Train.route('/',methods=['GET'])
def hello():
	return '<h1> Hello Split stich</h1>'

@Train.route('/train',methods=['GET'])
def train():
    start = time.time()
    data = request.get_json()
    acc = data['acc']
    s3 = boto3.client('s3')
    path = '/home/ubuntu/blkbox-ds/Creative_Production'
    #print(path)
    acc_dir = os.path.join(path, acc)
    video_dir = os.path.join(acc_dir,'Videos')
    
    if not os.path.exists(acc_dir):
        os.makedirs(acc_dir)
        os.makedirs(video_dir)
    else:
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
    
    result = s3.list_objects(Bucket = bucket, Prefix='Videos/{a}/'.format(a=acc)).get('Contents')

    video_count = 0
    for obj in result:
        new_url = str(url + obj['Key'])
        print(new_url)
        title = re.match('Videos/.*?/(.*?mp4)', obj['Key'])
        title = title.group(1)
        files = os.listdir(video_dir)
        if title not in files:
            s3.download_file(bucket, obj['Key'], '{}/Videos/{}'.format(acc,title))
            video_count +=1
    

    files = os.listdir(video_dir)
    video_files_path = []
    for i in files:
        video_files_path.append(video_dir+'/'+ i)
        
    def find_scenes(video_paths, threshold):
	    video_manager = VideoManager([video_paths])
	    scene_manager = SceneManager()    
	    scene_manager.add_detector(ContentDetector(threshold=threshold))    
	    video_manager.set_downscale_factor()    
	    video_manager.start()    
	    scene_manager.detect_scenes(frame_source = video_manager)   
	    return scene_manager.get_scene_list()

    def split_scenes(video_paths, scene_list, name):
        split_path = os.path.join(acc_dir + '/splits')
        if not os.path.exists(split_path):
            os.makedirs(split_path)
        os.chdir(split_path)
        file_path = os.path.join(split_path +'/'+ name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        os.chdir(file_path)
        split_video_ffmpeg([video_paths], scene_list = scene_list,
			output_file_template = '$VIDEO_NAME - Scene $SCENE_NUMBER.mp4', video_name = name)
        return True
    def check_video_threshold(video_path):
        # Create an object by passing the location as a string
        video_len = VideoFileClip(video_path)
        # getting duration of the video
        video_duration = int(video_len.duration)
        if video_duration <= 15:
            threshold = 45.00
        elif video_duration > 15 & video_duration < 30:
            threshold = 30.00
        return threshold

    counter = 0
    for video in video_files_path:
        thres = check_video_threshold(video)        
        scenes = find_scenes(video, thres)        
        split_scenes(video, scenes, files[counter])
        counter +=1
    
    folders = ['start','mid','end']
    
    for i in folders:
        f_paths = os.path.join(acc_dir, i)
        print(f_paths)
        if not os.path.exists(f_paths):
            os.makedirs(acc_dir+'/'+i)
    
    split_path = os.path.join(acc_dir + '/splits')
    

    videos = os.listdir(video_dir)
    
    split_path = Path(split_path)
    
    for i in range(len(videos)):
        filepaths = list(pd.Series(list(split_path.glob(r'{}/*.mp4'.format(videos[i]))), name='Filepath').astype(str))
        filepaths.sort()
        
        try:
            start_path = acc_dir + '/start'
            shutil.copy(filepaths[0], start_path)

            end_path = acc_dir + '/end'
            shutil.copy(filepaths[-1], end_path)

            filepaths = filepaths[1:-1]
            mid_path = acc_dir + '/mid'
            for f in filepaths:
                shutil.copy(f, mid_path)
        except Exception as e:
            print(e)

    start_files = [start_path + x for x in os.listdir(start_path) if ".mp4" in x]
    mid_files = [mid_path +'/'+ x for x in os.listdir(mid_path) if ".mp4" in x]
    end_files = [end_path +'/'+ x for x in os.listdir(end_path) if ".mp4" in x]

   
    
    # load the model
    dense_model = DenseNet201(weights='imagenet')
    # remove the last layers in order to get features instead of predictions
    feat_extractor = Model(inputs=dense_model.input, outputs=dense_model.get_layer("avg_pool").output)

    def global_performance(clip_name):
        conn = psycopg2.connect(user = "ds_readonly", password = "blkbox2020!",host = "db.blkbox.ai",port = "5432",database = "blkbox")
        sql = ("select sum(distinct(global_performance)) as global_performance "   
	        "from fb_app_assets "
	        "where asset_name like '%{a}%' and asset_type = 'VIDEO' "
	        "order by global_performance desc; ".format(a=clip_name))
        data = pd.read_sql_query(sql, conn)
        conn = None
        return max(data.global_performance,default=0)
        
    def all_video_ar(video):
        clip = VideoFileClip(video)
        clip = clip.subclip(0,5)
        value = clip.size
        return value
    
    def performance_df(files,section):
        counter = 0
        performance = []
        video_name_list = []
        dimension = []
        for video in files:
            
            s1 = video
            s2 = "{a}/".format(a=section)
            s3 = " - Scene"
            name = s1[s1.index(s2) + len(s2):s1.index(s3)]
            video_name_list.append(name)
            performance.append(global_performance(name))
            dimension.append(all_video_ar(video))
        df = pd.DataFrame(list(zip(video_name_list, files, performance, dimension)),columns =['video_name','files_path','performance','dimension'])
        return df

    df_mid_performance = performance_df(mid_files, 'mid')
    df_end_performance = performance_df(end_files, 'end')
    df_mid_performance['performance'] = df_mid_performance['performance'].fillna(0)
    df_end_performance['performance'] = df_end_performance['performance'].fillna(0)

    
    model_path = acc_dir + '/model_files'
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    df_mid_performance.to_csv('{}/mid_data.csv'.format(model_path))
    df_end_performance.to_csv('{}/end_data.csv'.format(model_path))
    
    ########################################
    def feature_extractor(files):
        importedvideos = []
        # load all the images and prepare them for feeding into the CNN
        counter = 0
        for video in files:
            print('----',video)
            frames = []
            count = 1
            path = video
            cap = cv2.VideoCapture(path)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            temp = length / No_of_frames
            ret = True
            while ret:
                ret, img = cap.read() # read one frame from the 'capture' object; img is (H, W, C)
                if ret:
                    img = cv2.resize(img, (224, 224))
                    frames.append(img)
                    count += temp
                    cap.set(1,count)
                else:
                    cap.release()
                    break
            video_frames = np.stack(frames, axis=0)
            # extract the images features
            imgs_features = feat_extractor.predict(video_frames)
            print("features successfully extracted!")
            #print(imgs_features.shape)
            flatten_img_features = imgs_features.flatten()
            flatten_img_features = np.expand_dims(flatten_img_features,axis = 0)
            #print(flatten_img_features.shape)
            importedvideos.append(flatten_img_features)
        videos_array = np.vstack(importedvideos)
        return videos_array
        
        
    # videos_mid_train = feature_extractor(mid_files)
    # np.save(f'/home/jignesh/blkbox/blkbox-ml-master/split_stich/{acc}/model_files/videos_mid_train-{height}*{width}', videos_mid_train)
    
    # videos_end_train = feature_extractor(end_files)
    # np.save(f'/home/jignesh/blkbox/blkbox-ml-master/split_stich/{acc}/model_files/videos_end_train-{height}*{width}', videos_end_train)

    #######################################
    model_path = acc_dir + '/model_files'
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    videos_end_train = feature_extractor(end_files)
    np.save('/{}/videos_end_train'.format(model_path), videos_end_train)

    file_name = '{}/data_files_end'.format(model_path)
    open_file = open(file_name, "wb")
    pickle.dump(end_files, open_file)
    open_file.close()

    videos_mid_train = feature_extractor(mid_files)
    np.save('/{}/videos_mid_train'.format(model_path), videos_mid_train)

    
    file_name = '{}/data_files_mid'.format(model_path)
    open_file = open(file_name, "wb")
    pickle.dump(mid_files, open_file)
    open_file.close()

    # with open(file_name, "rb") as pickle_file:
    #     files_mid = pickle.load(pickle_file)
    #     open_file.close()
    # print(files_mid)
    
    end = time.time()

    os.system('rm -rf /home/ubuntu/blkbox-ds/Creative_Production/{}/Videos'.format(acc))
    os.system('aws s3 cp /home/ubuntu/blkbox-ds/Creative_Production/{a}/ s3://blkbox-machinelearning/Model_files/{a} --recursive'.format(a = acc))
    os.system('rm -rf /home/ubuntu/blkbox-ds/Creative_Production/{}'.format(acc))
    total = end - start




    return {"val":"succeess", "time":total, "videos":video_count}