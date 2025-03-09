"""將麥克風連接到RPi
=>在RPi裡面執行此code來錄製real time 音訊
=>音訊會經過Mel 平埔處理成一串數字後
=>輸入到訓練好的模型做辨識
"""

import pyaudio
import wave
import os
import librosa
import json
import numpy as np
#np.set_printoptions(threshold = np.inf)
from scipy.fftpack import dct
from datetime import datetime

def record_audio_to_file(duration = 5, folder = "Audio", filename = "test_audio.wav", sample_rate=22050, channels=1, chunk_size=1024):
    """
    使用 pyaudio 錄製音訊並將其保存為 WAV 檔案到指定資料夾。
    :param duration: 錄音時間（秒）
    :param folder: 儲存音訊檔案的資料夾
    :param filename: 音訊檔案名稱
    :param sample_rate: 音訊採樣率（預設 16000 Hz）
    :param channels: 聲道數量（預設單聲道）
    :param chunk_size: 單次讀取的音訊塊大小
    """
    # 確保資料夾存在
    os.makedirs(folder, exist_ok=True)
    
    # 完整的檔案路徑
    filepath = os.path.join(folder, filename)

    # 初始化 PyAudio 物件
    p = pyaudio.PyAudio()

    # 開啟音訊流
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    print(f"開始錄製 {duration} 秒音訊，將保存為 {filepath}...")

    frames = []

    # 錄製音訊
    for i in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    # 停止並關閉音訊流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 儲存錄音為 WAV 檔案
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    
    config= {
            'sample_rate': 22050,
            'n_mels':256,
            'n_fft':1024,
            'hop_length':256
    }
    
    y,sr = librosa.load(r"/home/e520/Temp_File/Audio/test_audio.wav",sr = config['sample_rate'])
    
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=config['n_fft'],
        hop_length = config['hop_length'],
        n_mels = config['n_mels']
    )
    print("Loading")
    log_S = librosa.power_to_db(S,ref=np.max)
    mfcc = dct(log_S,type =2,axis=0,norm='ortho')
    mfcc = mfcc[:13,:]
    #if isinstance(mfcc,np.ndarray):
     #   mfcc = mfcc.tolist()
    #mfcc = json.dumps(mfcc)
    
    
    print(f"音訊已保存到 {filepath}")
    return mfcc
    
# 使用範例
if __name__ == "__main__":
    duration = 5 #錄製 5 秒鐘的音訊
    folder = "Audio"  # 音訊檔案儲存的資料夾
    time = datetime.now()
    filename = "test_audio.wav"  # 儲存的音訊檔案名稱
    mfcc = record_audio_to_file(duration, folder, filename)
    print("MFCC",mfcc)
