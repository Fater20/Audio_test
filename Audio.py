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
import simpleaudio as sa
import pygame
import pyaudio
import time
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


if __name__ == '__main__':
    #run_main()
    Wave_read = wave.open("./WAV_File/test.wav",mode="rb")
    nchannels = Wave_read.getnchannels()
    sampwidth = Wave_read.getsampwidth()
    framerate = Wave_read.getframerate()
    nframes = Wave_read.getnframes()

    str_data = Wave_read.readframes(nframes)
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data = np.reshape(wave_data,[nframes,nchannels])
    #wave_data.shape = (2, -1)
    p = pyaudio.PyAudio()

    print("nchannels ",nchannels)
    print("samplewidth ", sampwidth)
    print("framerate ", framerate)
    print("nframes ", nframes)

    stream = p.open(44100,1,format = p.get_format_from_width(sampwidth),output = True)
    #data = wave_data[0].readframes(44100)
    
    # play stream (3)
    #while len(data) > 0:
     #   stream.write(data)
      #  data = wave_data[0].readframes(44100)
    
    #print(len(Wave_read) / (1000*60))

    #stream.write(wave_data[:,0])
    #stream.stop_stream()

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
