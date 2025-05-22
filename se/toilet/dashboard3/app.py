from shiny import App, reactive, render, ui
import pandas as pd
import plotly.express as px
import geopandas as gpd
from shinywidgets import render_widget, output_widget
import processing, plots
from plots import plot_open_type_pie, plot_weekend_pie
from htmltools import tags
import os
import folium
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.colors import LogNorm, to_hex
from folium.plugins import MarkerCluster
from htmltools import HTML
import plotly.graph_objects as go
import matplotlib.font_manager as fm
from shared import font_prop



STATIC_DIR = os.path.join(os.path.dirname(__file__), "www")


# 📦 데이터 전처리
kb_df = processing.load_toilet_data()
df_plot = processing.get_toilet_count_by_region(kb_df)
pop_df = processing.load_population_data()
df_per_10k = processing.get_toilet_per_10k(kb_df, pop_df)
area_df = processing.load_area_data()


kb_df = processing.load_toilet_data()
pop_df = processing.load_population_data()

count_df = processing.get_toilet_count_by_region(kb_df)
df_per_10k = processing.get_toilet_per_10k(kb_df, pop_df)
df_density = processing.get_toilet_density(kb_df, area_df)
df_growth = processing.get_toilet_growth_trend(kb_df)
yearly_df = processing.get_toilet_growth_trend(kb_df)
combined_top_bottom_yc = processing.get_combined_growth_comparison(kb_df)
kb_path = './data/kb_df.csv'
yc_path = './data/yc_df.csv'

# 전처리
kb_df, yc_df = processing.load_processed_opening_data(kb_path, yc_path)

kb_df = pd.read_csv('./data/kb_df.csv')
yc_df = pd.read_csv('./data/yc_df.csv')

# 2페이지
yeongcheon_rates, gyeongbuk_rates = processing.prepare_radar_data()
compare_df = processing.load_and_prepare_comparison_data("./data/kb_df.csv")


API_KEY = "42CA-2DDB-565B-5200-FD2F-F620-ADB3-718A"

df_lactation = processing.fetch_lactation_rooms(API_KEY)
df_long = processing.prepare_grouped_bar_data("./data/kb_df.csv", df_lactation)
lactation_type_df = processing.preprocess_lactation_type(API_KEY)
bell_df = processing.preprocess_emergency_bell(kb_df)
cctv_df = processing.preprocess_cctv(kb_df)
diaper_df = processing.preprocess_diaper(kb_df)
yeongcheon, gyeongbuk_avg = processing.preprocess_child_fixture_rates(kb_df)

# === hs

gb_df = pd.read_csv("data/kb_df.csv")
gb_pop = pd.read_csv("data/pop_2023.csv", skiprows=1)
yc_pop = pd.read_csv("data/pop_emd_2020.csv", skiprows=1)

replace_map = {"문외동27": "문외동", "양항리": "임고면", "치산리": "신녕면"}
yc_df["읍면동명"] = yc_df["읍면동명"].replace(replace_map)

emd_list = sorted(yc_df["읍면동명"].dropna().unique().tolist())



# 지도 파일 데이터
GDF_2KM_PATH = "./2km_grid.geojson"
BOUNDARY_PATH = "./yeongcheon_boundary.geojson"
COORD_CSV_PATH = "./yc_address_coords.csv"
gdf_2km = gpd.read_file(GDF_2KM_PATH)
gdf_boundary = gpd.read_file(BOUNDARY_PATH)
#
# coord_df = pd.read_csv(COORD_CSV_PATH)
coord_df = (
    yc_df[["WGS84위도", "WGS84경도", "소재지도로명주소"]]
    .dropna(subset=["WGS84위도", "WGS84경도"])
    .copy()
)

# 선택적으로 컬럼명 변경
coord_df.columns = ["lat", "lon", "address"]

coord_df.info()
geojson_data = gdf_boundary.__geo_interface__
# === 



# ----------- 함수: 누적 그래프 데이터 --------------
def get_stacked_data(yc_df, cols):
    temp = yc_df.copy()
    temp[cols] = temp[cols].astype(bool)
    temp["설치된항목수"] = temp[cols].sum(axis=1)
    summary_df = temp.groupby("읍면동명")[cols + ["설치된항목수"]].sum()
    summary_df["화장실개수"] = temp.groupby("읍면동명").size()
    stacked_data = summary_df[cols].astype(int)
    stacked_data = stacked_data.loc[
        summary_df["설치된항목수"].sort_values(ascending=False).index
    ]
    return stacked_data
 
def classify_open_type(row):
    기본 = str(row['개방시간']) if pd.notna(row['개방시간']) else ''
    상세 = str(row['개방시간상세']) if pd.notna(row['개방시간상세']) else ''
    combined = 기본 + ' ' + 상세
    combined = combined.lower().replace(' ', '').replace('~', '-')

    if any(kw in combined for kw in ['24', '00:00-24:00', '상시', '연중무휴']):
        return '24시간'
    elif any(kw in combined for kw in [
        '09', '06', '07', '08', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
        '정시', '근무시간', '영업시간'
    ]):
        return '주간개방'
    elif any(kw in combined for kw in ['행사', '경기', '개장시', '필요시', '학생', '동절기', '이용중단', '야영장']):
        return '제한적 운영'
    else:
        return '정보없음'


def check_weekend_open(row):
    text = str(row['개방시간']) + ' ' + str(row['개방시간상세'])
    text = text.replace(' ', '').lower()

    if '주말' in text and '미개방' in text:
        return '미개방'
    if '공휴일미개방' in text or '휴일미개방' in text:
        return '미개방'
    if '주말' in text or '공휴일' in text or '토요일' in text or '일요일' in text:
        return '개방'
    if '연중무휴' in text or '24시간' in text or '상시' in text:
        return '개방'
    return '불명확'


kb_df['개방시간유형'] = kb_df.apply(classify_open_type, axis=1)
kb_df['주말개방여부'] = kb_df.apply(check_weekend_open, axis=1)

yc_df['개방시간유형'] = yc_df.apply(classify_open_type, axis=1)
yc_df['주말개방여부'] = yc_df.apply(check_weekend_open, axis=1)

# ==== UI ====

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(rel="stylesheet", href="styles.css")
    ),
    ui.page_navbar(
            ui.nav_panel("🚽 영천 vs 경북",
            ui.layout_column_wrap(
                width="1/1",
                gap="20px",
                ),

                ui.layout_columns(
                    ui.card(
                        ui.h3("📊 경북 속 영천시, 공공화장실 수준은?"),
                        ui.HTML("경북 타 도시에 비해 영천시는<br>평균 이하의 공공화장실을 보유하고 있으며, 분포 지역도 편중되어 있습니다."),
                        class_="bg-sky-100 text-sky-900 p-4 rounded-xl shadow-md"
                    ),
                    ui.card(
                        ui.layout_columns(
                            ui.value_box("🚻 총 화장실 수", "115개"),
                            ui.value_box("👥 인구 1만명당 수", "11.22개"),
                            ui.value_box("📐 ㎢당 밀도", "0.08개"),
                        ),
                        class_="bg-white p-4 rounded-2xl shadow-md"
                    ),
                    col_widths=(5, 7)
                ),

                # 📊 SECTION 1: 절대 수 + 인구당 수
                ui.layout_columns(
                    ui.card(
                        ui.card_header("① 시군구별 전체 화장실 수"),
                        output_widget("plot_total_count_"),
                        ui.card_footer(
                            "영천시 공공화장실은 115개로, 구미시(502개) 대비 약 5분의 1 수준"
                        ),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.card_header("② 인구 1만명당 화장실 수"),
                        output_widget("plot_per_10k"),
                        ui.card_footer(
                            "영천시 1만명당 화장실 수는 11개로, 영양군(123개) 대비 10분의 1 수준"
                        ),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    
                    ui.card(
                        ui.card_header("③ 면적당 화장실 수 (개/㎢)"),
                        output_widget("plot_density"),
                        ui.card_footer(
                            "영천시 면적당 화장실 수는 1.96개, 청송군(32.1개)과 16배 차이"
                        ),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                ),

               ui.layout_columns(
                    # 왼쪽: 증가 추이
                    ui.card(
                        ui.card_header("④ 화장실 설치 증가 추이 (2015~2023)"),
                        output_widget("plot_growth_comparison"),
                        ui.card_footer(
                            "최근 설치 수는 꾸준한 증가 추세, but 증가 폭은 크지 않음"
                        ),
                        class_="shadow-md p-3 rounded-xl",
                        width=6
                    ),
                    
                    # 오른쪽: 도넛 4개
                    ui.card(
                        ui.card_header("⑤ 개방시간/주말 개방 유형 도넛 차트"),
                        ui.navset_tab(
                            ui.nav_panel(
                                "개방시간",
                                ui.layout_columns(
                                    output_widget("plot_opening_gb"),
                                    output_widget("plot_opening_yc")
                                )
                            ),
                            ui.nav_panel(
                                "주말 개방",
                                ui.layout_columns(
                                    output_widget("plot_weekend_gb"),
                                    output_widget("plot_weekend_yc")
                                )
                            )
                        ),
                        ui.card_footer("야간·주말 이용 편의 높음"),
                        class_="shadow-md p-3 rounded-xl",
                        width=6
                    )
                ),
                    ui.layout_columns(
                        ui.card(
                            ui.h3("🤔 영천시 화장실 인프라, 얼마나 갖춰져 있을까?"),
                                ui.p("주요 편의시설 설치 현황을 통해 영천시 공공화장실의 질적 수준을 진단합니다."),
                                class_="bg-amber-100 text-gray-900 p-4 rounded-xl shadow-md"
                        ),
                        ui.card(
                            ui.layout_columns(
                                ui.value_box("🔔 비상벨 설치율:", "41.7%"),
                                ui.value_box("🎥 CCTV 설치율", "1.7%"),
                                ui.value_box("👶 기저귀 교환대 설치율","18.8%"),
                            col_widths=(4, 4, 4)
                            ),
                            class_="bg-white p-4 rounded-2xl shadow-md"
                        ),
                        col_widths=(5, 7)
                    ),

                        ui.layout_columns(
                            ui.card(
                                ui.card_header("① 영천시 vs 경북 평균: 편의시설 설치율"),
                                output_widget("infra_comparison"),
                                ui.card_footer("비상벨, CCTV, 어린이 화장실 등 주요 시설 설치율이 경북 평균과 비슷하거나 더 높음"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            ui.card(
                                ui.card_header("② 어린이 대변기 설치 여부"),
                                output_widget("plot_child_fixture"),
                                ui.card_footer("여아용은 경북 평균과 비슷, 남아용은 다소 낮아 균형적 확충 필요"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            
                        ),
                        ui.layout_columns(
                            ui.card(
                                ui.navset_tab(
                                    ui.nav_panel(
                                        "③ CCTV 설치율",
                                        output_widget("plot_cctv")
                                    ),
                                    ui.nav_panel(
                                        "④ 비상벨 설치율",
                                        output_widget("plot_emergency_bell")
                                    ),
                                    ui.nav_panel(
                                        "⑤ 기저귀 교환대 설치율",
                                        output_widget("plot_diaper")
                                    )
                                ),
                                ui.card_footer("CCTV는 설치율 최하위, 비상벨·기저귀교환대는 상위권 유지"),
                                class_="shadow-md p-3 rounded-xl"
                            ) 
                            
                        ),

                    ),
                    ui.nav_panel("🧻 읍면동별 화장실 현황",
                            ui.layout_columns(
                                ui.card(
                                    ui.card_header("읍면동 선택"),  # ✅ 카드 상단 제목
                                    ui.input_select("emd", None, choices=emd_list),  # ✅ 제목은 없애고 본문에 드롭다운만
                                    class_="shadow-md p-3 rounded-xl"
                                )
                            ),
                            ui.layout_columns(
                                ui.card(
                                    ui.card_header("히트맵 기반 영천시 읍면동별 화장실 인프라 분석"),
                                    ui.output_ui("updated_map"),
                                ),
                                ui.card(
                                    ui.card_header("영천시 읍면동 화장실 수 & 인프라 통계"),
                                    ui.navset_tab(
                                        ui.nav_panel("읍면동별 화장실 수",
                                            ui.output_plot("plot_count")
                                        ),
                                        ui.nav_panel("항목별 누적 비교",
                                            ui.output_plot("plot_stacked")
                                        )
                                    ),
                                    ui.output_ui("plot_summary"),
                                    class_="shadow-md p-3 rounded-xl"
                                    ),
                                col_widths=(7, 5)

                            ),
                            ui.layout_columns(
                                ui.card(
                                    ui.card_header("경북 내 영천시의 종합 설치 순위"),
                                    ui.output_ui("plot_rank"),
                            ),
                                ui.card(
                                    ui.card_header("영천시 내 공공화장실 취약 지역"),
                                    ui.HTML("""
                                            <iframe 
                                                src="./vul_loc.html" 
                                                width="100%" 
                                                height="500px" 
                                                style="border: none; margin-top: 16px;">
                                            </iframe>
                                        """),
                                    ui.output_ui("plot_vulnerable"),
                                ),
                        ),  
                    ),
                    title="영천 대똥여지도",
                    id="page",
            ),
)
# # 전처리 결과

# ✅ 서버 로직
def server(input, output, session):

    def plot_total_count_():
        return plots.plot_total_count(count_df)

    def plot_per_10k():
        return plots.plot_per_10k(df_per_10k)

    def plot_density():
        return plots.plot_density(df_density)

    def plot_growth_rate():
        return plots.plot_growth_rate(yearly_df)

    def plot_growth_comparison():
        return plots.plot_growth_comparison(combined_top_bottom_yc)
    
    def plot_opening_gb():
        return plot_open_type_pie(kb_df, "경북 전체")

    def plot_opening_yc():
        return plot_open_type_pie(yc_df, "영천시")

    def plot_weekend_gb():
        return plot_weekend_pie(kb_df, "경북 전체")

    def plot_weekend_yc():
        return plot_weekend_pie(yc_df, "영천시")
    
    def radar_install_compare():
        return plots.plot_radar_install_compare(yeongcheon_rates, gyeongbuk_rates)

    def bar_install_regions():
        return plots.plot_grouped_bar(df_long)
    
    def lactation_type_pie():
        return plots.plot_lactation_type_pie(lactation_type_df)
    def plot_emergency_bell():
        return plots.plot_emergency_bell(bell_df)
    def plot_cctv():
        return plots.plot_cctv(cctv_df)
    def plot_diaper():
        return plots.plot_diaper(diaper_df)
    
    def plot_child_fixture():
        return plots.plot_child_fixture_radar(yeongcheon, gyeongbuk_avg)
    
    def infra_comparison():
        return plots.plot_infra_comparison(compare_df)
        
    @output
    @render.plot
    def plot_stacked():
        selected = input.emd()
        cols = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
        colors = {
            "비상벨": "#4daf4a",
            "CCTV": "#377eb8",
            "기저귀교환대": "#ff7f00",
            "장애인화장실": "#984ea3",
            "어린이대변기": "#e41a1c",
        }
        stacked_data = get_stacked_data(yc_df, cols)

        bottom = np.zeros(len(stacked_data))

        for col in cols:
            barlist = plt.bar(
                stacked_data.index,
                stacked_data[col],
                bottom=bottom,
                label=col,
                color=colors[col],
            )
            for i, emd in enumerate(stacked_data.index):
                if emd != selected:
                    barlist[i].set_linewidth(2)
                    barlist[i].set_alpha(0.4)
                else:
                    barlist[i].set_linewidth(2)
                    barlist[i].set_edgecolor("gray")
            bottom += stacked_data[col]

        # ✅ 한글 폰트 적용 확실하게 다 해줌
        plt.xticks(rotation=45, ha="right", fontproperties=font_prop, fontsize=7)
        plt.yticks(fontproperties=font_prop)
        plt.ylabel("설치 수 (항목별)", fontproperties=font_prop)
        plt.title("읍면동별 공공화장실 항목별 설치 수 (누적 그래프)", fontsize=14, fontproperties=font_prop)

        # ✅ 범례도 전체 폰트 지정
        legend = plt.legend(title="항목")
        for text in legend.get_texts():
            text.set_fontproperties(font_prop)
        legend.get_title().set_fontproperties(font_prop)

        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        return plt.gcf()

    @output
    @render.plot
    def plot_count():
        selected = input.emd()
        toilet_count = yc_df["읍면동명"].value_counts().reset_index()
        toilet_count.columns = ["읍면동명", "화장실수"]
        toilet_count_sorted = toilet_count.sort_values("화장실수", ascending=False)
        plt.figure()
        bars = plt.bar(
            toilet_count_sorted["읍면동명"],
            toilet_count_sorted["화장실수"],
            color="cornflowerblue",
        )
        for i, emd in enumerate(toilet_count_sorted["읍면동명"]):
            if emd != selected:
                bars[i].set_linewidth(2)
                bars[i].set_alpha(0.3)
            else:
                bars[i].set_linewidth(2)
                bars[i].set_edgecolor("gray")       # 테두리 강조

            # 바 위에 숫자 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.3,
                f"{int(height)}",
                ha="center",
                fontsize=9,
                fontproperties=font_prop  # ✅ 텍스트에 폰트 적용
            )

        # ✅ 폰트 적용
        plt.xticks(rotation=45, ha="right", fontproperties=font_prop, fontsize = 7)
        plt.yticks(fontproperties=font_prop)
        plt.ylabel("공공화장실 수", fontproperties=font_prop)
        plt.title("영천시 읍면동별 공공화장실 수", fontproperties=font_prop)

        # ✅ 범례 없음 → 생략
        plt.tight_layout()
        return plt.gcf()
    
    @output
    @render.ui
    def updated_map():
        # 선택된 읍면동 지도 하이라이트
        selected = input.emd()
        m = folium.Map(
            location=[35.968, 128.941], zoom_start=13, tiles="CartoDB dark_matter"
        )

        # 히트맵 레이어
        vmin = max(gdf_2km["val"][gdf_2km["val"] > 0].min(), 1)
        vmax = gdf_2km["val"].max()
        norm = LogNorm(vmin=vmin, vmax=vmax)
        cmap = matplotlib.colormaps["RdYlGn_r"]

        def get_color(v):
            return "#ffffff" if v <= 0 else to_hex(cmap(norm(v)))

        def get_opacity(v):
            return 0.55 if v > 0 else 0.01

        heat_layer = folium.FeatureGroup(name="2km 격자 히트맵", control=False)
        for _, row in gdf_2km.iterrows():
            val = row["val"]
            folium.GeoJson(
                row.geometry,
                style_function=lambda feat, v=val: {
                    "fillColor": get_color(v),
                    "color": "gray",
                    "weight": 0.3,
                    "fillOpacity": get_opacity(v),
                },
                tooltip=folium.Tooltip(
                    f"인구: {val:.0f}<br>읍면동: {row.get('EMD_KOR_NM', '없음')}",
                    sticky=True,
                ),
            ).add_to(heat_layer) 
        heat_layer.add_to(m)

        # 마커 클러스터 레이어
        marker_layer = folium.FeatureGroup(name="주소 마커 클러스터", control=False)
        cluster = MarkerCluster()
        for _, row in coord_df.iterrows():
            lat, lon = row["lat"], row["lon"]
            folium.Marker(
                location=[lat, lon],
                # tooltip=addr,
                # popup=addr,
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(cluster)
        cluster.add_to(marker_layer)
        marker_layer.add_to(m)

        # 경계선
        folium.GeoJson(
            geojson_data,
            name="영천시 경계",
            style_function=lambda f: {"color": "yellow", "weight": 2, "fill": False},
            control=False
            # tooltip=folium.GeoJsonTooltip(fields=["EMD_KOR_NM"]),
        ).add_to(m)

        # 선택 읍면동 하이라이트
        def style_fn(feature):
            emd = feature["properties"].get("EMD_KOR_NM", "")
            is_selected = emd == selected
            return {
                "fillColor": "red" if is_selected else "transparent",
                "color": "black" if is_selected else "transparent",
                "weight": 4 if is_selected else 0,
                "fillOpacity": 0.5 if is_selected else 0,
            }

        selected_bounds = (
            gdf_boundary[gdf_boundary["EMD_KOR_NM"] == selected]
            .to_crs(4326)
            .geometry.values[0]
            .bounds
        )
        padding = 0.01
        m.fit_bounds(
            [
                [selected_bounds[1] - padding, selected_bounds[0] - padding],
                [selected_bounds[3] + padding, selected_bounds[2] + padding],
            ]
        )

        folium.GeoJson(
            geojson_data,
            name="선택 읍면동",
            style_function=style_fn,
            control=False,
            # #tooltip=folium.GeoJsonTooltip(
            #     fields=["EMD_KOR_NM"],
            #     sticky=False,
            #     permanent=True,
            #     direction="center",
            #     opacity=0.9,
            # ),
        ).add_to(m)

        legend_html = """
            {% macro html(this, kwargs) %}
            <div style="
                position: absolute;
                top: 10px; right: 10px;
                z-index: 9999;
                background-color: white;
                padding: 12px;
                border: 1px solid lightgray;
                border-radius: 8px;
                font-size: 14px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
            " class="leaflet-control leaflet-bar">
                <b>히트맵 인구 수</b><br>
                <i style="background:#d73027;width:18px;height:10px;display:inline-block;"></i> 매우 높음<br>
                <i style="background:#fdae61;width:18px;height:10px;display:inline-block;"></i> 높음<br>
                <i style="background:#ffffbf;width:18px;height:10px;display:inline-block;"></i> 중간<br>
                <i style="background:#a6d96a;width:18px;height:10px;display:inline-block;"></i> 낮음<br>
                <i style="background:#1a9850;width:18px;height:10px;display:inline-block;"></i> 매우 낮음
            </div>
            {% endmacro %}
        """


        # folium.LayerControl(collapsed=False).add_to(m)
        # 지도 크기 설정
        from branca.element import Template, MacroElement
        legend = MacroElement()
        legend._template = Template(legend_html)
        m.get_root().add_child(legend)
        m.get_root().html.add_child(
            
            folium.Element(
                f"""
                <style>
                    .folium-map {{
                        height: 100% !important;
                    }}
                    .map-title {{
                        position: absolute;
                        top: 18px; left: 50%;
                        transform: translateX(-50%);
                        z-index: 9999;
                        background: rgba(0,0,0,0.6);
                        color: gold;
                        padding: 12px 28px;
                        border-radius: 24px;
                        font-size: 2.1rem;
                        font-weight: bold;
                        letter-spacing: 2px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.22);
                        border: 2px solid #ffec8b;
                        pointer-events: none;
                    }}
                </style>
                <div class="map-title">{selected}</div>
                """
            )
        )

        BASE_DIR = os.path.dirname(__file__)
        save_path = os.path.join(BASE_DIR, "www", "updated_map.html")
        m.save(save_path)

        return ui.HTML("""
            <iframe 
                src='./updated_map.html' 
                width='100%' 
                height='100%' 
                style='border:none;'>
            </iframe>
        """)
    
    @output
    @render.ui
    def plot_summary():
        cols = [
            "읍면동명",
            "비상벨",
            "CCTV",
            "기저귀교환대",
            "장애인화장실",
            "어린이대변기",
        ]
        selected = input.emd()

        # 집계
        summary_df = yc_df[cols].copy()
        summary_df["총합"] = summary_df[cols[1:]].sum(axis=1)
        summary_df = (
            summary_df.groupby("읍면동명")[cols[1:] + ["총합"]].sum().astype(int)
        )

        # 총합 기준으로 정렬 후 순위 인덱스 부여
        summary_df_sorted = summary_df.sort_values(
            "총합", ascending=False
        ).reset_index()
        summary_df_sorted["__rank__"] = summary_df_sorted.index + 1  # 총합 기준 순위

        # 선택된 항목과 top5 추출
        top5 = summary_df_sorted.head(5)
        selected_row = summary_df_sorted[summary_df_sorted["읍면동명"] == selected]

        # 병합 후 중복 제거
        display_df = pd.concat([selected_row, top5]).drop_duplicates("읍면동명")

        # 선택된 항목을 맨 위로 정렬
        display_df["정렬키"] = display_df["읍면동명"].apply(
            lambda x: 0 if x == selected else 1
        )
        display_df = display_df.sort_values(["정렬키", "총합"], ascending=[True, False])



        # 하이라이트 함수 정의
        def _highlight(row):
            return (
                ["background-color: skyblue"] * len(row)
                if row["읍면동명"] == selected
                else ["" for _ in row]
            )

        html = (
            display_df.drop(columns=["정렬키", "__rank__"])
            .reset_index(drop=True)
            .style
            .hide(axis="index")  # ✅ index 숨기기
            .apply(_highlight, axis=1)
            .to_html()
        )
        return HTML(html)

    @output
    @render.ui
    def plot_rank():
        #  기본 데이터 집계
        city_counts = gb_df["시군구명"].value_counts().reset_index()
        city_counts.columns = ["시군구", "화장실 수"]
        city_counts = city_counts.sort_values("화장실 수", ascending=False)

        yc_rank = (city_counts["시군구"] == "영천시").idxmax() + 1
        yc_toilet_count = city_counts.loc[city_counts["시군구"] == "영천시", "화장실 수"].values[0]

        # 인구 병합
        gb_pop_fixed = gb_pop.rename(columns={"행정구역별(읍면동)": "시군구"})
        city_all = pd.merge(city_counts, gb_pop_fixed, on="시군구", how="left")
        city_all = city_all.rename(columns={"총인구 (명)": "총인구수"})

        # 2️ 트리맵
        color_map = {city: '#d3d3d3' for city in city_all["시군구"].unique()}
        color_map["영천시"] = '#ffa366'

        treemap_fig = px.treemap(
            city_all,
            path=["시군구"],
            values="화장실 수",
            color="시군구",
            color_discrete_map=color_map,
            hover_data={"총인구수": True, "화장실 수": True}
        )
        treemap_fig.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>화장실 수: %{value:,}개<br>인구수: %{customdata[0]:,}명<extra></extra>"
        )
        treemap_fig.update_layout(
            title=f"경북 전체 시군구별 공공화장실 수 트리맵<br><sup>영천시는 {yc_rank}위, 총 {yc_toilet_count:,}개 설치</sup>",
            margin=dict(t=60, l=20, r=20, b=20),
            height=600
        )

        # 3️ 테이블 (Top5 + 생략 + 영천시)
        top5 = city_counts.head(5)
        yc_row = city_counts[city_counts["시군구"] == "영천시"]
        ellipsis_row = pd.DataFrame([["...", None]], columns=["시군구", "화장실 수"])
        top_rows = pd.concat([top5, ellipsis_row, yc_row], ignore_index=True)

        top_rows = pd.merge(top_rows, gb_pop_fixed, on="시군구", how="left")
        top_rows = top_rows.rename(columns={"총인구 (명)": "총인구수"})

        display_df = top_rows[["시군구", "화장실 수", "총인구수"]].copy()
        display_df.columns = ["시군구", "화장실 수", "인구 수"]
        display_df.loc[display_df["시군구"] == "...", ["화장실 수", "인구 수"]] = "..."
        display_df["인구 수"] = display_df["인구 수"].apply(lambda x: f"{int(x):,}" if pd.notnull(x) and x != "..." else x)

        row_colors = []
        for city in display_df["시군구"]:
            if city == "영천시":
                row_colors.append('#ffe0cc')  # 강조
            elif city == "...":
                row_colors.append('#eeeeee')  # 생략
            else:
                row_colors.append('#f9f9f9')  # 일반

        table_fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(display_df.columns),
                fill_color='#1f3b70',
                font=dict(color='white', size=13, family='Arial'),
                align='center',
                height=32
            ),
            cells=dict(
                values=[display_df[col] for col in display_df.columns],
                fill_color=[row_colors],
                font=dict(color='black', size=12),
                align=['center', 'right', 'right'],
                height=28
            )
        )])
        table_fig.update_layout(
            title_text=f"영천시는 경북 공공화장실 수 {yc_rank}위 ({yc_toilet_count:,}개)",
            margin=dict(l=20, r=20, t=60, b=20),
            height=400
        )

        # 4️ 두 plotly 시각화를 HTML로 합치기
        treemap_html = treemap_fig.to_html(include_plotlyjs='cdn', full_html=False)
        table_html = table_fig.to_html(include_plotlyjs=False, full_html=False)

        return HTML(treemap_html + "<br><br>" + table_html)

    @output
    @render.ui
    def plot_vulnerable():
        import pandas as pd
        import plotly.graph_objects as go
        from htmltools import HTML

        # 데이터 로딩 및 전처리
        yc = pd.read_csv("./data/yc_df.csv", encoding="utf-8")
        replace_map = {"문외동27": "문외동", "양항리": "임고면", "치산리": "신녕면"}
        yc["읍면동명"] = yc["읍면동명"].replace(replace_map)

        # 화장실 수가 적은 상위 10개 읍면동 추출
        yc_2 = yc.groupby('읍면동명').size().reset_index(name='화장실수')
        yc_2 = yc_2.sort_values('화장실수', ascending=True)
        yc_22 = yc_2.head(10).reset_index(drop=True)

        # 옵션 합계 계산
        features = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
        yc_total = yc.groupby('읍면동명')[features].sum().reset_index()
        yc_total['총합'] = yc_total[features].sum(axis=1)

        # 병합 및 정렬
        yc_final = pd.merge(yc_22, yc_total, on='읍면동명', how='left')
        yc_sol = yc_final.sort_values(by=['화장실수', '총합'], ascending=[True, True]).reset_index(drop=True)

        # 등급 부여 (상위 7개는 매우 취약, 하위 3개는 취약)
        yc_sol = yc_sol.copy()
        yc_sol["등급"] = ["매우 취약"] * 7 + ["취약"] * 3

        # 색상 매핑
        등급색 = {
            "우수": "#d4f4dd",
            "보통": "#fff5cc",
            "취약": "#ffd9d9",
            "매우 취약": "#ff9999",
        }
        row_colors = [등급색.get(g, "#f0f0f0") for g in yc_sol["등급"]]

        # Plotly Table 시각화
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["읍면동", "화장실 수", "총 편의시설 수", "등급"],
                        fill_color="#7f0000",
                        font=dict(color="white", size=13),
                        align="center",
                        height=32,
                    ),
                    cells=dict(
                        values=[
                            yc_sol["읍면동명"],
                            yc_sol["화장실수"].astype(int),
                            yc_sol["총합"].astype(int),
                            yc_sol["등급"],
                        ],
                        fill_color=[row_colors],
                        font=dict(color="black", size=12),
                        align=["center", "right", "right", "center"],
                        height=28,
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="영천시 공공화장실 취약지역",
            margin=dict(l=20, r=20, t=60, b=20),
            height=460,
        )

        return HTML(fig.to_html(include_plotlyjs="cdn"))



    
    output.plot_opening_gb = render_widget(plot_opening_gb)
    output.plot_opening_yc = render_widget(plot_opening_yc)
    output.plot_weekend_gb = render_widget(plot_weekend_gb)
    output.plot_weekend_yc = render_widget(plot_weekend_yc)

    output.plot_total_count_ = render_widget(plot_total_count_)
    output.plot_per_10k = render_widget(plot_per_10k)
    output.plot_density = render_widget(plot_density)
    output.plot_growth_rate = render_widget(plot_growth_rate)
    output.plot_growth_comparison = render_widget(plot_growth_comparison)

    output.plot_opening_gb = render_widget(plot_opening_gb)
    output.plot_opening_yc = render_widget(plot_opening_yc)
    output.plot_weekend_gb = render_widget(plot_weekend_gb)
    output.plot_weekend_yc = render_widget(plot_weekend_yc)
    output.radar_install_compare = render_widget(radar_install_compare)
    output.bar_install_regions = render_widget(bar_install_regions)
    output.lactation_type_pie = render_widget(lactation_type_pie)
    output.plot_emergency_bell = render_widget(plot_emergency_bell)
    output.plot_cctv = render_widget(plot_cctv)
    output.plot_diaper = render_widget(plot_diaper)
    output.plot_child_fixture = render_widget(plot_child_fixture)
    output.infra_comparison = render_widget(infra_comparison)



app = App(app_ui, server, static_assets=STATIC_DIR)



