import serial
import time
import MAIN  # 假設 MAIN.py 中有 main(data) 函式

# 設定序列埠參數（根據實際狀況調整，例如：COM3）
serial_port = "COM3"
baud_rate = 9600

max_rows = 13
# 每一個 row 的資料長度為85，每5筆為一組，故期望每 row 接收到 85/5 = 17 組資料
expected_segments_per_row = 17
total_expected_messages = max_rows * expected_segments_per_row

# 用來儲存接收到的分段資料，格式為 { row_index: [segment1, segment2, ...] }
data_by_row = {}

ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)  # 給予初始化時間

received_messages_count = 0

try:
    while received_messages_count < total_expected_messages:
        if ser.in_waiting:
            print("開始接收資料...")
            # 讀取一行資料並去除尾端換行符號
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            # 預期格式："row{row_index}:數字1,數字2,數字3,數字4,數字5"
            if line.startswith("row"):
                colon_index = line.find(':')
                if colon_index == -1:
                    print("訊息格式錯誤，找不到冒號:", line)
                    continue

                # 解析 row index（"row" 後面的部分至冒號）
                row_str = line[3:colon_index]
                try:
                    row_index = int(row_str)
                except ValueError:
                    print("無法解析 row index:", row_str)
                    continue

                # 取出冒號後面的字串，假設格式為 "數字1,數字2,數字3,數字4,數字5"
                group_str = line[colon_index+1:].strip()
                # 若有可能仍含有括號，可先移除，但不做檢查
                group_str = group_str.strip('[]')
                
                # 判斷使用逗號分隔或空白分隔
                if ',' in group_str:
                    parts = group_str.split(',')
                else:
                    parts = group_str.split()
                
                try:
                    one_d_list = [float(num.strip()) for num in parts if num.strip()]
                    if len(one_d_list) != 5:
                        print(f"row {row_index} 的分段數字數量不等於 5: {one_d_list}")
                        continue
                except ValueError:
                    print("數字轉換失敗，請檢查資料格式:", group_str)
                    continue

                # 將該分段加入對應 row 的資料中
                if row_index not in data_by_row:
                    data_by_row[row_index] = []
                data_by_row[row_index].append(one_d_list)
                received_messages_count += 1
                print(f"成功解析 row {row_index} 的 segment: {one_d_list}")
            else:
                print("訊息格式錯誤，不以 'row' 開頭:", line)
        else:
            # 若無資料，稍作延遲降低 CPU 負荷
            time.sleep(0.5)

    # 檢查每個 row 是否都接收到完整的 17 組分段
    all_rows_complete = True
    for row_index in range(max_rows):
        segments = data_by_row.get(row_index, [])
        if len(segments) != expected_segments_per_row:
            print(f"Row {row_index} 的分段數量不符，收到 {len(segments)} 筆")
            all_rows_complete = False

    if not all_rows_complete:
        print("資料接收不完整，無法組成完整的 2d list")
    else:
        # 依序合併每一個 row 的分段成完整的一列
        final_2d_list = []
        for row_index in range(max_rows):
            complete_row = []
            # 假設發送端已依序傳送，直接依照接收順序串接各段
            for segment in data_by_row[row_index]:
                complete_row.extend(segment)
            if len(complete_row) != 85:
                print(f"Row {row_index} 資料長度不符，長度為 {len(complete_row)}")
            final_2d_list.append(complete_row)
        
        print("已成功重組為 13*85 的 2d list")
        # 呼叫 MAIN.py 中的 main 函式並傳入重組後的 2d list
        MAIN.main(final_2d_list)
    
except KeyboardInterrupt:
    print("接收程式終止。")
finally:
    ser.close()
