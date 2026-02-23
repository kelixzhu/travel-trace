import streamlit as st
from PIL import Image
import exifread
import pandas as pd

# 1. 设置页面全局属性（宽屏显示）
st.set_page_config(page_title="TravelTrace 旅迹", layout="wide")

st.title("✈️ TravelTrace 旅迹")
st.markdown("上传你的旅行照片，自动生成足迹地图与时光相册。")

# 2. 辅助函数：将照片中隐藏的 GPS 数据转换为地图能识别的十进制坐标
def get_decimal_from_dms(dms, ref):
    degrees = dms[0].num / dms[0].den
    minutes = dms[1].num / dms[1].den / 60.0
    seconds = dms[2].num / dms[2].den / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return round(degrees + minutes + seconds, 5)

# 3. 辅助函数：解析照片信息
def get_exif_data(image_file):
    tags = exifread.process_file(image_file, details=False)
    lat, lon, date_time = None, None, "未知时间"
    
    # 提取拍摄时间
    if 'EXIF DateTimeOriginal' in tags:
        date_time = str(tags['EXIF DateTimeOriginal'])
        
    # 提取经纬度
    if 'GPS GPSLatitude' in tags and 'GPS GPSLatitudeRef' in tags:
        lat = get_decimal_from_dms(tags['GPS GPSLatitude'].values, tags['GPS GPSLatitudeRef'].printable)
    if 'GPS GPSLongitude' in tags and 'GPS GPSLongitudeRef' in tags:
        lon = get_decimal_from_dms(tags['GPS GPSLongitude'].values, tags['GPS GPSLongitudeRef'].printable)
        
    return lat, lon, date_time

# 4. 界面核心：照片上传区
uploaded_files = st.file_uploader("请在这里拖入或点击上传照片 (支持 JPG/PNG)", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    photo_data = []
    
    # 遍历处理每一张用户上传的照片
    for file in uploaded_files:
        lat, lon, date_time = get_exif_data(file)
        photo_data.append({
            "file": file,
            "lat": lat,
            "lon": lon,
            "time": date_time
        })
        
    # 筛选出成功提取到坐标的照片，用来画地图
    map_data = [p for p in photo_data if p['lat'] is not None and p['lon'] is not None]
    
    # 5. 左右分屏显示逻辑 (左边占2份宽度，右边占1份)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 你的旅行足迹")
        if map_data:
            # 将数据转换成表格格式，喂给自带的地图组件
            df = pd.DataFrame(map_data)
            st.map(df, latitude='lat', longitude='lon', zoom=11)
        else:
            st.info("提示：上传的照片中没有检测到地理位置 (GPS) 信息。请确保手机拍照时开启了位置记录。")
            
    with col2:
        st.subheader("📸 时光相册")
        for p in photo_data:
            # 显示时间和坐标文本
            st.caption(f"🕒 拍摄时间: {p['time']}")
            if p['lat'] and p['lon']:
                st.caption(f"📍 坐标: {p['lat']}, {p['lon']}")
            else:
                st.caption("📍 位置: 未知")
            
            # 显示照片缩略图
            image = Image.open(p['file'])
            st.image(image, use_container_width=True)
            st.divider() # 分割线
            
    # 预留给下一步的游记生成按钮
    if st.button("✨ 自动生成游记"):
        st.success("基础地图框架已跑通！下一步我们将接入 AI 模型来写游记。")
else:
    st.info("请在上方框内上传照片开始体验。")
