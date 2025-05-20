# shiny 대시보드용 전체 구조 제안

from shiny import App, ui, render, reactive
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from geopy.distance import geodesic
import tempfile

# 데이터 로드
emd = gpd.read_file("yc_emd.geojson")
tourism_df = pd.read_csv("../../../public/asset/data/yc_df2.csv")
toilet_df = pd.read_csv("../data/toilet.csv")  # 실제 경로에 맞게 수정
# 임시 경로만 확보하고 close

with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
    temp_path = tmp.name  # 경로 저장

# 파일 닫힌 후 저장
emd.to_file(temp_path, driver="GeoJSON")

# UI 구성
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("town", "읍면동 선택", sorted(emd['EMD_NM'].unique())),
        ui.input_numeric("radius", "반경(m)", 500, min=100, max=2000)
    ),
    ui.output_ui("map"),
    ui.output_table("result")
)

# 거리 계산 함수
def get_nearby_toilets(poi_df, toilet_df, radius=500):
    result = []
    for _, poi in poi_df.iterrows():
        try:
            poi_coord = (float(poi['LC_LA']), float(poi['LC_LO']))
        except ValueError:
            continue
        for _, row in toilet_df.iterrows():
            toilet_coord = (row['WGS84위도'], row['WGS84경도'])
            dist = geodesic(poi_coord, toilet_coord).meters
            if dist <= radius:
                result.append({
                    '관광지명': poi['TOURIST_SPOT_NM'],
                    '화장실명': row['화장실명'],
                    '거리(m)': round(dist)
                })
    return pd.DataFrame(result)

# 서버 로직
def server(input, output, session):
    @reactive.Calc
    def filtered():
        return tourism_df[tourism_df['LEGALDONG_NM'] == input.town()]

    @output
    @render.ui
    def map():
        m = folium.Map(location=[35.9704, 128.9408], zoom_start=12)

        # 읍면동 경계
        folium.GeoJson(
            data=emd.name,
            name="읍면동 경계",
            tooltip=folium.GeoJsonTooltip(fields=['EMD_NM']),
            style_function=lambda feature: {
                'fillColor': '#dddddd',
                'color': 'black',
                'weight': 1.5,
                'fillOpacity': 0.3,
            },
        ).add_to(m)

        # 관광지 마커
        cluster = MarkerCluster().add_to(m)
        for _, row in filtered().iterrows():
            folium.Marker(
                location=[row['LC_LA'], row['LC_LO']],
                popup=row['TOURIST_SPOT_NM']
            ).add_to(cluster)

        return ui.HTML(m._repr_html_())

    @output
    @render.table
    def result():
        return get_nearby_toilets(filtered(), toilet_df, radius=input.radius())

app = App(app_ui, server)