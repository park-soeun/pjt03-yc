```python
# =========================
# 📦 Import Modules
# =========================

import os
import functools
from shinywidgets import output_widget
from shiny import reactive, render
from shinywidgets import render_widget
import  json
import geopandas as gpd

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from shiny import App as ShinyApp, ui, render
from shinywidgets import render_widget, output_widget
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================
# 📦 Import Modules - 중복 제거 및 최적화
# =========================

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from shiny import App as ShinyApp, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import functools


# =========================
# 🚀 FastAPI Initialization
# =========================

main_api = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_api.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@main_api.get("/")
def redirect_to_dashboard():
    return RedirectResponse(url="/shiny")



# =========================
# 📁 데이터 관련 함수 - 캐싱 및 오류 처리 개선
# =========================



# CSV 로딩 (인코딩 문제 해결 포함)
farm_df = pd.read_csv("ycdata/farm_map.csv", encoding="utf-8-sig")

# 컬럼명 공백 제거
farm_df.columns = farm_df.columns.str.strip()

# 이제 '주소' 컬럼을 정상적으로 참조할 수 있음
farm_df["읍면동"] = farm_df["주소"].str.extract(r"영천시\s(\S+)")

# 면적 평으로 변환 (1㎡ = 0.3025평)
farm_df["면적(평)"] = (farm_df["면적(제곱미터)"] * 0.3025).round(1)

# 기술센터 데이터 - 상수로 한 번만 정의
TECH_CENTER_DATA = pd.DataFrame({
    "분류": [
        "농업인 상담소"] * 12 + ["농산물 산지 유통센터"] * 11 + ["농기계 임대 사업소"] * 5,
    "기관": [
        "농촌인력 지원센터 (중앙)", "금호 농민상담소", "대창 농민상담소", "청통 농민상담소",
        "신녕 농민상담소", "화산 농민상담소", "화남 농민상담소", "화북 농민상담소",
        "자양 농민상담소", "임고 농민상담소", "고경 농민상담소", "북안 농민상담소",
        "과미유통영농조합법인", "청우영농조합법인", "동산영농조합법인", "삼진영농조합법인",
        "영천친환경농업영농조합법인", "천지유통영농조합법인", "화성영농조합법인", "영천유기촌영농조합법인",
        "영천화남농협", "대구경북능금농협", "금호농협",
        "임대사업본소 (서부본소)", "남부분소", "동부분소", "북부분소", "중부분소"
    ],
    "근무 요일": [
        "월·수·금", "월·수·금", "화·목", "화·목", "월·수·금", "월·수·금", "화·목", "월·수·금",
        "화·목", "월~금", "월·수·금", "화·목"
    ] + ["-"] * 16,
    "주소": [
        "경상북도 영천시 역전로 12", "경상북도 영천시 금호로 190-12", "경상북도 영천시 금박로 1033",
        "경상북도 영천시 원촌리 516-82", "경상북도 영천시 화성중앙길 30", "경상북도 영천시 연지길 16",
        "경상북도 영천시 삼창리 1023-2", "경상북도 영천시 자천6길 17", "경상북도 영천시 포은로 1631",
        "경상북도 영천시 포은로 491", "경상북도 영천시 호국로 1059", "경상북도 영천시 운북로 2006-3",
        "경상북도 영천시 임고면 평천리 355-10", "경상북도 영천시 청통면 청통초등길 8번지",
        "경상북도 영천시 금호읍 거여로 140", "경상북도 영천시 신녕면 관기길 222",
        "경상북도 영천시 화남면 신선로 10-17", "경상북도 영천시 금호읍 가라골1길 72-4",
        "경상북도 영천시 임고면 덕연길 36", "경상북도 영천시 청통면 청통로 127번지",
        "경상북도 영천시 화남면 천문로 1587", "경상북도 영천시 화남면 천문로 1669",
        "경상북도 영천시 금호읍 금창로 74",
        "경북 영천시 청통면 호당1길 66-17", "경북 영천시 대창면 금박로 1033",
        "경북 영천시 고경면 호국로 386-5", "경북 영천시 화북면 천문로 2150", "경북 영천시 한방로 272"
    ],
    "전화번호": [
        "054-339-7368", "054-334-0274", "054-335-4072", "054-335-7901",
        "054-332-0901", "054-335-5901", "054-337-6969", "054-337-2743",
        "054-336-2751", "054-335-1165", "054-336-1901", "054-333-6834",
        "054-338-5390", "054-336-1414", "054-334-0022", "확인 불가",
        "054-337-6202", "확인 불가", "확인 불가", "054-332-5825",
        "054-337-9201", "확인 불가", "054-337-2231",
        "054-339-7228", "054-339-7722", "054-339-7373", "054-339-7602", "054-339-7591"
    ],
    "비고": [
        "-"] * 12 + 
        ["취급 품목 : 포도", "취급 품목 : 저장양파", "취급 품목 : 사과", "취급 품목 : 저장양파",
         "취급 품목 : 사과", "취급 품목 : 복숭아", "취급 품목 : 감자", "취급 품목 : 마늘",
         "취급 품목 : 포도", "취급 품목 : 사과", "취급 품목 : 복숭아"] +
        ["보유농기계 : 72종 532대", "보유농기계 : 18종 104대", "보유농기계 : 28종 188대",
         "보유농기계 : 25종 167대", "보유농기계 : 22종 129대"]
})


# 데이터 로드 함수 - 메모리 효율성 및 오류 처리 개선
@functools.lru_cache(maxsize=10)  # 캐싱 적용
def load_and_prepare(path, col_name):
    """데이터 파일을 로드하고 전처리하는 함수 (캐싱 적용)"""
    try:
        df = pd.read_csv(path, encoding="cp949", usecols=["일시", col_name], dtype={col_name: str})
        df.columns = df.columns.str.strip()
        df["일시"] = pd.to_datetime(df["일시"], format="%b-%y", errors="coerce")
        df["연도"] = df["일시"].dt.year
        df["월"] = df["일시"].dt.month
        df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
        return df[["일시", "연도", "월", col_name]]
    except Exception as e:
        print(f"파일 로드 에러 ({path}): {e}")
        # 샘플 데이터 반환 (파일이 없을 경우)
        dates = pd.date_range(start='2015-01-01', end='2025-12-31', freq='MS')
        sample_df = pd.DataFrame({
            '일시': dates,
            '연도': dates.year,
            '월': dates.month,
            col_name: np.random.normal(10, 5, len(dates))
        })
        return sample_df[["일시", "연도", "월", col_name]]

# 가상 데이터 생성 함수 - 한 번만 호출하도록 개선
@functools.lru_cache(maxsize=1)
def generate_crop_data():
    """작물 데이터 생성 (캐싱 적용)"""
    crops = ["포도", "복숭아", "마늘", "사과", "배"]
    data = {
        "작물": crops,
        "생산량(톤)": [12000, 8500, 15000, 7000, 5000],
        "전국순위": [1, 3, 1, 5, 7],
        "수익성": [85, 80, 75, 70, 65]
    }
    return pd.DataFrame(data)

@functools.lru_cache(maxsize=1)
def generate_population_data():
    """인구 데이터 생성 (캐싱 적용)"""
    years = list(range(2019, 2025))
    data = {
        "연도": years,
        "총인구": [100000, 98500, 97000, 96500, 95800, 95000],
        "귀농인구": [500, 620, 750, 890, 1050, 1200]
    }
    return pd.DataFrame(data)

@functools.lru_cache(maxsize=1)
def generate_farm_data():
    """농지 데이터 생성 (캐싱 적용)"""
    data = {
        "id": list(range(1, 11)),
        "유형": ["농지", "주거", "농지", "농지", "주거", "주거", "농지", "농지", "주거", "농지"],
        "위치": ["영천시 임고면", "영천시 금호읍", "영천시 고경면", "영천시 화산면", "영천시 신녕면", 
                "영천시 중앙동", "영천시 북안면", "영천시 자양면", "영천시 동부동", "영천시 청통면"],
        "면적(평)": [1500, 25, 2000, 1200, 30, 22, 1800, 900, 28, 1600],
        "가격(만원)": [45000, 15000, 60000, 35000, 18000, 12000, 50000, 28000, 16000, 48000],
        "위도": [35.9875, 35.9654, 36.0123, 35.9987, 36.0254, 35.9732, 36.0345, 35.9876, 35.9732, 36.0087],
        "경도": [128.9342, 128.9123, 128.8765, 128.9454, 128.8932, 128.9267, 128.8876, 128.9023, 128.9345, 128.8765]
    }
    return pd.DataFrame(data)

# 기후 데이터 통합 로드 함수 - 성능 개선
@functools.lru_cache(maxsize=1)
def load_climate_data():
    """모든 기후 데이터를 한 번에 로드하고 병합 (캐싱 적용)"""
    try:
        # 필요한 컬럼만 로드
        temperature = load_and_prepare("ycdata/yc_temp_2015_2025.csv", "평균기온(℃)")
        rain = load_and_prepare("ycdata/yc_rain_2015_2025.csv", "강수량(mm)")
        humidity = load_and_prepare("ycdata/yc_hum_2015_2025.csv", "평균습도(%rh)")
        solar = load_and_prepare("ycdata/yc_solar_2015_2025.csv", "일사합(MJ/m2)")
        sunshine = load_and_prepare("ycdata/yc_solar_2015_2025.csv", "일조합(hr)")
        wind = load_and_prepare("ycdata/yc_wind_2015_2025.csv", "평균풍속(m/s)")

        # 효율적인 병합 (merge 대신 join 사용)
        climate_df = temperature.set_index(["일시", "연도", "월"])
        for df, col in [(rain, "강수량(mm)"), (humidity, "평균습도(%rh)"), 
                        (solar, "일사합(MJ/m2)"), (sunshine, "일조합(hr)"), 
                        (wind, "평균풍속(m/s)")]:
            climate_df = climate_df.join(df.set_index(["일시", "연도", "월"]))
        
        climate_df = climate_df.reset_index()
        print(f"기후 데이터 로드 성공: {len(climate_df)}행")
        return climate_df
    except Exception as e:
        print(f"기후 데이터 로드 실패: {e}")
        # 대체 데이터 생성
        dates = pd.date_range(start='2015-01-01', end='2025-12-31', freq='MS')
        return pd.DataFrame({
            '일시': dates,
            '연도': dates.year,
            '월': dates.month,
            '평균기온(℃)': np.random.normal(15, 8, len(dates)),
            '강수량(mm)': np.random.gamma(2, 50, len(dates)),
            '평균습도(%rh)': np.random.normal(60, 10, len(dates)),
            '일사합(MJ/m2)': np.random.gamma(3, 5, len(dates)),
            '일조합(hr)': np.random.gamma(2, 3, len(dates)),
            '평균풍속(m/s)': np.random.normal(2, 0.5, len(dates))
        })

# 데이터 미리 로드하기 (앱 시작 시 한 번만 실행)
crop_data = generate_crop_data()
population_data = generate_population_data()
farm_data = generate_farm_data()

# =========================
# 🎨 UI Definition
# =========================


CSS_STYLES = """
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang&family=Nanum+Pen+Script&family=NanumSquareNeo:wght@700&display=swap');

    body {
        font-family: 'NanumSquareNeo', 'Gowun Batang', sans-serif;
        background-color: #f4fbe6;
        color: #3e4e3e;
        letter-spacing: 0.3px;
    }

    h1, h2, h3, .card-header {
        font-family: 'NanumSquareNeo', sans-serif;
        font-weight: 700;
        color: #2e7d32;
    }

    .banner-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    }

    .title-center-text {
        text-align: center;
        max-width: 60%;
    }

    .banner-img {
        width: 80px;
        height: auto;
        border-radius: 8px;
    }


    .chat-bot {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background: #ecf9ec;
        padding: 16px 20px;
        border-radius: 16px;
        border-left: 6px solid #81c784;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .chat-bot:hover {
        transform: translateY(-2px);
        background: #f4fbf0;
    }

    .chat-bot-icon {
        font-size: 2em;
        color: #66bb6a;
    }

    .chat-bot-message {
        font-size: 1em;
        font-family: 'NanumSquareNeo', sans-serif;
        color: #2e7d32;
        line-height: 1.6;
    }

    .title-banner {
        background: linear-gradient(to right, #d0f5b1, #a5d6a7);
        color: #1b5e20;
        padding: 40px 25px;
        margin-bottom: 30px;
        border-radius: 16px;
        text-align: center;
        font-size: 2em;
        font-weight: bold;
        letter-spacing: 1.2px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }

    .sidebar {
        background-color: #ecf9ec;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #c5e1a5;
    }

    .card {
        background-color: #ffffff;
        border: 2px solid #c5e1a5;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 2px 6px rgba(76, 175, 80, 0.1);
        transition: all 0.3s ease-in-out;
    }

    .card:hover {
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.25);
        transform: translateY(-2px);
    }

    .card-header {
        background-color: #e6f4d9;
        color: #33691e;
        padding: 12px 20px;
        font-size: 1.2em;
        border-bottom: 2px solid #aed581;
        border-radius: 16px 16px 0 0;
    }

    .nav-tabs .nav-link.active {
        font-weight: bold;
        background-color: #f1f8e9;
        border-bottom: 3px solid #66bb6a;
        color: #2e7d32;
    }

    .custom-tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        color: #558b2f;
    }

    .custom-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 120%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #f0f4c3;
        color: #33691e;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85em;
        white-space: nowrap;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }

    .lead {
        font-family: 'Nanum Pen Script', cursive;
        font-size: 1.3em;
        color: #4e704e;
    }

    button, .btn {
        font-family: 'NanumSquareNeo', sans-serif;
        background-color: #a5d6a7;
        color: #1b5e20;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        border-radius: 12px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    button:hover, .btn:hover {
        background-color: #81c784;
    }
"""



# UI 정의 - 모듈화 및 가독성 향상
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"),
        ui.tags.style(CSS_STYLES)
    ),
    
    ui.tags.div(
        {"class": "title-banner"},
        ui.tags.div(
            {"class": "banner-content"},
            ui.tags.img(src="/static/left_farm.png", class_="banner-img"),
            ui.tags.div(
                {"class": "title-center-text"},
                ui.h1("영천 귀농 관측일지: 별이 머무는 땅 씨앗을 심다.", class_="mb-0"),
                ui.p("시민을 행복하게 영천을 위대하게!", class_="lead mb-0")
            ),
            ui.tags.img(src="/static/right_star.png", class_="banner-img")
        )
    ),

    ui.navset_tab(
        # 메인 페이지 탭
        ui.nav_panel("🏠 TAB.1 : Main Page",
            ui.tags.div(
                ui.tags.div({"class": "chat-bot"},
                ui.tags.span("🤖", {"class": "chat-bot-icon"}),
                ui.tags.div({"class": "chat-bot-message"},
                           "별이 머무는 영천에서 귀농을 시작해볼까요? 통계부터 먼저 살펴보시죠!"
                    )
                ),
                {"class": "container"},
                ui.h2("📘 영천 귀농 대시보드 소개"),
                ui.card(
                            ui.card_header("🌌 영천 귀농 관측일지"),
                            ui.markdown("""
                    > **"별이 머무는 땅, 씨앗을 심다."**
                    ✨ **영천은 별빛과 과수의 고장**입니다.  
                    이 대시보드는 귀농인과 예비 농업인을 위한 **종합 안내판**입니다.
                    ---
                    ### 🧭 이 대시보드에서 할 수 있는 일
                    - 🗺️ **팜맵 탐험**: 농지와 주거지 위치 시각화  
                    - 🌡️ **기후 통계 분석**: 작물별 재배 적합성 확인  
                    - 🧑‍🌾 **상담소·센터 정보 확인**: 시설 분류별 필터 지원  
                    - 📈 **귀농 인구 변화 관찰**: 연도별 통계 제공
                    ---
                    💡 **데이터로 땅을 읽고, 별을 보며 농사를 꿈꿔보세요.**
                    """)
                ),
                ui.h2("🎯 한눈에 보는 영천시 주요 통계"),
                ui.tags.div({"class": "row", "style": "margin-bottom: 20px;"}, 
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("👨‍👩‍👧‍👦 인구"),
                            ui.tags.h3("99,638명", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("🏠 가구 수"),
                            ui.tags.h3("54,431가구", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("➡️ 인구 이동(전입)"),
                            ui.tags.h3("11,666명", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("👩‍🌾 농가 인구"),
                            ui.tags.h3("8,065가구", {"class": "text-center"})
                        )
                    )
                ),
                ui.tags.div({"class": "row", "style": "margin-bottom: 20px;"}, 
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("🚜 농업기계 보유"),
                            ui.tags.h3("26,354개", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("🔁 사업체수"),
                            ui.tags.h3("14,217개", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("🏘 주택보급률"),
                            ui.tags.h3("105.3%", {"class": "text-center"})
                        )
                    ),
                    ui.tags.div({"class": "col-md-3"},
                        ui.card(
                            ui.card_header("🧱 토지 거래"),
                            ui.tags.h3("9,199필지", {"class": "text-center"})
                        )
                    ),
                    ui.p("출처 : 영천시의 50대 통계")
                ),

                ui.tags.hr(),
                ui.h2("👥 영천시 인구 분포포"),
                ui.tags.div({"class": "row"},
                    # 왼쪽 카드: 읍면동별 인구 현황
                    ui.tags.div({"class": "col-md-6"},
                        ui.card(
                            ui.card_header("영천시 읍면동별 인구 현황(2024년)"),
                            output_widget("population_map")
                        )
                    ),
                    # 오른쪽 카드: 연령대 - 성별 인구 피라미드
                    ui.tags.div({"class": "col-md-6"},
                        ui.card(
                            ui.card_header("연령대 - 성별 인구 피라미드"),
                            output_widget("age_distribution_plot")
                        )
                    )
                )
            )
        ),
        
        # 팜맵 탭
        ui.nav_panel("🗺️ TAB.2 : 팜맵",
            ui.tags.div({"class": "chat-bot"},
            ui.tags.span("🤖", {"class": "chat-bot-icon"}),
            ui.tags.div({"class": "chat-bot-message"},
                "안녕하세요! 👩‍🌾 이 탭에서는 영천시의 농지 정보를 지도와 함께 확인할 수 있어요.\n",
                "작물별 면적 분포도 차트로 시각화됩니다!"
                )
            ),
            ui.h2("🏡 농지 지도 시각화"),
            ui.tags.div(
                {"class": "row"},
                ui.tags.div(
                    {"class": "col-md-3"},
                    ui.h3("📈 작물별 면적 분포"),
                    ui.input_select(
                        "filter_eupmyeon_dropdown", "📍 읍면동 선택 (단일 선택)", 
                        choices=["전체"] + sorted(farm_df["읍면동"].dropna().unique().tolist()),
                        selected="전체"
                    ),
                    ui.h5("지역 작물 면적 분포"),
                    output_widget("crop_pie_chart")
                ),
                ui.tags.div(
                    {"class": "col-md-9"},
                    ui.card(
                        ui.card_header("🗺️ 영천시 팜맵"),
                        ui.tags.iframe(src="/static/farm_map.html", width="100%", height="500px", style="border:none;")
                    )
                )
            ),
            ui.tags.hr(),
            ui.card(
                ui.card_header("📋 영천시 팜맵 목록"),
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.input_selectize(
                            "filter_eupmyeon", "📍 읍면동 선택 (다중 선택 가능)",
                            choices=sorted(farm_df["읍면동"].dropna().unique().tolist()),
                            multiple=True,
                            options={"placeholder": "읍면동을 선택하세요"}
                        ),
                        ui.input_selectize(
                            "filter_crop", "🌱 재배작물 선택 (다중 선택 가능)",
                            choices=sorted(farm_df["재배작물"].dropna().unique().tolist()),
                            multiple=True,
                            options={"placeholder": "재배작물을 선택하세요"}
                        ),
                        ui.input_action_button("download_csv", "CSV로 저장하기 💾"),
                        ui.p("드롭다운에서 다중 선택이 가능합니다.", class_="text-muted small")
                    ),
                    ui.output_ui("paginated_table_ui")  # 페이지별 테이블을 담는 컨테이너
                )
            )
        ),
        
        # 기후 정보 탭
        ui.nav_panel("🌡 TAB.3 : 기후 정보",
            ui.tags.div({"class": "chat-bot"},
            ui.tags.span("🤖", {"class": "chat-bot-icon"}),
            ui.tags.div({"class": "chat-bot-message"},
                        "연도별로 기온, 습도, 강수량을 살펴보고 재배 작물도 추천드려요!"
            )
            ),
            ui.h2("📈 영천 연중 기후 통계 및 예측"),
            # 상단 컨트롤 박스
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h4("🎛️ 데이터 필터링"),
                    ui.input_slider("year_range", "연도 범위", min=2015, max=2025, value=[2015, 2025]),
                    ui.input_select("indicator", "기후 지표 선택", {
                        "평균기온(℃)": "평균기온(℃)",
                        "강수량(mm)": "강수량(mm)",
                        "평균습도(%rh)": "평균습도(%rh)",
                        "일조합(hr)": "일조합(hr)",
                        "평균풍속(m/s)": "평균풍속(m/s)"
                    }),
                    ui.input_radio_buttons("agg_type", "집계 방식", 
                                        choices=["월별", "연도별"], 
                                        selected="월별"),
                    ui.p("데이터 출처: 기상청 전국 기후 통계", class_="text-muted small")
                ),
                
                ui.tags.div(
                    {"class": "row mt-4"},
                    ui.tags.div(
                        {"class": "col-md-12"},
                        ui.card(
                            ui.card_header("📊 선택한 기후 지표의 추이"),
                            # 메인 컨텐츠
                            output_widget("climate_widget_plot")
                        )
                    )
                ),
                
                ui.tags.hr(),

                ui.card(
                    ui.card_header("📆 주요 작물별 재배 적합 기후"),
                    ui.markdown("""
                    | 작물 | 적정 기온 | 적정 강수량 | 생육 특성 |
                    |---|---|---|---|
                    | 🍇 포도 | 15~18℃ | 800~900mm | 고온 다습한 기후에서 당도 높음 |
                    | 🍑 복숭아 | 12~16℃ | 600~800mm | 서리 피해에 취약함 |
                    | 🧄 마늘 | 8~15℃ | 400~600mm | 저온 단일 조건에서 생육 촉진 |
                    | 🍎 사과 | 10~15℃ | 700~900mm | 일교차가 클수록 착색 우수 |
                    | 🍐 배 | 12~16℃ | 800~1000mm | 봄철 저온에 약함 |
                    
                    > 영천 지역은 일교차가 크고 일조량이 풍부하여 과수 재배에 적합합니다.
                    """)
                )
            )
        ),
        
        # 농업기술센터 탭
        ui.nav_panel("🧑‍🌾 TAB.4 : 농업기술센터",
            ui.tags.div({"class": "chat-bot"},
            ui.tags.span("🤖", {"class": "chat-bot-icon"}),
            ui.tags.div({"class": "chat-bot-message"},
                        "가까운 상담소 정보를 찾고, 귀농 준비를 도와드릴게요 🧑‍🏫"
            )
        ),
            ui.h2("📚 영천시 농업기술센터 및 귀농 지원 기관 지도"),
            ui.tags.div(
                {"class": "row"},
                ui.tags.div(
                    {"class": "col-md-12"},
                    ui.card(
                        ui.card_header("📋 영천 농업기술센터 정보 지도"),
                        ui.tags.iframe(src="/static/yc_act_map.html", width="100%", height="500px", style="border:none;")
                    )
                )
            ),
            ui.tags.hr(),
            ui.card(
                ui.card_header("🏢 농업 센터 상담 및 교육"),
                ui.input_selectize(
                    "category_filter", 
                    "📦 시설 분류 선택 (다중 선택 가능)", 
                    choices=["농업인 상담소", "농산물 산지 유통센터", "농기계 임대 사업소"],
                    multiple=True,
                    selected=["농업인 상담소", "농산물 산지 유통센터", "농기계 임대 사업소"],
                    options={"placeholder": "시설 분류를 선택하세요"}
                ),
                ui.output_table("tech_center_table_ui")
            )
        )
    )
)

# =========================
# 🧠 Server Logic - 성능 최적화 및 코드 정리
# =========================

def server(input, output, session):
    # ---------------------------
    # 🎯 메인 인구 시각화
    # ---------------------------
    @output
    @render.plot
    def main_population_plot():
        """귀농 인구 변화 시각화"""
        return px.line(
            population_data,
            x="연도",
            y="귀농인구",
            markers=True,
            title="귀농 인구 변화"
        )


    @output
    @render_widget
    def farm_map_plot():
        df = filtered_df()
        fig = px.scatter_mapbox(
            df,
            lat="위도",
            lon="경도",
            color="재배작물",
            size="면적(평)",
            hover_name="주소",
            hover_data=["재배작물", "면적(평)"],
            zoom=11,
            height=500
        )
        fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        return fig
    # ---------------------------
    # 🎯 팜맵 필터링링 시각화
    # ---------------------------
    @output
    @render.table
    def filtered_farm_table():
        df = farm_df.copy()

        eupmyeon = input.filter_eupmyeon()
        crop = input.filter_crop()

        if eupmyeon:
            df = df[df["읍면동"].isin(eupmyeon)]
        if crop:
            df = df[df["재배작물"].isin(crop)]

        return df[["팜맵관리번호", "주소", "사용용도", "재배작물", "면적(제곱미터)","면적(평)"]]
    

    @reactive.Calc
    def filtered_df():
        df = farm_df.copy()
        eupmyeon = input.filter_eupmyeon()
        crop = input.filter_crop()

        if eupmyeon:
            df = df[df["읍면동"].isin(eupmyeon)]
        if crop:
            df = df[df["재배작물"].isin(crop)]

        return df[["팜맵관리번호", "주소", "사용용도", "재배작물", "면적(평)"]]


    @output
    @render.ui
    def paginated_table_ui():
        df = filtered_df()
        page_size = 10
        total_pages = max(1, int(np.ceil(len(df) / page_size)))

        # 기본 페이지 번호 설정 (input.page_num 없으면 1)
        current_page = input.page_num() if "page_num" in input else 1

        return ui.tags.div(
            ui.output_table("paginated_table"),
            ui.input_slider("page_num", "페이지 선택", min=1, max=total_pages, value=current_page, step = 1)
        )


    @output
    @render.table
    def paginated_table():
        df = filtered_df()
        page = input.page_num()
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return df.iloc[start_idx:end_idx]


    # 다운로드 CSV 처리
    @reactive.effect
    @reactive.event(input.download_csv)
    def save_csv():
        df = filtered_df()
        path = "ycdata/filtered_farm_data.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 저장됨: {path}")
            
    # ---------------------------
    # 🎯 읍면동 파이 차트 시각화
    # ---------------------------
    @output
    @render_widget
    def crop_pie_chart():
        eupmyeon = input.filter_eupmyeon_dropdown()
        df = farm_df.copy()

        if eupmyeon != "전체":
            df = df[df["읍면동"] == eupmyeon]

        crop_area = df.groupby("재배작물")["면적(평)"].sum().reset_index()

        fig = go.Figure(data=[
            go.Pie(
                labels=crop_area["재배작물"],
                values=crop_area["면적(평)"],
                hoverinfo="label+percent+value",
                textinfo="label+percent"
            )
        ])
        fig.update_layout(title=f"{eupmyeon} 지역 작물별 면적 분포")
        return fig
    # ---------------------------
    # 🧑‍🌾 기술센터 테이블 출력
    # ---------------------------
    
    # ────────────────────────────────────────
    # 🎯  인구 단계구분도 (Mapbox choropleth)
    # ────────────────────────────────────────
    @render_widget
    def population_map():
        # 1) Shapefile 읽기 & 좌표계 변환
        shp_folder = './ycdata/ychsi_map'
        shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]
        shp_path = os.path.join(shp_folder, shp_files[0])
        gdf = gpd.read_file(shp_path).to_crs(epsg=4326)

        # 2) 인구 통계 불러오기
        pop_df = pd.read_excel(
            './ycdata/15_24populat.xlsx',
            usecols=['행정기관', '연도', '총인구수', '남자 인구수', '여자 인구수']
        )

        # 숫자 처리
        pop_df['총인구수'] = pop_df['총인구수'].astype(str).str.replace(",", "").astype(int)
        pop_df['남자 인구수'] = pop_df['남자 인구수'].astype(str).str.replace(",", "").astype(int)
        pop_df['여자 인구수'] = pop_df['여자 인구수'].astype(str).str.replace(",", "").astype(int)

        # 성비 추가 (남성 인구 비율)
        pop_df['남성비율(%)'] = (pop_df['남자 인구수'] / pop_df['총인구수'] * 100).round(1)

        # 3) 2024년 필터링
        pop_2024 = pop_df[pop_df['연도'] == 2024]

        # 4) 병합
        merged = gdf.merge(
            pop_2024,
            left_on='ADM_NM',
            right_on='행정기관',
            how='left'
        )

        # 5) GeoJSON 변환
        geojson_dict = json.loads(merged.to_json())

        # 6) Plotly Choropleth Mapbox
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson_dict,
            locations='행정기관',
            featureidkey='properties.행정기관',
            color='총인구수',
            color_continuous_scale='YlGnBu',
            mapbox_style='carto-positron',
            zoom=9,
            center={
                'lat': merged.geometry.centroid.y.mean(),
                'lon': merged.geometry.centroid.x.mean()
            },
            opacity=0.75,
            labels={
                '총인구수': '총인구수',
                '남자 인구수': '남자 인구',
                '여자 인구수': '여자 인구',
                '남성비율(%)': '남성비율(%)'
            },
            hover_data={
                '행정기관': True,
                '총인구수': True,
                '남자 인구수': True,
                '여자 인구수': True,
                '남성비율(%)': True
            }
        )

        fig.update_layout(
            margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
            title_text='영천시 읍·면·동별 총인구수 및 성비 (2024년)'
        )

        return fig

    # 바인딩
    output.population_map = population_map


   
    # ---------------------------
    # 🎯 연령대·성별 인구 피라미드
    # ---------------------------
    @render_widget
    def age_distribution_plot():
        # 1) 엑셀 불러오기
        df = pd.read_excel(
            "./ycdata/final_25_pop.xlsx",
            dtype=str
        ).rename(columns={
            "연령": "연령대_raw",
            "남자 인구수": "인구수(남)",
            "여자 인구수": "인구수(여)"
        })

        # 2) 숫자 변환
        for col in ["인구수(남)", "인구수(여)"]:
            df[col] = df[col].str.replace(",", "").astype(int)
        df["인구수(남)"] = -df["인구수(남)"]  # 피라미드용 부호 반전

        # 3) 연령 숫자 추출 및 정수 변환
        df["age"] = df["연령대_raw"].str.extract(r"(\d+)").astype(float)
        df = df.dropna(subset=["age"])
        df["age"] = df["age"].astype(int)

        # 4) 10세 단위로 구간 나누기
        max_age = df["age"].max()
        bins = list(range(0, ((max_age // 10) + 1) * 10 + 1, 10))
        labels = [f"{b}-{b+9}세" for b in bins[:-1]]
        df["연령대"] = pd.cut(df["age"], bins=bins, right=False, labels=labels)

        # 5) 그룹핑하여 연령대별 인구 합계
        grouped = df.groupby("연령대")[["인구수(남)", "인구수(여)"]].sum().reset_index()

        # 6) 시각화용 long 포맷 변환
        df_long = grouped.melt(
            id_vars="연령대",
            value_vars=["인구수(남)", "인구수(여)"],
            var_name="성별",
            value_name="인구수"
        )
        df_long["연령대"] = pd.Categorical(df_long["연령대"], categories=labels, ordered=True)

        # 7) 피라미드 차트 생성
        max_pop = df_long["인구수"].abs().max()
        fig = px.bar(
            df_long,
            x="인구수", y="연령대",
            color="성별", orientation="h", barmode="relative",
            labels={"인구수": "인구수", "연령대": "연령대", "성별": "성별"},
            color_discrete_map={"인구수(남)": "steelblue", "인구수(여)": "lightcoral"}
        )
        fig.update_xaxes(
            tickvals=[-max_pop, -max_pop//2, 0, max_pop//2, max_pop],
            ticktext=[
                f"{int(max_pop):,}", f"{int(max_pop//2):,}", "0",
                f"{int(max_pop//2):,}", f"{int(max_pop):,}"
            ]
        )
        fig.update_layout(
            plot_bgcolor="white",
            margin=dict(l=80, r=80, t=50, b=50),
            title="영천시 연령대별 성별 인구 피라미드"
        )

        return fig

    output.age_distribution_plot = age_distribution_plot
    # ---------------------------
    # 🧑‍🌾 농업 통합 테이블 출력
    # ---------------------------
    # 필터링된 데이터 reactively 반환
    @reactive.Calc
    def filtered_tech_center():
        selected = input.category_filter()
        df = TECH_CENTER_DATA.copy()
        if selected:
            df = df[df["분류"].isin(selected)]
        else:
            df = df.iloc[0:0]  # 빈 DataFrame 반환
        return df

    # 페이지 번호 슬라이더 UI 포함 전체 테이블 UI
    @output
    @render.ui
    def tech_center_table_ui():
        df = filtered_tech_center()
        if df.empty:
            return ui.markdown("👉 분류를 선택하면 목록이 표시됩니다.")
        
        total_pages = int(np.ceil(len(df) / 10))
        return ui.tags.div(
            ui.output_table("tech_center_table"),
            ui.input_slider("tech_page", "페이지 선택", min=1, max=total_pages, value=1)
        )

    # 실제 페이지에 따라 보여줄 테이블 데이터
    @output
    @render.table
    def tech_center_table():
        df = filtered_tech_center()
        page = input.tech_page()
        start = (page - 1) * 10
        end = start + 10
        return df.iloc[start:end]



    # ---------------------------
    # 🌡 기후 데이터 필터링
    # ---------------------------
    @reactive.Calc
    def filtered_climate():
        df = load_climate_data()
        year_min, year_max = input.year_range()
        return df[(df["연도"] >= year_min) & (df["연도"] <= year_max)]
    

    # ---------------------------
    # 📊 기후 Plotly 시각화 (Widget)
    # ---------------------------
    @output
    @render_widget
    def climate_widget_plot():
        df = filtered_climate()
        indicator = input.indicator()
        agg_type = input.agg_type()

        group_col = "월" if agg_type == "월별" else "연도"
        grouped = df.groupby(group_col)[indicator].mean().reset_index()

        fig = go.Figure(data=[
            go.Scatter(
                x=grouped[group_col],
                y=grouped[indicator],
                mode="lines+markers",
                name=indicator
            )
        ])
        fig.update_layout(
            title=f"{group_col}별 {indicator} 평균",
            xaxis_title=group_col,
            yaxis_title=indicator,
            template="plotly_white"
        )
        return fig




# =========================
# 🚀 App Execution
# =========================

shiny_app = ShinyApp(app_ui, server=server)
main_api.mount("/shiny", shiny_app)
app = main_api

```