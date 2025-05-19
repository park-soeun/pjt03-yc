from shiny import App, ui, render, reactive
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from htmltools import HTML

# 샘플 데이터
locations = pd.read_csv('../public/asset/data/yc_data.csv')

location_df = pd.DataFrame(locations)
eupmyeondong_list = sorted(location_df["LEGALDONG_NM"].unique())
thema_list = sorted(location_df["CL_NM"].unique())

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("emd_filter", "읍면동 선택:", choices=["전체"] + eupmyeondong_list, selected="전체"),
        ui.input_checkbox_group("theme_filter", "관광지 테마:", choices=thema_list, selected=thema_list),
    ),
    ui.output_ui("map")
)

def server(input, output, session):
    @reactive.calc
    def filtered_df():
        df = location_df.copy()
        if input.emd_filter() != "전체":
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

        html = m.get_root().render()

        # ✅ div로 감싸서 높이 강제 지정
        return ui.HTML(f"""
            <div style='width:100%; height:600px'>
                {html}
            </div>
        """)

app = App(app_ui, server)
