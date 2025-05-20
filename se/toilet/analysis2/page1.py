import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go
from geopy.distance import geodesic


tourism_df = pd.read_csv('../../../public/asset/data/yc_df2.csv')

# .shp 파일 불러오기 (shx, dbf도 같이 필요!)

emd = gpd.read_file('../data2/emd/emd.shp', encoding='cp949')

# GeoJSON으로 저장
emd = emd[emd['EMD_NM'].isin(['신녕면', '청통면', '화산면', '화남면', '화북면', '자양면', '임고면', '고경면', '중앙면', '동부면', '서부면', '완산면', '남부면', '금호면', '북안면', '대창면'])]
import tempfile
import os

# 임시 경로만 확보하고 close
with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
    temp_path = tmp.name  # 경로 저장

# 파일 닫힌 후 저장
emd.to_file(temp_path, driver="GeoJSON")

emd.columns
print(emd.crs)
emd = emd.to_crs(epsg=4326)  # 위경도 좌표계로 변환
emd.to_file("yc_emd.geojson", driver="GeoJSON")
# 1. 지도 기본 객체
m = folium.Map(location=[35.9704, 128.9408], zoom_start=12)

# 2. 읍면동 경계 추가
folium.GeoJson(
    data="yc_emd.geojson",
    name="읍면동 경계",
    tooltip=folium.GeoJsonTooltip(fields=['EMD_NM'], aliases=["읍면동:"]),
    style_function=lambda feature: {
        'fillColor': '#dddddd',
        'color': 'black',
        'weight': 1.5,
        'fillOpacity': 0.3,
    },
    highlight_function=lambda x: {
        'color': 'blue',
        'weight': 3,
        'fillOpacity': 0.6
    }
).add_to(m)

m.save("map_emd.html")



def on_each(feature, layer):
    layer.on('click', """
        function(e) {
            var town = e.target.feature.properties['읍면동명'];
            alert("선택된 읍면동: " + town);
        }
    """)

# JavaScript 커스텀 이벤트 삽입 (Shiny 연동 시 필요)
m.get_root().html.add_child(folium.Element("""
<script>
    function onMapLoad() {
        let layers = document.getElementsByClassName("leaflet-interactive");
        for (let i = 0; i < layers.length; i++) {
            layers[i].addEventListener("click", function(e) {
                let name = this.getAttribute("title");
                alert("선택된 읍면동: " + name);
            });
        }
    }
    setTimeout(onMapLoad, 1000);
</script>
"""))

m.save("map_with_click.html")


selected_df = tourism_df[tourism_df['LEGALDONG_NM'] == '자양면']
# 1. 관광지 좌표 기준
poi_coord = (selected_df['LC_LA'], selected_df['LC_LO'])

# 2. 모든 화장실 좌표랑 거리 계산 → geopy 또는 haversine 사용

def get_nearby_toilets(poi_coord, toilet_df, radius=500):
    result = []
    for _, row in toilet_df.iterrows():
        toilet_coord = (row['WGS84위도'], row['WGS84경도'])
        dist = geodesic(poi_coord, toilet_coord).meters
        if dist <= radius:
            result.append((row['화장실명'], dist))
    return sorted(result, key=lambda x: x[1])
