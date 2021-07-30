# # stich : {"acc":"act_835479183667691", "videos":["/home/ubuntu/blkbox-ds/Creative_Production/act_1007332209799361/mid/1080 x 1080 EN.mp4 - Scene 002.mp4","/home/ubuntu/blkbox-ds/Creative_Production/act_1007332209799361/mid/1080 x 1080 ES.mp4 - Scene 007.mp4"]}
# # start_scenes : {"acc":"act_835479183667691"}

# # import boto3,re
# # # s3 = boto3.resource('s3')

# # # videos = ["https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/Model_files/act_1007332209799361/mid/1080+x+1080+ES.mp4+-+Scene+008.mp4",
# # #         "https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/Model_files/act_1007332209799361/end/1080+x+1080+PT.mp4+-+Scene+010.mp4"]

# # # for video in videos:
# # #     res = re.match(r'.*?com/(.*mp4)', video)
# # #     name = res.group(1)
# # #     print('-----------',name)
# # #     local_name = re.match(r'.*/(.*mp4)',name)
# # #     local_name = local_name.group(1)
# # #     print('----------',local_name)
# # #     acc = 'act_100733220979936'
# # #     bucket = 'blkbox-machinelearning'
# # #     #s3.download_file(bucket,name,'{}/Videos/{}'.format(acc,local_name))
# # #     #name = name.replace('+',' ')
# # #     #s3.meta.client.download_file(bucket,name,local_name)

# # my_bucket = 'blkbox-machinelearning'
# # import boto3
# # s3 = boto3.resource('s3')

# # ## Bucket to use
# # my_bucket = s3.Bucket('blkbox-machinelearning')

# # ## List objects within a given prefix
# # for obj in my_bucket.objects.filter(Delimiter='/', Prefix='Model_files/'):
# #         print(obj.key)


# vid = "https://blkbox-machinelearning.s3.us-west-1.amazonaws.com/Model_files/act_1252889271474289/start/1080x1080_DHfortheHolidays_UAad_V1.mp4 - Scene 001.mp4"

# # import ffmpeg

# # info=ffmpeg.probe(vid)

# # print(f"duration={info['format']['duration']}")
# # print(f"framerate={info['streams'][0]['avg_frame_rate']}")


# #from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, concatenate_audioclips, AudioClip, CompositeAudioClip

# # target_clip = VideoFileClip(vid)
# # print('-----------',target_clip)

# def with_moviepy(filename):
#     from moviepy.editor import VideoFileClip
#     clip = VideoFileClip(filename)
#     duration       = clip.duration
#     fps            = clip.fps
#     width, height  = clip.size
#     return duration, fps, (width, height)

# print(with_moviepy(vid))


import boto3
s3 = boto3.client('s3')
acc = 'act_1252889271474289'
counter = 2
#name = 'Model_files/act_1252889271474289/start/1080x1080_CoffeeCompetitionV2b.mp4 - Scene 001.mp4'
name = 'Model_files/act_1252889271474289/start/1080x1080_CoffeeCompetitionV2b.mp4 - Scene 001.mp4'

try:
    s3.download_file('blkbox-machinelearning',name,'/home/ubuntu/blkbox-ds/Creative_Production/scripts/vid_{}.mp4'.format(counter))
    print('success')
except Exception as e:
    print('############',e,'#########')
        