import numpy as np
import cv2 # extract frames from the videos
from PIL import Image  # to manipulate images
import os
import psycopg2

from tensorflow.keras.applications import DenseNet201
from tensorflow.keras.preprocessing.image import load_img,img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.applications.imagenet_utils import preprocess_input

from PIL import Image
import os,time, boto3
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
from flask import Blueprint, request, Flask
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

No_of_frames = 10
No_of_mid_scenes = 2
No_of_end_scenes = 1

nb_closest_videos = 1 

################ Model
dense_model = DenseNet201(weights = 'imagenet')
feat_extractor = Model(inputs = dense_model.input, outputs = dense_model.get_layer("avg_pool").output)


Test = Blueprint('api_2', __name__)
@Test.route('/next_scene',methods=["POST"])
def test():
	data= request.get_json()
	vid = data['video']
	#vid = vid
	section = data['section']
	acc = data['acc']
	print('---------',acc, vid, section)

	s3 = boto3.client('s3')
	
	path = '/home/ubuntu/blkbox-ds/Creative_Production'
	acc_dir = os.path.join(path,acc)
	print(acc_dir)
	if not os.path.exists(acc_dir):
		os.makedirs(acc_dir)
	
	import re
	obj = re.match('.*/(Model.*)',vid)
	
	object_file = obj.group(1)
	print(object_file)
	s3.download_file('blkbox-machinelearning', object_file, '{}/test.mp4'.format(acc))
	vid = '{}/test.mp4'.format(acc)
	target_clip = VideoFileClip(vid)
	
	# get only first 5 seconds
	target_clip = target_clip.subclip(0,2)
	target_size = target_clip.size
	height, width = target_size
	target_size = str(target_size)
	print(height, width, target_size)
	
	model_path = 'Model_files/{}/model_files'.format(acc)
	print('------------download files')
	os.system('aws s3 cp s3://blkbox-machinelearning/Model_files/{a}/model_files {a}/ --recursive'.format(a = acc))

	file_name = '{}/data_files_mid'.format(acc)
	open_file = open(file_name, "rb")
	files_mid = pickle.load(open_file)
	open_file.close()
	
	file_name = '{}/data_files_end'.format(acc)
	open_file = open(file_name, "rb")
	files_end = pickle.load(open_file)
	open_file.close()
	print('=======files====',len(files_mid),len(files_end))
	#print('----------------',files_mid, files_end)

	
	df_mid_performance = pd.read_csv('{}/mid_data.csv'.format(acc))
	df_end_performance = pd.read_csv('{}/end_data.csv'.format(acc))
	print('-------dataframe shape ',df_mid_performance.shape, df_end_performance.shape)

	videos_mid_train = np.load('{}/videos_mid_train.npy'.format(acc))
	
	videos_end_train = np.load('{}/videos_end_train.npy'.format(acc))
	print('======== array shape', videos_mid_train.shape,videos_end_train.shape)

	# print(df_mid_performance['dimension'])
	# if df_mid_performance['dimension'].iloc[0] == target_size:
	# 	print("Same Size")
	# else:
	# 	print(df_mid_performance['dimension'].iloc[0], target_size, type(df_mid_performance['dimension'].iloc[0]),type(target_size))
	# 	print("different size")

	videos_mid_train = videos_mid_train[[list(df_mid_performance.index[df_mid_performance['dimension'] == target_size])]]

	videos_end_train = videos_end_train[[list(df_end_performance.index[df_end_performance['dimension'] == target_size])]]
	print('---- same shape --',len(videos_mid_train), len(videos_end_train))

	list_m = list(df_mid_performance.index[df_mid_performance['dimension'] == target_size])
	list_e = list(df_end_performance.index[df_end_performance['dimension'] == target_size])
	
	
	files_mid = [files_mid[i] for i in list_m]
	files_end = [files_end[i] for i in list_e]

	print(len(files_mid), len(files_end))
	
	def feature_extractor(video):
		importedvideos = []
		# load all the images and prepare them for feeding into the CNN
		counter = 0
	
		frames = []
		count = 1
		cap = cv2.VideoCapture(video)
		length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		#    print("The total frames in the video is :",length)
		temp = length / No_of_frames
		#    print(temp)
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
		#print("features successfully extracted!")
		#    print(imgs_features.shape)
		flatten_img_features = imgs_features.flatten()
		flatten_img_features = np.expand_dims(flatten_img_features,axis = 0)
		#print(flatten_img_features.shape)
		importedvideos.append(flatten_img_features)
		videos_array = np.vstack(importedvideos)
		return videos_array

	def array_file_merge(video_array,target_array,files_train,target):
		array = np.concatenate((video_array,target_array),axis=0)
		print(array.shape)
		files_t = files_train + target
		print(len(files_t))
		return array, files_t

	videos_test = feature_extractor(vid)
	
	arr_mid, files_m = array_file_merge(videos_mid_train,videos_test,files_mid,[vid])
	arr_end, files_e = array_file_merge(videos_end_train,videos_test,files_end,[vid])
	#print(arr_mid)
	#print('----------', files_t)
	print(len(arr_mid), len(arr_mid))

	def cos(arr,files):
		cosSimilarities = cosine_similarity(arr)
		# store the results into a pandas dataframe
		cos_similarities_df = pd.DataFrame(cosSimilarities, columns=files, index=files)
		print(cos_similarities_df.shape)
		return cos_similarities_df



	if section == 'mid':
		cos_similarities_df = cos(arr_mid,files_m)
		closest_videos = cos_similarities_df[vid].sort_values(ascending=False)[:3].index
	elif section == 'end':
		cos_similarities_df = cos(arr_end,files_e)
		closest_videos = cos_similarities_df[vid].sort_values(ascending=False)[:3].index

	
	print(cos_similarities_df)
	cos_similarities_df.to_csv('cos_sim.csv')

	
	#closest_videos = cos_similarities_df[vid].sort_values(by = vid, ascending=False)[1:2].index


	
	print('=-=====',closest_videos)

	#print(closest_videos[0])
	import re
	video_path = re.match(r'.*(act.*)',closest_videos[1])
	video_path = video_path.group(1)
	
	key = 'Model_files/'+video_path
	print(key)

	
	bucket = 'blkbox-machinelearning'

	url = f'https://{bucket}.s3.amazonaws.com/{key}'
	

	return {"val":"Success","video":url}

@Test.route('/alternate_scene',methods=["POST"])
def alternate():
	data= request.get_json()
	vid = data['video']
	#vid = vid
	section = data['section']
	acc = data['acc']
	print('---------',acc, vid, section)

	s3 = boto3.client('s3')
	
	path = '/home/ubuntu/blkbox-ds/Creative_Production'
	acc_dir = os.path.join(path,acc)
	print(acc_dir)
	if not os.path.exists(acc_dir):
		os.makedirs(acc_dir)
	
	import re
	obj = re.match('.*/(Model.*)',vid)
	
	object_file = obj.group(1)
	print(object_file)
	s3.download_file('blkbox-machinelearning', object_file, '{}/test.mp4'.format(acc))
	vid = '{}/test.mp4'.format(acc)
	target_clip = VideoFileClip(vid)
	
	# get only first 5 seconds
	target_clip = target_clip.subclip(0,2)
	target_size = target_clip.size
	height, width = target_size
	target_size = str(target_size)
	print(height, width, target_size)
	
	model_path = 'Model_files/{}/model_files'.format(acc)
	print('------------download files')
	os.system('aws s3 cp s3://blkbox-machinelearning/Model_files/{a}/model_files {a}/ --recursive'.format(a = acc))

	file_name = '{}/data_files_mid'.format(acc)
	open_file = open(file_name, "rb")
	files_mid = pickle.load(open_file)
	open_file.close()
	
	file_name = '{}/data_files_end'.format(acc)
	open_file = open(file_name, "rb")
	files_end = pickle.load(open_file)
	open_file.close()
	print('=======files====',len(files_mid),len(files_end))
	#print('----------------',files_mid, files_end)

	
	df_mid_performance = pd.read_csv('{}/mid_data.csv'.format(acc))
	df_end_performance = pd.read_csv('{}/end_data.csv'.format(acc))
	print('-------dataframe shape ',df_mid_performance.shape, df_end_performance.shape)

	videos_mid_train = np.load('{}/videos_mid_train.npy'.format(acc))
	
	videos_end_train = np.load('{}/videos_end_train.npy'.format(acc))
	print('======== array shape', videos_mid_train.shape,videos_end_train.shape)

	# print(df_mid_performance['dimension'])
	# if df_mid_performance['dimension'].iloc[0] == target_size:
	# 	print("Same Size")
	# else:
	# 	print(df_mid_performance['dimension'].iloc[0], target_size, type(df_mid_performance['dimension'].iloc[0]),type(target_size))
	# 	print("different size")

	videos_mid_train = videos_mid_train[[list(df_mid_performance.index[df_mid_performance['dimension'] == target_size])]]

	videos_end_train = videos_end_train[[list(df_end_performance.index[df_end_performance['dimension'] == target_size])]]
	print('---- same shape --',len(videos_mid_train), len(videos_end_train))

	list_m = list(df_mid_performance.index[df_mid_performance['dimension'] == target_size])
	list_e = list(df_end_performance.index[df_end_performance['dimension'] == target_size])
	
	
	files_mid = [files_mid[i] for i in list_m]
	files_end = [files_end[i] for i in list_e]

	print(len(files_mid), len(files_end))
	
	def feature_extractor(video):
		importedvideos = []
		# load all the images and prepare them for feeding into the CNN
		counter = 0
	
		frames = []
		count = 1
		cap = cv2.VideoCapture(video)
		length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		#    print("The total frames in the video is :",length)
		temp = length / No_of_frames
		#    print(temp)
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
		#print("features successfully extracted!")
		#    print(imgs_features.shape)
		flatten_img_features = imgs_features.flatten()
		flatten_img_features = np.expand_dims(flatten_img_features,axis = 0)
		#print(flatten_img_features.shape)
		importedvideos.append(flatten_img_features)
		videos_array = np.vstack(importedvideos)
		return videos_array

	def array_file_merge(video_array,target_array,files_train,target):
		array = np.concatenate((video_array,target_array),axis=0)
		print(array.shape)
		files_t = files_train + target
		print(len(files_t))
		return array, files_t

	videos_test = feature_extractor(vid)
	
	arr_mid, files_m = array_file_merge(videos_mid_train,videos_test,files_mid,[vid])
	arr_end, files_e = array_file_merge(videos_end_train,videos_test,files_end,[vid])
	#print(arr_mid)
	#print('----------', files_t)
	print(len(arr_mid), len(arr_mid))

	def cos(arr,files):
		cosSimilarities = cosine_similarity(arr)
		# store the results into a pandas dataframe
		cos_similarities_df = pd.DataFrame(cosSimilarities, columns=files, index=files)
		print(cos_similarities_df.shape)
		return cos_similarities_df



	if section == 'mid':
		cos_similarities_df = cos(arr_mid,files_m)
		closest_videos = cos_similarities_df[vid].sort_values(ascending=False)[1:5].index
	elif section == 'end':
		cos_similarities_df = cos(arr_end,files_e)
		closest_videos = cos_similarities_df[vid].sort_values(ascending=False)[1:5].index

	
	print(cos_similarities_df)
	cos_similarities_df.to_csv('cos_sim.csv')

	
	closest_videos = closest_videos.tolist()
	
	import re
	bucket = 'blkbox-machinelearning'
	urls = []
	
	for vi in closest_videos[1:5]:
		print('@@@@@@@@@',vi)
		video_path = re.match(r'.*(act.*)',vi)
		video_path = video_path.group(1)
	
		key = 'Model_files/'+video_path
		print(key)
	
		url = f'https://{bucket}.s3.amazonaws.com/{key}'
		urls.append(url)
	
	os.system('rm -rf /home/ubuntu/blkbox-ds/Creative_Production/{}'.format(acc))

	return {"val":"Success","video":urls}