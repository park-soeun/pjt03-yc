# app.py
from shiny import App, reactive, render, ui
import pandas as pd
import plotly.express as px
from shinywidgets import render_widget, output_widget
import processing, plots
from plots import plot_open_type_pie, plot_weekend_pie
from pathlib import Path  # ✅ 경로 모듈



# ✅ [1] 경로 정리
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

kb_path = DATA_DIR / "kb_df.csv"
yc_path = DATA_DIR / "yc_df.csv"
pop_path = DATA_DIR / "pop_2023.csv"     
area_path = DATA_DIR / "area_2023.csv" 

# ✅ [2] 전처리된 CSV 불러오기
kb_df = pd.read_csv(kb_path)
yc_df = pd.read_csv(yc_path)


# ✅ 경로를 함수에 전달
kb_df = processing.load_toilet_data(kb_path)
pop_df = processing.load_population_data(pop_path)  # ← 오류 원인 해결됨!
area_df = processing.load_area_data(area_path)

# ✅ [3] 전처리 함수 호출
df_plot = processing.get_toilet_count_by_region(kb_df)
df_per_10k = processing.get_toilet_per_10k(kb_df, pop_df)
df_density = processing.get_toilet_density(kb_df, area_df)
df_growth = processing.get_toilet_growth_trend(kb_df)
yearly_df = processing.get_toilet_growth_trend(kb_df)
combined_top_bottom_yc = processing.get_combined_growth_comparison(kb_df)

# ✅ [4] 개방 시간 데이터 불러오기 (전처리버전)
kb_df, yc_df = processing.load_processed_opening_data(kb_path, yc_path)

# ✅ [5] 개방시간 분류 함수
def classify_open_type(row):
    기본 = str(row['개방시간']) if pd.notna(row['개방시간']) else ''
    상세 = str(row['개방시간상세']) if pd.notna(row['개방시간상세']) else ''
    combined = (기본 + ' ' + 상세).lower().replace(' ', '').replace('~', '-')

    if any(kw in combined for kw in ['24', '00:00-24:00', '상시', '연중무휴']):
        return '24시간'
    elif any(kw in combined for kw in ['09','06','07','08','10','11','12','13','14','15','16','17','18','19','20','21','22','23','정시','근무시간','영업시간']):
        return '주간개방'
    elif any(kw in combined for kw in ['행사','경기','개장시','필요시','학생','동절기','이용중단','야영장']):
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

# ✅ [6] 여성·가족 인프라용 추가 전처리


API_KEY = "42CA-2DDB-565B-5200-FD2F-F620-ADB3-718A"
df_lactation = processing.fetch_lactation_rooms(API_KEY)
df_long = processing.prepare_grouped_bar_data(kb_path, df_lactation)
lactation_type_df = processing.preprocess_lactation_type(API_KEY)
bell_df = processing.preprocess_emergency_bell(kb_df)
cctv_df = processing.preprocess_cctv(kb_df)
diaper_df = processing.preprocess_diaper(kb_df)
yeongcheon, gyeongbuk_avg = processing.preprocess_child_fixture_rates(kb_df)
yeongcheon_rates, gyeongbuk_rates = processing.prepare_radar_data(kb_path, API_KEY)

# ✅ [7] UI 구성
app_ui = ui.page_navbar(
    ui.nav_panel("1. 경북 vs 영천시",
        ui.layout_column_wrap(width="1/1", gap="16px"),
        ui.layout_columns(
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
        ui.layout_columns(
            ui.card("① 시군구별 전체 화장실 수", output_widget("plot_total_count_")),
            ui.card("② 인구 1만명당 화장실 수", output_widget("plot_per_10k")),
            ui.card("③ 면적당 화장실 수", output_widget("plot_density")),
        ),
        ui.layout_columns(
            ui.card("④ 화장실 설치 증가 추이", output_widget("plot_growth_comparison"))
        ),
        ui.layout_columns(
            ui.card("⑤ 경북 개방시간 분포", output_widget("plot_opening_gb")),
            ui.card("⑥ 영천 개방시간 분포", output_widget("plot_opening_yc"))
        ),
        ui.layout_columns(
            ui.card("⑦ 경북 주말 개방 여부", output_widget("plot_weekend_gb")),
            ui.card("⑧ 영천 주말 개방 여부", output_widget("plot_weekend_yc"))
        )
    ),
    ui.nav_panel("2. 여성·가족 인프라 분석",
        ui.layout_column_wrap(width="1/1", gap="20px"),
        ui.card(
            ui.h3("👶 출산율 1위 영천시, 인프라도 함께 1위일까?"),
            ui.p("수유실, CCTV, 비상벨, 어린이 대변기, 기저귀 교환대 등 여성·가족 친화 인프라를 시각화로 분석합니다."),
            class_="bg-amber-100 text-gray-900 p-4 rounded-xl shadow-md"
        ),
        ui.layout_columns(
            ui.value_box("🍼 수유실 수 (영천)", "23개"),
            ui.value_box("🎥 CCTV 설치율", "82%"),
            ui.value_box("🚼 어린이 화장실 설치율", "34%"),
        ),
        ui.layout_columns(
            ui.card("① 영천시 vs 경북 평균", output_widget("radar_install_compare")),
            ui.card("② 시군구별 항목 설치율", output_widget("bar_install_regions")),
        ),
        ui.layout_columns(
            ui.card("③ CCTV 설치율 Top5", output_widget("plot_cctv")),
            ui.card("④ 비상벨 설치율 Top5", output_widget("plot_emergency_bell")),
            ui.card("⑤ 기저귀 교환대 설치율 Top5", output_widget("plot_diaper")),
        ),
        ui.layout_columns(
            ui.card("⑥ 수유실 유형 분포", output_widget("lactation_type_pie")),
            ui.card("⑦ 어린이 대변기 설치 여부", output_widget("plot_child_fixture")),
        ),
        ui.card("⑧ 수유실 위치 및 CCTV 지도", output_widget("map_lactation_cctv")),
        ui.card(
            ui.h4("🔎 인프라 미설치 지역 요약"),
            ui.p("❗ 아직도 영천시 내 ○○동, △△면에는 기저귀 교환대 설치 화장실이 없습니다."),
            ui.p("❗ 어린이 대변기 설치율은 경북 평균의 60% 수준에 그칩니다."),
            ui.p("❗ CCTV 미설치 화장실이 21곳 존재합니다."),
            class_="bg-red-50 text-red-900 p-4 rounded-xl"
        )
    )
)

# ✅ [8] 서버
def server(input, output, session):
    output.plot_total_count_ = render_widget(lambda: plots.plot_total_count(df_plot))
    output.plot_per_10k = render_widget(lambda: plots.plot_per_10k(df_per_10k))
    output.plot_density = render_widget(lambda: plots.plot_density(df_density))
    output.plot_growth_comparison = render_widget(lambda: plots.plot_growth_comparison(combined_top_bottom_yc))

    output.plot_opening_gb = render_widget(lambda: plot_open_type_pie(kb_df, "경북 전체"))
    output.plot_opening_yc = render_widget(lambda: plot_open_type_pie(yc_df, "영천시"))

    output.plot_weekend_gb = render_widget(lambda: plot_weekend_pie(kb_df, "경북 전체"))
    output.plot_weekend_yc = render_widget(lambda: plot_weekend_pie(yc_df, "영천시"))

    output.radar_install_compare = render_widget(lambda: plots.plot_radar_install_compare(yeongcheon_rates, gyeongbuk_rates))
    output.bar_install_regions = render_widget(lambda: plots.plot_grouped_bar(df_long))
    output.lactation_type_pie = render_widget(lambda: plots.plot_lactation_type_pie(lactation_type_df))
    output.plot_emergency_bell = render_widget(lambda: plots.plot_emergency_bell(bell_df))
    output.plot_cctv = render_widget(lambda: plots.plot_cctv(cctv_df))
    output.plot_diaper = render_widget(lambda: plots.plot_diaper(diaper_df))
    output.plot_child_fixture = render_widget(lambda: plots.plot_child_fixture_radar(yeongcheon, gyeongbuk_avg))

# ✅ 실행
app = App(app_ui, server)
