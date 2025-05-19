import requests
import folium

# REST API 키
KAKAO_API_KEY = "fe0c4ebbe878bf51f535c24615d3ca23"

# 카카오 장소 검색
url = "https://dapi.kakao.com/v2/local/search/keyword.json"
headers = {
    "Authorization": f"KakaoAK {KAKAO_API_KEY}"
}
params = {
    "query": "영천시 카페",
    "size": 15
}
res = requests.get(url, headers=headers, params=params)
places = res.json()['documents']

# folium 지도 생성 (영천시청 중심)
m = folium.Map(location=[35.9734, 128.9408], zoom_start=13)

# 마커 추가
for p in places:
    name = p['place_name']
    lat = float(p['y'])
    lng = float(p['x'])
    addr = p['road_address_name']
    
    folium.Marker(
        location=[lat, lng],
        popup=f"{name}<br>{addr}",
        tooltip=name,
        icon=folium.Icon(color='blue')
    ).add_to(m)

# HTML로 저장
m.save("yeongcheon_cafes_map.html")
print("✅ 지도 저장 완료! yeongcheon_cafes_map.html 파일 열어보세요.")

import webbrowser

webbrowser.open("yeongcheon_cafes_map.html")










from shiny import App, ui, render, reactive
import requests
import folium
import os

categories = {
    "카페": "CE7",
    "관광지": "AT4",
    "문화시설": "CT1",
    "전통시장": "OL7"
}

KAKAO_API_KEY = "fe0c4ebbe878bf51f535c24615d3ca23"

def get_places(category_code):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "category_group_code": category_code,
        "x": "128.9408",
        "y": "35.9734",
        "radius": 10000
    }
    res = requests.get(url, headers=headers, params=params)
    return res.json()["documents"]

app_ui = ui.page_fluid(
    ui.input_select("category", "카테고리 선택", list(categories.keys())),
    ui.output_ui("map")
)

def server(input, output, session):
    @reactive.Calc
    def places():
        code = categories[input.category()]
        return get_places(code)
    
    @output
    @render.ui
    def map():
        m = folium.Map(location=[35.9734, 128.9408], zoom_start=13)
        for p in places():
            folium.Marker(
                [float(p['y']), float(p['x'])],
                popup=p['place_name']
            ).add_to(m)
        filepath = "map.html"
        m.save(filepath)
        return ui.include_html(filepath)

app = App(app_ui, server)

