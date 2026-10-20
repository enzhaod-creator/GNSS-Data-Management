
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

# 4. 站点管理
elif page == "站点管理":

    st.title("📍 GNSS站点管理")

    st.write("后续将展示GNSS站点信息。")

    st.dataframe(
        {
            "站点编号": ["BJFS", "SHAO", "WUHN"],
            "站点名称": ["北京测试站", "上海测试站", "武汉测试站"],
            "状态": ["示例", "示例", "示例"]
        },
        hide_index=True,
        use_container_width=True
    )

    st.caption("以上为模拟数据，并非真实数据库记录。")

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
