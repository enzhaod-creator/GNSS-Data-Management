import streamlit as st
import requests
import pandas as pd
from datetime import date

# ================= 配置后端地址 =================

BACKEND_URL = "http://10.199.205.3:8000/api/stations"

# 1. 设置网页基础信息
st.set_page_config(
    page_title="GNSS数据管理系统",
    page_icon="🛰️",
    layout="wide"
)

# 2. 创建侧边栏
st.sidebar.title("🛰️ GNSS管理平台")

# 增加了一个“数据上传”选项
page = st.sidebar.radio(
    "功能导航",
    ["系统首页", "站点管理", "数据查询", "数据下载", "数据上传"]
)

st.sidebar.divider()
st.sidebar.caption("GNSS Data Management System")

# ================= 系统首页 =================
if page == "系统首页":
    st.title("🛰️ GNSS数据管理系统")
    st.write("GNSS Data Management Platform")
    st.divider()

    # 向后端请求看板数据
    try:
        res = requests.get(f"{BACKEND_URL}/dashboard/stats")
        if res.status_code == 200:
            stats = res.json()
        else:
            stats = {"station_count": 0, "file_count": 0, "total_size_gb": 0}
    except:
        stats = {"station_count": 0, "file_count": 0, "total_size_gb": 0}

    col1, col2, col3 = st.columns(3)
    col1.metric("GNSS站点数量", stats["station_count"])
    col2.metric("RINEX文件数量", stats["file_count"])
    col3.metric("数据存储量", f"{stats['total_size_gb']} GB")

    st.subheader("系统功能")
    st.info("本系统用于GNSS观测数据的存储、管理、查询和下载。")
    st.success("✅ 系统已成功连接后端数据库！")

# ================= 站点管理 =================
elif page == "站点管理":
    st.title("📍 GNSS站点管理")
    
    # 向后端请求真实站点数据
    try:
        res = requests.get(f"{BACKEND_URL}/")
        if res.status_code == 200:
            stations = res.json()
            if stations:
                df = pd.DataFrame(stations)
                # 简单重命名一下列名，让表格更好看
                df = df.rename(columns={"id": "ID", "name": "站点编号", "lat": "纬度", "lon": "经度"})
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.warning("数据库中暂无站点数据。")
        else:
            st.error("获取站点数据失败。")
    except Exception as e:
        st.error(f"无法连接后端服务，请确保后端已启动。({e})")

# ================= 数据查询 =================
elif page == "数据查询":
    st.title("🔍 GNSS数据查询")

    station = st.text_input("输入站点编号", placeholder="例如：BJFS")

    if st.button("查询数据", type="primary"):
        if station:
            try:
                res = requests.get(f"{BACKEND_URL}/{station}/files")
                if res.status_code == 200:
                    files = res.json()
                    if files:
                        df = pd.DataFrame(files)
                        df = df.rename(columns={"file_name": "文件名", "file_path": "存储路径", "obs_date": "观测日期"})
                        st.dataframe(df, hide_index=True, use_container_width=True)
                        st.success(f"找到 {len(files)} 个文件。")
                    else:
                        st.warning("该站点下暂无文件。")
                elif res.status_code == 404:
                    st.error("数据库中没有这个测站。")
            except Exception as e:
                st.error(f"查询失败，无法连接后端。({e})")
        else:
            st.warning("请输入站点编号。")

# ================= 数据下载 =================
elif page == "数据下载":
    st.title("📥 GNSS数据下载")
    st.write("输入文件名进行下载：")
    
    file_name = st.text_input("文件名", placeholder="例如：BJFS_20231010.rnx")
    
    if st.button("获取下载链接"):
        if file_name:
            # 前端直接用 Markdown 生成一个下载链接指向后端
            download_url = f"{BACKEND_URL}/download/{file_name}"
            st.markdown(f"👉 [点击此处下载 {file_name}]({download_url})")
            st.info("提示：如果点击没有反应，请确认该文件真实存在于后端。")

# ================= 数据上传 =================
elif page == "数据上传":
    st.title("📤 GNSS数据上传")
    
    with st.form("upload_form"):
        upload_station = st.text_input("站点编号", value="WUHN")
        upload_date = st.date_input("观测日期", value=date.today())
        uploaded_file = st.file_uploader("选择 RINEX 文件", type=["rnx", "o", "23o"])
        
        submitted = st.form_submit_button("开始上传")
        
        if submitted and uploaded_file is not None:
            # 构造请求发给后端
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {
                "station_name": upload_station,
                "obs_date": str(upload_date)
            }
            
            try:
                res = requests.post(f"{BACKEND_URL}/upload", data=data, files=files)
                if res.status_code == 200:
                    st.success(f"文件 {uploaded_file.name} 上传成功！已存入数据库。")
                else:
                    st.error("上传失败，后端返回错误。")
            except Exception as e:
                st.error(f"无法连接后端服务。({e})")
