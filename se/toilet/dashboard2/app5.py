# shiny 대시보드용 전체 구조 제안

from shiny import App, ui, render, reactive
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from geopy.distance import geodesic
import tempfile
import os

# 데이터 로드
emd = gpd.read_file("yc_emd.geojson")
tourism_df = pd.read_csv("../../../public/asset/data/yc_df2.csv")
toilet_df = pd.read_csv("../data/toilet.csv")  # 실제 경로에 맞게 수정

# GeoJSON 파일 임시 저장 (Shiny용)
with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
    temp_path = tmp.name
emd.to_file(temp_path, driver="GeoJSON")

# UI 구성
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("town", "읍면동 선택 (미선택 시 전체)", ["전체"] + sorted(emd['EMD_NM'].unique())),
        ui.input_numeric("radius", "반경(m)", 500, min=100, max=2000)
    ),
    ui.output_ui("map"),
    ui.output_table("result")
)

# 거리 계산 함수
def get_nearby_toilets(poi_df, toilet_df, radius=500):
    if len(poi_df) > 4:
        return pd.DataFrame([])  # 3개 이상이면 계산하지 않음
    result = []
    for _, poi in poi_df.iterrows():
        try:
            lat = float(poi['LC_LA'])
            lon = float(poi['LC_LO'])
            if pd.isna(lat) or pd.isna(lon):
                continue
            poi_coord = (lat, lon)
        except (ValueError, TypeError):
            continue
        for _, row in toilet_df.iterrows():
            if pd.isna(row['WGS84위도']) or pd.isna(row['WGS84경도']):
                continue
            toilet_coord = (row['WGS84위도'], row['WGS84경도'])
            dist = geodesic(poi_coord, toilet_coord).meters
            if dist <= radius:
                result.append({
                    '관광지명': poi.get('POI_NM', '이름 없음'),
                    '화장실명': row.get('화장실명', '이름 없음'),
                    '거리(m)': round(dist)
                })
    return pd.DataFrame(result)

# 서버 로직
def server(input, output, session):
    @reactive.Calc
    def filtered():
        if input.town() == "전체":
            return tourism_df
        return tourism_df[tourism_df['LEGALDONG_NM'] == input.town()]

    @output
    @render.ui
    def map():
        # 선택된 읍면동 중심 좌표로 지도 초기화
        if input.town() != "전체":
            selected_geom = emd[emd['EMD_NM'] == input.town()].geometry
            if not selected_geom.empty:
                centroid = selected_geom.iloc[0].centroid
                m = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)
            else:
                m = folium.Map(location=[35.9704, 128.9408], zoom_start=12)
        else:
            m = folium.Map(location=[35.9704, 128.9408], zoom_start=12)

        def style_function(feature):
            selected = input.town()
            if selected != "전체" and feature['properties']['EMD_NM'] == selected:
                return {'fillColor': 'orange', 'color': 'red', 'weight': 2.5, 'fillOpacity': 0.5}
            return {'fillColor': '#dddddd', 'color': 'black', 'weight': 1.5, 'fillOpacity': 0.3}

        geo = folium.GeoJson(
            data=temp_path,
            name="읍면동 경계",
            tooltip=folium.GeoJsonTooltip(fields=['EMD_NM']),
            style_function=style_function,
        ).add_to(m)

        # 관광지 마커
        cluster = MarkerCluster().add_to(m)
        for _, row in filtered().iterrows():
            try:
                lat = float(row['LC_LA'])
                lon = float(row['LC_LO'])
                if pd.notna(lat) and pd.notna(lon):
                    folium.Marker(
                        location=[lat, lon],
                        popup=row.get('POI_NM', '이름 없음')
                    ).add_to(cluster)
            except (ValueError, TypeError):
                continue

        return ui.HTML(m._repr_html_())

    @output
    @render.table
    def result():
        return get_nearby_toilets(filtered(), toilet_df, radius=input.radius())

app = App(app_ui, server)
