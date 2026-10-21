
import streamlit as st
import pandas as pd
from pathlib import Path


# ==================================================
# 1. 网页基础配置
# ==================================================

st.set_page_config(
    page_title="GNSS数据管理系统",
    page_icon="🛰️",
    layout="wide"
)


# ==================================================
# 2. 数据文件路径
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

STATIONS_FILE = DATA_DIR / "stations.csv"
RINEX_FILE = DATA_DIR / "rinex_files.csv"


# ==================================================
# 3. 读取GNSS站点信息
# ==================================================

def load_stations():

    required_columns = [
        "station_code",
        "station_name",
        "latitude",
        "longitude",
        "status"
    ]

    if not STATIONS_FILE.exists():
        return pd.DataFrame(), "未找到stations.csv文件"

    try:
        df = pd.read_csv(
            STATIONS_FILE,
            dtype={"station_code": "string"}
        )

        if not all(
            col in df.columns
            for col in required_columns
        ):
            return pd.DataFrame(), "站点CSV缺少必要字段"

        return df, None

    except Exception as e:
        return pd.DataFrame(), f"站点数据读取失败：{e}"


# ==================================================
# 4. 读取RINEX文件索引
# ==================================================

def load_rinex_files():

    required_columns = [
        "file_id",
        "station_code",
        "filename",
        "observation_date",
        "file_type",
        "file_size",
        "storage_path"
    ]

    if not RINEX_FILE.exists():
        return pd.DataFrame(), "未找到rinex_files.csv文件"

    try:
        df = pd.read_csv(
            RINEX_FILE,
            dtype={
                "file_id": "string",
                "station_code": "string",
                "filename": "string",
                "storage_path": "string"
            }
        )

        if not all(
            col in df.columns
            for col in required_columns
        ):
            return pd.DataFrame(), "RINEX文件索引缺少必要字段"

        return df, None

    except Exception as e:
        return pd.DataFrame(), f"RINEX索引读取失败：{e}"


# ==================================================
# 5. 左侧导航栏
# ==================================================

st.sidebar.title("🛰️ GNSS管理平台")

page = st.sidebar.radio(
    "功能导航",
    [
        "系统首页",
        "站点管理",
        "数据查询",
        "数据下载"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "GNSS Data Management System"
)


# ==================================================
# 6. 系统首页
# ==================================================

if page == "系统首页":

    st.title("🛰️ GNSS数据管理系统")

    st.write(
        "GNSS Data Management Platform"
    )

    st.divider()

    # 读取数据
    stations_df, station_error = load_stations()
    files_df, file_error = load_rinex_files()

    # 创建统计指标
    col1, col2, col3 = st.columns(3)

    # GNSS站点数量
    if station_error:
        col1.metric(
            "GNSS站点数量",
            "未接入"
        )
    else:
        col1.metric(
            "GNSS站点数量",
            len(stations_df)
        )

    # RINEX文件数量和存储量
    if file_error:

        col2.metric(
            "RINEX文件数量",
            "未接入"
        )

        col3.metric(
            "数据存储量",
            "未接入"
        )

    else:

        col2.metric(
            "RINEX文件数量",
            len(files_df)
        )

        # 将文件大小转换为数值
        file_sizes = pd.to_numeric(
            files_df["file_size"],
            errors="coerce"
        ).fillna(0)

        total_bytes = file_sizes.sum()

        total_gb = total_bytes / (1024 ** 3)

        col3.metric(
            "数据存储量",
            f"{total_gb:.2f} GB"
        )

    # 系统功能介绍
    st.subheader("系统功能")

    st.info(
        "本系统用于GNSS观测数据的"
        "存储、管理、查询和下载。"
    )

    # 站点数据状态
    if station_error:

        st.warning(station_error)

    elif stations_df.empty:

        st.warning(
            "站点信息表已建立，"
            "等待录入真实GNSS站点。"
        )

    else:

        st.success(
            "GNSS站点数据已成功读取。"
        )

    # RINEX索引状态
    if file_error:

        st.warning(file_error)

    elif files_df.empty:

        st.info(
            "RINEX文件索引已建立，"
            "等待录入真实文件信息。"
        )

    else:

        st.success(
            "RINEX文件索引已成功读取。"
        )

    st.caption(
        "当前统计数据来自CSV索引，"
        "后续将连接数据库与真实文件存储。"
    )


# ==================================================
# 7. GNSS站点管理
# ==================================================

elif page == "站点管理":

    st.title("📍 GNSS站点管理")

    st.write(
        "GNSS观测站点信息展示与查询"
    )

    df, error = load_stations()

    if error:

        st.warning(error)

    elif df.empty:

        st.info(
            "暂无真实GNSS站点数据。"
        )

    else:

        # 搜索站点
        keyword = st.text_input(
            "搜索站点编号或名称",
            placeholder="输入站点编号或名称"
        )

        # 筛选数据
        if keyword:

            mask = (
                df["station_code"]
                .fillna("")
                .astype(str)
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

            filtered_df = df[mask].copy()

        else:

            filtered_df = df.copy()

        # 显示站点数量
        st.metric(
            "GNSS站点数量",
            len(filtered_df)
        )

        # 显示站点信息
        st.subheader("站点信息表")

        st.dataframe(
            filtered_df,
            hide_index=True,
            use_container_width=True
        )

        # 经纬度数据处理
        map_df = filtered_df.copy()

        map_df["latitude"] = pd.to_numeric(
            map_df["latitude"],
            errors="coerce"
        )

        map_df["longitude"] = pd.to_numeric(
            map_df["longitude"],
            errors="coerce"
        )

        map_df = map_df.dropna(
            subset=[
                "latitude",
                "longitude"
            ]
        )

        # 过滤无效坐标
        map_df = map_df[
            map_df["latitude"].between(-90, 90)
            &
            map_df["longitude"].between(-180, 180)
        ]

        # 显示地图
        st.subheader("GNSS站点空间分布")

        if map_df.empty:

            st.info(
                "当前没有有效站点坐标可用于地图显示。"
            )

        else:

            st.map(
                map_df,
                latitude="latitude",
                longitude="longitude"
            )


# ==================================================
# 8. GNSS数据查询
# ==================================================

elif page == "数据查询":

    st.title("🔍 GNSS数据查询")

    st.write(
        "按照站点、观测日期和文件类型"
        "检索RINEX观测数据。"
    )

    files_df, error = load_rinex_files()

    if error:

        st.warning(error)

    elif files_df.empty:

        st.info(
            "RINEX文件索引已建立，"
            "暂无真实文件记录。"
        )

    else:

        # 获取站点选项
        station_options = sorted(
            files_df["station_code"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        station = st.selectbox(
            "选择GNSS站点",
            ["全部站点"] + station_options
        )

        # 获取文件类型
        type_options = sorted(
            files_df["file_type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        file_type = st.selectbox(
            "选择文件类型",
            ["全部类型"] + type_options
        )

        # 日期范围
        date_range = st.date_input(
            "选择观测日期范围",
            value=[]
        )

        # 查询按钮
        if st.button(
            "查询数据",
            type="primary"
        ):

            result = files_df.copy()

            # 按站点筛选
            if station != "全部站点":

                result = result[
                    result["station_code"] == station
                ]

            # 按文件类型筛选
            if file_type != "全部类型":

                result = result[
                    result["file_type"] == file_type
                ]

            # 按日期筛选
            if len(date_range) == 2:

                start_date, end_date = date_range

                dates = pd.to_datetime(
                    result["observation_date"],
                    errors="coerce"
                )

                result = result[
                    dates.between(
                        pd.Timestamp(start_date),
                        pd.Timestamp(end_date)
                    )
                ]

            elif len(date_range) == 1:

                st.warning(
                    "请同时选择开始日期和结束日期。"
                )

                st.stop()

            # 显示查询结果
            st.metric(
                "查询结果数量",
                len(result)
            )

            st.dataframe(
                result,
                hide_index=True,
                use_container_width=True
            )

            if result.empty:

                st.info(
                    "没有找到符合条件的RINEX文件。"
                )


# ==================================================
# 9. GNSS数据下载
# ==================================================

elif page == "数据下载":

    st.title("📥 GNSS数据下载")

    st.write(
        "GNSS观测数据下载中心"
    )

    files_df, error = load_rinex_files()

    if error:

        st.warning(error)

    elif files_df.empty:

        st.info(
            "暂无可下载的GNSS文件。"
        )

    else:

        st.subheader("RINEX文件列表")

        # 只展示文件元数据
        st.dataframe(
            files_df,
            hide_index=True,
            use_container_width=True
        )

        st.warning(
            "当前仅展示文件索引，"
            "尚未连接真实文件存储服务，"
            "暂不支持下载。"
        )

    st.caption(
        "后续将实现单文件下载、"
        "批量下载和大文件下载任务。"
    )
