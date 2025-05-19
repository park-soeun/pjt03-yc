from shiny import App, ui, render, reactive
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from htmltools import HTML
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WWW_DIR = os.path.join(BASE_DIR, "www")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "www")

# www 디렉토리 없으면 만들기
os.makedirs(WWW_DIR, exist_ok=True)

def make_empty_map():
    m = folium.Map(location=[35.9677, 128.9397], zoom_start=11)
    m.save(os.path.join(WWW_DIR, "filtered_map.html"))

make_empty_map()

# 샘플 데이터
locations = pd.read_csv('../public/asset/data/yc_df2.csv')

location_df = pd.DataFrame(locations)
eupmyeondong_list = sorted(location_df["LEGALDONG_NM"].unique())
thema_list = sorted(location_df["CL_NM"].unique())

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "emd_filter",
            "읍면동 선택:",
            choices={"": "읍면동을 선택해주세요"} | {v: v for v in eupmyeondong_list},
            selected=""
        ),
        ui.input_checkbox_group("theme_filter", "관광지 테마:", choices=thema_list, selected=thema_list),
    ),
    ui.output_ui("map")
)
def server(input, output, session):
    @reactive.calc
    def filtered_df():
        df = location_df.copy()
        if input.emd_filter() != "":
            df = df[df["LEGALDONG_NM"] == input.emd_filter()]
        df = df[df["CL_NM"].isin(input.theme_filter())]
        return df

    @output
    @render.ui
    def map():
        df = filtered_df()
        m = folium.Map(location=[35.9677, 128.9397], zoom_start=11)
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            folium.Marker(
                location=[row["LC_LA"], row["LC_LO"]],
                popup=f"{row['POI_NM']} ({row['CL_NM']})",
                tooltip=row["POI_NM"]
            ).add_to(marker_cluster)

        # HTML 파일로 저장 (www 폴더가 프로젝트 루트에 있어야 함)
        m.save("www/filtered_map.html")

        # iframe으로 삽입
        return ui.tags.iframe(src="/filtered_map.html", width="100%", height="600")

app = App(app_ui, server, static_assets=STATIC_DIR)
