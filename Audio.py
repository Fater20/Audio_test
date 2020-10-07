#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/7/5 13:11
# @Author  : DaiPuwei
# @FileName: VoiceExtract.py
# @Software: PyCharm
# @E-mail  ：771830171@qq.com
# @Blog    ：https://blog.csdn.net/qq_30091945

import numpy as np
from pydub import AudioSegment
import pydub
import os
import wave
import json
from matplotlib import pyplot as plt
from pydub.playback import play
import pygame
import pyaudio
import time
from pygame import mixer
def MP32WAV(mp3_path,wav_path):
    """
    这是MP3文件转化成WAV文件的函数
    :param mp3_path: MP3文件的地址
    :param wav_path: WAV文件的地址
    """
    pydub.AudioSegment.converter = "C:\\Users\\dell\\Documents\\ffmpeg\\bin\\ffmpeg.exe"            #说明ffmpeg的地址
    MP3_File = AudioSegment.from_mp3(file=mp3_path)
    MP3_File.export(wav_path,format="wav")

def Read_WAV(wav_path):
    """
    这是读取wav文件的函数，音频数据是单通道的。返回json
    :param wav_path: WAV文件的地址
    """
    wav_file = wave.open(wav_path,'r')
    numchannel = wav_file.getnchannels()            # 声道数
    samplewidth = wav_file.getsampwidth()           # 量化位数
    framerate = wav_file.getframerate()             # 采样频率
    numframes = wav_file.getnframes()               # 采样点数
    print("channel", numchannel)
    print("sample_width", samplewidth)
    print("framerate", framerate)
    print("numframes", numframes)
    Wav_Data = wav_file.readframes(numframes)
    Wav_Data = np.fromstring(Wav_Data,dtype=np.int16)
    Wav_Data = Wav_Data*1.0/(max(abs(Wav_Data)))        #对数据进行归一化
    # 生成音频数据,ndarray不能进行json化，必须转化为list，生成JSON
    dict = {"channel":numchannel,
            "samplewidth":samplewidth,
            "framerate":framerate,
            "numframes":numframes,
            "WaveData":list(Wav_Data)}
    return json.dumps(dict)

def DrawSpectrum(wav_data,framerate):
    """
    这是画音频的频谱函数
    :param wav_data: 音频数据
    :param framerate: 采样频率
    """
    Time = np.linspace(0,len(wav_data)/framerate*1.0,num=len(wav_data))
    plt.figure(1)
    plt.plot(Time,wav_data)
    plt.grid(True)
    plt.show()
    plt.figure(2)
    Pxx, freqs, bins, im = plt.specgram(wav_data,NFFT=1024,Fs = 16000,noverlap=900)
    plt.show()
    print(Pxx)
    print(freqs)
    print(bins)
    print(im)

def run_main():
    """
        这是主函数
    """
    # MP3文件和WAV文件的地址
    path1 = './MP3_File'
    path2 = "./WAV_File"
    paths = os.listdir(path1)
    mp3_paths = []
    # 获取mp3文件的相对地址
    for mp3_path in paths:
        mp3_paths.append(path1+"/"+mp3_path)
    #print(mp3_paths)

    # 得到MP3文件对应的WAV文件的相对地址
    wav_paths = []
    for mp3_path in mp3_paths:
       wav_path = path2+"/"+mp3_path[1:].split('.')[0].split('/')[-1]+'.wav'
       wav_paths.append(wav_path)
    #print(wav_paths)

    # 将MP3文件转化成WAV文件
    for(mp3_path,wav_path) in zip(mp3_paths,wav_paths):
        MP32WAV(mp3_path,wav_path)
    for wav_path in wav_paths:
        Read_WAV(wav_path)

    # 开始对音频文件进行数据化
    for wav_path in wav_paths:
        wav_json = Read_WAV(wav_path)
        #print(wav_json)
        wav = json.loads(wav_json)
        wav_data = np.array(wav['WaveData'])
        framerate = int(wav['framerate'])

        p = pyaudio.PyAudio()
        stream = p.open(44100,1,format = p.get_format_from_width(2),output = True)
        stream.write(wav_data)

        DrawSpectrum(wav_data,framerate)


def play_audio_callback(wave_path):

    wf = wave.open(wave_path, 'rb')
 
    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()
 
    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
 
 
    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=1,
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
 
    # read data
    stream.start_stream()
 
    while stream.is_active():
        time.sleep(0.1)
 
    # stop stream (4)
    stream.stop_stream()
    stream.close()
 
    # close PyAudio (5)
    p.terminate()
 
 
def play_audio(path, state):
    Wave_read = wave.open(path, mode="rb")
    p = pyaudio.PyAudio()

    stream = p.open(88200,1,format = p.get_format_from_width(2),frames_per_buffer=4096,output = True)
    data = Wave_read.readframes(88200*5)

    stream.write(data)

    # play stream (3)
    while len(data) > 0:
        if(state[0] != state[1]):
            stream.stop_stream()
            stream.close()
            if(state[1]-state[0]>0):
                for i in range(0,(state[1]-state[0])*10):
                    framerate = 88200+1100*i
                    stream = p.open(framerate, 1, format = p.get_format_from_width(2),frames_per_buffer=4096,output = True)
                    data = Wave_read.readframes(44100+550*i)
                    stream.write(data)
            else: 
                for i in range(0,(state[1]-state[0])*10,-1):
                    framerate = 88200+1100*i
                    stream = p.open(framerate, 1, format = p.get_format_from_width(2),frames_per_buffer=4096,output = True)
                    data = Wave_read.readframes(44100+550*i)
                    stream.write(data)     
            state[0] = state[1]
        else:
            data = Wave_read.readframes(8820)
            stream.write(data)

#Function Name: play_audio_init
#mood: 0:calm 1:happy 2:sad 3:angry
#value: 25-100
def play_audio_init(current_mood, value):
    if current_mood==0 :
        pygame.mixer.init(44100)
        pygame.mixer.music.load("./MP3_File/test4.mp3") # 载入音乐
        pygame.mixer.music.set_volume(value)# 设置音量
        pygame.mixer.music.play(-1) # 播放音乐
    elif current_mood==1 :
        pygame.mixer.init(132300)
        pygame.mixer.music.load("./MP3_File/test4.mp3") # 载入音乐
        pygame.mixer.music.set_volume(value)# 设置音量
        pygame.mixer.music.play(-1) # 播放音乐
    elif current_mood==2 :
        pygame.mixer.init(14700)
        pygame.mixer.music.load("./MP3_File/test4.mp3") # 载入音乐
        pygame.mixer.music.set_volume(value)# 设置音量
        pygame.mixer.music.play(-1) # 播放音乐
    elif current_mood==3 :
        pygame.mixer.init(44100)
        pygame.mixer.music.load("./MP3_File/test4.mp3") # 载入音乐
        pygame.mixer.music.set_volume(value)# 设置音量
        pygame.mixer.music.play(-1) # 播放音乐
        drums = pygame.mixer.Sound("./MP3_File/drums.wav")
        if(value-0.1 >= 0.1):
            drums_volume = value-0.1
        else:
            drums_volume = 0.1
        drums.set_volume(drums_volume)
        drums.play()
    else:
        print("Mood ERROR")

#Function Name: change_Audio
#mood: 0:calm 1:happy 2:sad 3:angry
#value: 25-100
#time: 单位是秒
#pos: 上一次调整时帧的位置
def change_Audio(current_mood, next_mood, value, time, pos):
    
    #计算帧位置
    if current_mood==1 :
        pos = pos + 2*132300*time
    if current_mood==2 :
        pos = pos + 2*14700*time
    elif current_mood==3 :
        pos = pos + 2*44100*time
    else:
        pos = pos + 2*44100*time
    
    if(pos>=5735808):
        pos = 0

    #判断是否发生情绪转变
    if current_mood == next_mood:
        pygame.mixer.music.set_volume(value)
    else:
        if next_mood==1 :
            pygame.mixer.quit()
            pygame.mixer.init(132300)
            pygame.mixer.music.load("./MP3_File/test4.mp3")  # 载入音乐
            pygame.mixer.music.set_volume(value)            # 设置音量
            pygame.mixer.music.play(-1)                     # 播放音乐
            pygame.mixer.music.set_pos(pos/132300)          #设置播放位置
        elif next_mood==2 :
            pygame.mixer.quit()
            pygame.mixer.init(14700)
            pygame.mixer.music.load("./MP3_File/test4.mp3")  # 载入音乐
            pygame.mixer.music.set_volume(value)            # 设置音量
            pygame.mixer.music.play(-1)                     # 播放音乐
            pygame.mixer.music.set_pos(pos/14700)           #设置播放位置
        elif next_mood==3 :
            pygame.mixer.quit()
            pygame.mixer.init(44100)
            pygame.mixer.music.load("./MP3_File/test4.mp3")  # 载入音乐
            pygame.mixer.music.set_volume(value)            # 设置音量
            pygame.mixer.music.play(-1)                     # 播放音乐
            pygame.mixer.music.set_pos(pos/44100)           #设置播放位置
            drums = pygame.mixer.Sound("./MP3_File/drums.wav")
            if(value-0.1 >= 0.1):
                drums_volume = value-0.1
            else:
                drums_volume = 0.1
            drums.set_volume(drums_volume)
            drums.play()   
            
        else:
            pygame.mixer.quit()
            pygame.mixer.init(44100)
            pygame.mixer.music.load("./MP3_File/test4.mp3")  # 载入音乐
            pygame.mixer.music.set_volume(value)            # 设置音量
            pygame.mixer.music.play(-1)                     # 播放音乐
            pygame.mixer.music.set_pos(pos/44100)           #设置播放位置
    return pos

if __name__ == '__main__':
    #run_main()
    pos=0
    play_audio_init(0, 50)
    time.sleep(20)
    while 1:
        pos=change_Audio(0, 1, 50, 20, pos)
        time.sleep(20)
        pos=change_Audio(1, 2, 50, 20, pos)
        time.sleep(20)
        pos=change_Audio(2, 3, 50, 20, pos)
        time.sleep(20)
        pos=change_Audio(3, 0, 50, 20, pos)
        time.sleep(20)
    
    #state=[0, -2]
    #play_audio("./WAV_File/test.wav", state)
    #play_audio_callback("./WAV_File/test.wav")
    #pygame.mixer.pre_init(22100, 16, 2, 4096)

    #str_data = Wave_read.readframes(nframes)
    #wave_data = np.fromstring(str_data, dtype=np.short)
    #wave_data = np.reshape(wave_data,[nframes,nchannels])
    #wave_data.shape = (2, -1)

 
    #print(len(Wave_read) / (1000*60))

    #stream.write(wave_data)
    #stream.stop_stream()
    """
    time = np.arange(0, nframes) * (1.0 / framerate)

    plt.figure()
    # 左声道波形
    plt.subplot(3,1,1)
    plt.plot(time, wave_data[:,0])
    plt.xlabel("time (seconds)")
    plt.ylabel("Amplitude")
    plt.title("Left channel")
    plt.grid()  # 标尺

    plt.subplot(3,1,3)
    # 右声道波形
    plt.plot(time, wave_data[:,1], c="g")
    plt.xlabel("time (seconds)")
    plt.ylabel("Amplitude")
    plt.title("Left channel")
    plt.title("right channel")
    plt.grid()

    plt.show()
    #wave_obj = sa.WaveObject.from_wave_file("./WAV_File/test.wav")
    #while True:
        #play_obj = wave_obj.play()
        #play_obj.wait_done()
        #sound = AudioSegment.from_file("./MP3_File/test.mp3", "mp3")
        #play(sound)
    """
