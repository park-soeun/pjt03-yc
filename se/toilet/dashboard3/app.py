from shiny import App, reactive, render, ui
import pandas as pd
import plotly.express as px
from shinywidgets import render_widget, output_widget
import processing, plots
from plots import plot_open_type_pie, plot_weekend_pie




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
    ui.layout_columns(
        output_widget("plot_opening_gb"),
        output_widget("plot_opening_yc"),
    ),
    ui.layout_columns(
        output_widget("plot_weekend_gb"),
        output_widget("plot_weekend_yc"),
    )
)


app_ui = ui.page_navbar(
            ui.nav_panel("1. 경북 vs 영천시",
            ui.layout_column_wrap(
                width="1/1",
                gap="16px"),

                # 🧭 Header Section
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
                    col_widths=(8, 4)
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
                        ui.h4("④-1 화장실 설치 증가 추이 (2015~2023)"),
                        output_widget("plot_growth_rate"),
                        class_="shadow-md p-3 rounded-xl"
                    ),
                    ui.card(
                        ui.h4("④-2 화장실 설치 증가 추이 (2015~2023)"),
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



app = App(app_ui, server)  # 또는 server 빠짐


