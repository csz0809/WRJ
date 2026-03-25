import streamlit as st
import time
import datetime
import pandas as pd
import plotly.express as px
from threading import Thread
import numpy as np

# 初始化会话状态
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = pd.DataFrame(columns=["序号", "时间戳", "状态"])
if "last_heartbeat_time" not in st.session_state:
    st.session_state.last_heartbeat_time = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "sequence" not in st.session_state:
    st.session_state.sequence = 1

def send_heartbeat():
    """模拟无人机每秒发送心跳包"""
    while st.session_state.is_running:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        seq = st.session_state.sequence
        # 更新最新心跳时间
        st.session_state.last_heartbeat_time = datetime.datetime.now()
        # 记录心跳数据
        new_row = pd.DataFrame({
            "序号": [seq],
            "时间戳": [current_time],
            "状态": ["正常"]
        })
        st.session_state.heartbeat_data = pd.concat([st.session_state.heartbeat_data, new_row], ignore_index=True)
        st.session_state.sequence += 1
        time.sleep(1)

def check_connection():
    """地面站断线检测（3秒超时报警）"""
    while st.session_state.is_running:
        if st.session_state.last_heartbeat_time:
            time_diff = (datetime.datetime.now() - st.session_state.last_heartbeat_time).total_seconds()
            if time_diff > 3:
                # 记录断线状态
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                new_row = pd.DataFrame({
                    "序号": [st.session_state.sequence],
                    "时间戳": [current_time],
                    "状态": ["断线"]
                })
                st.session_state.heartbeat_data = pd.concat([st.session_state.heartbeat_data, new_row], ignore_index=True)
                st.session_state.sequence += 1
        time.sleep(0.5)

# 页面布局
st.set_page_config(page_title="无人机心跳监测系统", layout="wide")
st.title("🚁 无人机通信'心跳'监测可视化系统")

# 控制区
col1, col2 = st.columns(2)
with col1:
    if st.button("启动监测", disabled=st.session_state.is_running):
        st.session_state.is_running = True
        # 启动心跳发送线程
        heartbeat_thread = Thread(target=send_heartbeat, daemon=True)
        heartbeat_thread.start()
        # 启动断线检测线程
        check_thread = Thread(target=check_connection, daemon=True)
        check_thread.start()
        st.success("监测已启动！")

with col2:
    if st.button("停止监测", disabled=not st.session_state.is_running):
        st.session_state.is_running = False
        st.warning("监测已停止！")

# 数据展示区
st.subheader("📊 心跳包数据列表")
st.dataframe(st.session_state.heartbeat_data, use_container_width=True)

# 可视化区
st.subheader("📈 心跳包时序折线图")
if not st.session_state.heartbeat_data.empty:
    # 转换时间戳为datetime格式
    st.session_state.heartbeat_data["时间戳_dt"] = pd.to_datetime(st.session_state.heartbeat_data["时间戳"])
    # 绘制折线图
    fig = px.line(
        st.session_state.heartbeat_data,
        x="时间戳_dt",
        y="序号",
        color="状态",
        title="无人机心跳包发送时序",
        labels={"时间戳_dt": "时间", "序号": "心跳包序号"},
        color_discrete_map={"正常": "green", "断线": "red"}
    )
    st.plotly_chart(fig, use_container_width=True)

# 状态提示区
st.subheader("🔍 实时连接状态")
if st.session_state.is_running:
    if st.session_state.last_heartbeat_time:
        time_diff = (datetime.datetime.now() - st.session_state.last_heartbeat_time).total_seconds()
        if time_diff <= 3:
            st.success("✅ 连接正常，心跳包接收正常")
        else:
            st.error(f"❌ 连接超时！已{time_diff:.1f}秒未收到心跳包")
    else:
        st.info("⏳ 等待第一个心跳包...")
else:
    st.info("🛑 监测未启动")

# 数据导出
if not st.session_state.heartbeat_data.empty:
    csv = st.session_state.heartbeat_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 导出心跳数据",
        data=csv,
        file_name=f"drone_heartbeat_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
        mime='text/csv'
    )
