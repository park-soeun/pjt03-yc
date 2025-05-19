import geopandas as gpd
from ipyleaflet import Map, Marker, GeoData, WidgetControl
from ipywidgets import HTML, VBox, Layout

# 🗺️ 지도 생성
m = Map(center=(35.9676, 128.9383), zoom=12)

# 📍 마커 생성 (영천시청)
marker = Marker(location=(35.9676, 128.9383), draggable=False)
m.add_layer(marker)

# ✅ SHP 또는 GeoJSON에서 영천시 경계 불러오기 (EPSG:4326으로 변환)
gdf = gpd.read_file("C:/Users/USER/Desktop/my_blog/my_blog/project/pjt03-yc/sp/ychsi-map/ychsi.shp")  # 또는 geojson 경로
gdf = gdf.to_crs(epsg=4326)

# ✅ ipyleaflet GeoData로 변환하여 지도에 추가
geo_layer = GeoData(
    geo_dataframe=gdf,
    style={
        'color': 'blue',           # 테두리 색
        'weight': 1,               # 선 굵기
        'fillColor': 'transparent' # 채우지 않음
    },
    name='영천시 테두리'
)
m.add_layer(geo_layer)

# ℹ️ 오른쪽 상단 정보 위젯 박스
info_html = HTML()
info_html.value = ""

info_box = VBox([info_html], layout=Layout(
    border='1px solid black',
    padding='10px',
    background_color='white',
    width='250px',
    display='none'
))

control = WidgetControl(widget=info_box, position='topright')
m.add_control(control)

# 🖱️ 마커 클릭 시 정보 출력
def on_marker_click(**kwargs):
    if kwargs.get('type') == 'click':
        info_html.value = """
        <b>📍 영천시청</b><br>
        위도: 35.9676<br>
        경도: 128.9383<br>
        경상북도 영천시의 행정 중심지입니다.
        """
        info_box.layout.display = 'block'

marker.on_click(on_marker_click)

m

