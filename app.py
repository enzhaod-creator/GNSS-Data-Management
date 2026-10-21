import pandas as pd
from pathlib import Path
import streamlit as st
from datetime import date

# 读取真实GNSS站点信息
def load_stations():
    csv_path = (
        Path(__file__).resolve().parent
        / "data"
        / "stations.csv"
    )

    if not csv_path.exists():
        return pd.DataFrame(), "未找到站点信息文件"

    try:
        df = pd.read_csv(
            csv_path,
            dtype={"station_code": "string"}
        )

        required_columns = [
            "station_code",
            "station_name",
            "latitude",
            "longitude",
            "status"
        ]

        if not all(col in df.columns for col in required_columns):
            return pd.DataFrame(), "站点文件缺少必要字段"

        return df, None

    except Exception as e:
        return pd.DataFrame(), f"站点文件读取失败：{e}"


# 读取RINEX文件索引
def load_rinex_files():

    csv_path = (
        Path(__file__).resolve().parent
        / "data"
        / "rinex_files.csv"
    )

    if not csv_path.exists():
        return pd.DataFrame(), "尚未创建RINEX文件索引"

    try:
        df = pd.read_csv(
            csv_path,
            dtype={
                "file_id": "string",
                "station_code": "string",
                "filename": "string",
                "storage_path": "string"
            }
        )

        required_columns = [
            "file_id",
            "station_code",
            "filename",
            "observation_date",
            "file_type",
            "file_size",
            "storage_path"
        ]

        if not all(col in df.columns for col in required_columns):
            return pd.DataFrame(), "RINEX索引缺少必要字段"

        return df, None

    except Exception as e:
        return pd.DataFrame(), f"读取RINEX索引失败：{e}"

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

    # 从CSV读取真实站点信息
    stations_df, station_error = load_stations()

    col1, col2, col3 = st.columns(3)

    # 动态统计真实站点数量
    if station_error:
        col1.metric("GNSS站点数量", "未接入")
        st.warning(station_error)
    else:
        col1.metric(
            "GNSS站点数量",
            len(stations_df)
        )

   
# 从文件索引读取统计信息
files_df, file_error = load_rinex_files()

if file_error:
    col2.metric("RINEX文件数量", "未接入")
    col3.metric("数据存储量", "未接入")

else:
    col2.metric(
        "RINEX文件数量",
        len(files_df)
    )

    if files_df.empty:
        total_bytes = 0
    else:
        total_bytes = pd.to_numeric(
            files_df["file_size"],
            errors="coerce"
        ).fillna(0).sum()

    total_gb = total_bytes / (1024 ** 3)

    col3.metric(
        "数据存储量",
        f"{total_gb:.2f} GB"
    )


    st.subheader("系统功能")

    st.info(
        "本系统用于GNSS观测数据的存储、"
        "管理、查询和下载。"
    )

    if not station_error and stations_df.empty:
        st.warning("站点信息表已建立，等待录入真实GNSS站点。")

    elif not station_error:
        st.success("GNSS站点数据已成功读取。")

    st.caption(
        "RINEX文件统计和存储量统计将在"
        "后续接入真实GNSS文件后启用。"
    )

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

# 5. GNSS数据查询
elif page == "数据查询":

    st.title("🔍 GNSS数据查询")
    st.write("按照站点、日期和文件类型检索RINEX观测数据。")

    files_df, file_error = load_rinex_files()

    if file_error:
        st.warning(file_error)

    elif files_df.empty:
        st.info("RINEX文件索引已建立，暂无真实文件记录。")

    else:
        # 站点筛选
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

        # 文件类型筛选
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

        # 观测日期范围
        date_range = st.date_input(
            "选择观测日期范围",
            value=[]
        )

        if st.button("查询数据", type="primary"):

            result = files_df.copy()

            if station != "全部站点":
                result = result[
                    result["station_code"] == station
                ]

            if file_type != "全部类型":
                result = result[
                    result["file_type"] == file_type
                ]

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

            st.metric("查询结果数量", len(result))

            st.dataframe(
                result,
                hide_index=True,
                use_container_width=True
            )

            if result.empty:
                st.info("没有找到符合条件的RINEX文件。")


# 6. 数据下载
elif page == "数据下载":

    st.title("📥 GNSS数据下载")

    st.write("后续将提供RINEX观测文件下载。")

    st.info("文件下载模块正在开发中。")
