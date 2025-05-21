from shiny import App, reactive, render, ui
import pandas as pd
import plotly.express as px
from shinywidgets import render_widget, output_widget
import processing, plots
from plots import plot_open_type_pie, plot_weekend_pie
from htmltools import tags
import os
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

API_KEY = "42CA-2DDB-565B-5200-FD2F-F620-ADB3-718A"

df_lactation = processing.fetch_lactation_rooms(API_KEY)
df_long = processing.prepare_grouped_bar_data("./data/kb_df.csv", df_lactation)
lactation_type_df = processing.preprocess_lactation_type(API_KEY)
bell_df = processing.preprocess_emergency_bell(kb_df)
cctv_df = processing.preprocess_cctv(kb_df)
diaper_df = processing.preprocess_diaper(kb_df)
yeongcheon, gyeongbuk_avg = processing.preprocess_child_fixture_rates(kb_df)



 
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
            ui.nav_panel("1. 경북 vs 영천시",
            ui.layout_column_wrap(
                width="1/1",
                gap="16px"),

                # 🧭 Header Section
                ui.layout_columns(ㅔ
                    ui.card(
                        ui.h3("📊 영천시 공공화장실 인프라, 어디쯤인가요?"),
                        ui.p("경북 전체와 비교한 영천시의 공공화장실 규모와 접근성은 평균 이하입니다."),
                        class_="bg-sky-100 text-sky-900 p-4 rounded-xl shadow-md"
                    ),
                    ui.card(
                        ui.layout_columns(
                            ui.value_box("🚻 총 화장실 수", "92개"),
                            ui.value_box("👥 인구 1만명당 수", "1.14개"),
                            ui.value_box("📐 ㎢당 밀도", "0.33개"),
                        ),
                        class_="bg-white p-4 rounded-2xl shadow-md"
                    ),
                    col_widths=(4, 8)
                ),

                # 📊 SECTION 1: 절대 수 + 인구당 수
                ui.layout_columns(
                    ui.card(
                        ui.h4("① 시군구별 전체 화장실 수"),
                        output_widget("plot_total_count_"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.h4("② 인구 1만명당 화장실 수"),
                        output_widget("plot_per_10k"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.h4("③ 면적당 화장실 수 (개/㎢)"),
                        output_widget("plot_density"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                ),

                # 📐 SECTION 2: 증가율
                ui.layout_columns(
                    ui.card(
                        ui.h4("④ 화장실 설치 증가 추이 (2015~2023)"),
                        output_widget("plot_growth_comparison"),
                        class_="shadow-md p-3 rounded-xl"
                    )
                ),

                # 🕓 SECTION 3: 개방시간 비교
                ui.layout_columns(
                    ui.card(
                        ui.h4("⑤ 경북 전체 개방시간 유형 분포"),
                        output_widget("plot_opening_gb"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.h4("⑥ 영천 개방시간 유형 분포"),
                        output_widget("plot_opening_yc"),
                        class_="shadow-md p-3 rounded-xl"
                    )
                ),

                # 🚻 SECTION 4: 주말 개방 여부
                ui.layout_columns(
                    ui.card(
                        ui.h4("⑦ 경북 주말 개방 여부"),
                        output_widget("plot_weekend_gb"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.h4("⑧ 영천 주말 개방 여부"),
                        output_widget("plot_weekend_yc"),
                        class_="shadow-md p-3 rounded-xl"
                    )
                )
            ),
                ui.nav_panel("2. 여성·가족 인프라 분석",
                    ui.layout_column_wrap(
                        width="1/1",
                        gap="20px"),

                        # ✅ 1행: 강조 텍스트 카드
                        ui.card(
                            ui.h3("👶 출산율 1위 영천시, 인프라도 함께 1위일까?"),
                            ui.p("수유실, CCTV, 비상벨, 어린이 대변기, 기저귀 교환대 등 여성·가족 친화 인프라를 시각화로 분석합니다."),
                            class_="bg-amber-100 text-gray-900 p-4 rounded-xl shadow-md"
                        ),

                        # ✅ 2행: KPI 박스 (3열)
                        ui.layout_columns(
                            ui.value_box("🍼 수유실 수 (영천)", "23개"),
                            ui.value_box("🎥 CCTV 설치율", "82%"),
                            ui.value_box("🚼 어린이 화장실 설치율", "34%"),
                            col_widths=(4, 4, 4)
                        ),

                        # ✅ 3행: Radar Chart + Grouped Bar Chart (2열)
                        ui.layout_columns(
                            ui.card(
                                ui.h4("① 영천시 vs 경북 평균: 편의시설 설치율"),
                                output_widget("radar_install_compare"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            ui.card(
                                ui.h4("② 시군구별 5대 항목 설치율"),
                                output_widget("bar_install_regions"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            col_widths=(6, 6)
                        ),

                        # ✅ 4행: 항목별 설치율 Top5 (3열)
                        ui.layout_columns(
                            ui.card(
                                ui.h4("③ CCTV 설치율 Top 5"),
                                output_widget("plot_cctv"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            ui.card(
                                ui.h4("④ 비상벨 설치율 Top 5"),
                                output_widget("plot_emergency_bell"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            ui.card(
                                ui.h4("⑤ 기저귀 교환대 설치율 Top 5"),
                                output_widget("plot_diaper"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            col_widths=(4, 4, 4)
                        ),

                        # ✅ 5행: Pie Charts (2열)
                        ui.layout_columns(
                            ui.card(
                                ui.h4("⑥ 수유실 유형 분포"),
                                output_widget("lactation_type_pie"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            ui.card(
                                ui.h4("⑦ 어린이 대변기 설치 여부"),
                                output_widget("plot_child_fixture"),
                                class_="shadow-md p-3 rounded-xl"
                            ),
                            col_widths=(6, 6)
                        ),
                    )
            )
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



app = App(app_ui, server, static_assets=STATIC_DIR)


