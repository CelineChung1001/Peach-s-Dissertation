import serial
import time
import sound

def send_message(ser, message):
    """
    傳送指令給 Arduino，格式範例：SEND:訊息
    Arduino 端須根據收到的指令來執行 LoRa 傳送
    """
    command = f"SEND:{message}\n"
    ser.write(command.encode('utf-8'))
    print(f"Message sent: {message}")

if __name__ == "__main__":
    # 請確認序列埠名稱，例如 /dev/ttyACM0 或 /dev/ttyUSB0
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # 給予 Arduino 初始化的時間

    try:
        print("Sending MFCC...")
        # 假設 sound.record_audio_to_file() 回傳一個二維 list 的 MFCC 資料
        mfcc = sound.record_audio_to_file()
        
        # 逐筆傳送每一列資料
        for index, row in enumerate(mfcc):
            # 將單一列包裝成二維 list 格式，例如: [[row 資料]]
            message = [row]
            send_message(ser, message)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            # 根據需求，可以加入延遲或等待接收端回覆的機制
            time.sleep(0.1)  # 調整間隔時間以符合實際需求
    finally:
        ser.close()
