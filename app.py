import time
import pandas as pd
from datetime import datetime

# 存储心跳数据
heartbeat_data = []
last_receive_time = time.time()
sequence = 0

def send_heartbeat():
    global sequence, last_receive_time
    sequence += 1
    current_time = datetime.now().strftime("%H:%M:%S")
    heartbeat_data.append({"序号": sequence, "时间": current_time})
    last_receive_time = time.time()
    print(f"[{current_time}] 心跳包 {sequence} 发送成功")

def check_connection():
    global last_receive_time
    if time.time() - last_receive_time > 3:
        print("⚠️  连接超时！3秒未收到心跳包")
        return True
    return False

# 主循环
if __name__ == "__main__":
    try:
        while True:
            send_heartbeat()
            time.sleep(1)
            if check_connection():
                break
    except KeyboardInterrupt:
        # 保存数据到CSV
        df = pd.DataFrame(heartbeat_data)
        df.to_csv("heartbeat_data.csv", index=False, encoding="utf-8")
        print("\n✅ 数据已保存为 heartbeat_data.csv")
