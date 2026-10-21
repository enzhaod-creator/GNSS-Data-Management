import pandas as pd
from pathlib import Path
import streamlit as st
from datetime import date

# 1. 设置网页基础信息
st.set_page_config(
    page_title="GNSS数据管理系统",
    page_icon="🛰️",
    layout="wide"
)

# 2. 创建侧边栏
st.sidebar.title("🛰️ GNSS管理平台")

page = st.sidebar.radio(
    "功能导航",
    ["系统首页", "站点管理", "数据查询", "数据下载"]
)

st.sidebar.divider()
st.sidebar.caption("GNSS Data Management System")

# 3. 系统首页
if page == "系统首页":

    st.title("🛰️ GNSS数据管理系统")
    st.write("GNSS Data Management Platform")
    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("GNSS站点数量", 0)
    col2.metric("RINEX文件数量", 0)
    col3.metric("数据存储量", "0 GB")

    st.subheader("系统功能")

    st.info(
        "本系统用于GNSS观测数据的存储、"
        "管理、查询和下载。"
    )

    st.success("系统网页已创建，等待接入数据库。")


# 4. GNSS站点管理
elif page == "站点管理":

    st.title("📍 GNSS站点管理")
    st.write("GNSS观测站点信息展示与查询")

    station_file = (
        Path(__file__).resolve().parent
        / "data"
        / "stations.csv"
    )

    if station_file.exists():

        df = pd.read_csv(
            station_file,
            dtype={"station_code": "string"}
        )

        if df.empty:
            st.info("暂无真实GNSS站点数据。")

        else:
            keyword = st.text_input(
                "搜索站点编号或名称"
            )

            if keyword:
                mask = (
                    df["station_code"]
                    .fillna("")
                    .str.contains(
                        keyword,
                        case=False,
                        regex=False
                    )
                    |
                    df["station_name"]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        keyword,
                        case=False,
                        regex=False
                    )
                )
                df = df[mask]

            st.metric("站点数量", len(df))

            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True
            )

            map_df = df.copy()

            map_df["latitude"] = pd.to_numeric(
                map_df["latitude"],
                errors="coerce"
            )

            map_df["longitude"] = pd.to_numeric(
                map_df["longitude"],
                errors="coerce"
            )

            map_df = map_df.dropna(
                subset=["latitude", "longitude"]
            )

            map_df = map_df[
                map_df["latitude"].between(-90, 90)
                & map_df["longitude"].between(-180, 180)
            ]

            if not map_df.empty:
                st.subheader("GNSS站点分布地图")
                st.map(
                    map_df,
                    latitude="latitude",
                    longitude="longitude"
                )

    else:
        st.warning("尚未找到站点数据文件。")


# 5. 数据查询
elif page == "数据查询":

    st.title("🔍 GNSS数据查询")

    station = st.text_input(
        "输入站点编号",
        placeholder="例如：BJFS"
    )

    observation_date = st.date_input(
        "选择观测日期",
        value=date.today()
    )

    if st.button("查询数据", type="primary"):
        st.info(
            f"站点：{station or '全部'}，"
            f"日期：{observation_date}"
        )
        st.warning("当前为演示版本，尚未连接MySQL。")

# 6. 数据下载
elif page == "数据下载":

    st.title("📥 GNSS数据下载")

    st.write("后续将提供RINEX观测文件下载。")

    st.info("文件下载模块正在开发中。")
