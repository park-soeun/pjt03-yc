import pandas as pd
import folium
from folium.plugins import MarkerCluster

# 샘플 관광지 데이터 로딩
data = pd.read_csv('../public/asset/data/yc_data.csv')

df = pd.DataFrame(data)

# folium 지도 생성
map_center = [35.9677, 128.9397]
m = folium.Map(location=map_center, zoom_start=11)

# 마커 클러스터 추가
marker_cluster = MarkerCluster().add_to(m)

# 마커 추가
for _, row in df.iterrows():
    folium.Marker(
        location=[row["LC_LA"], row["LC_LO"]],
        popup=f"{row['POI_NM']} ({row['CL_NM']})",
        tooltip=row["POI_NM"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# 저장
m.save("./yeongcheon_overview.html")
