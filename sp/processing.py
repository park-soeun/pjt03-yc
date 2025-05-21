import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from api_file.lactation_api import fetch_lactation_rooms

# =======================
# 1. 기본 데이터 불러오기
# =======================

def load_toilet_data(kb_path):
    df = pd.read_csv(kb_path)
    df = df[df["시군구명"].notna()]
    return df

def load_population_data(pop_path):
    pop_df = pd.read_csv(pop_path)
    pop_df = pop_df.iloc[:, [0, 1]].copy()
    pop_df.columns = ['시군구명', '총인구']
    pop_df['시군구명'] = pop_df['시군구명'].str.strip()
    pop_df['총인구'] = pd.to_numeric(pop_df['총인구'], errors='coerce')
    return pop_df

def load_area_data(area_path):
    df = pd.read_csv(area_path)
    df.columns = ["시군구명", "면적"]
    df["시군구명"] = df["시군구명"].str.strip()
    return df

# =======================
# 2. 기본 통계 가공
# =======================

def get_toilet_count_by_region(df):
    toilet_by_region = df["시군구명"].value_counts().reset_index()
    toilet_by_region.columns = ["시군구명", "화장실수"]
    toilet_by_region = toilet_by_region.sort_values("화장실수", ascending=False)
    toilet_by_region["색상"] = toilet_by_region["시군구명"].apply(
        lambda x: "#1f77b4" if x == "영천시" else "#cccccc"
    )
    return toilet_by_region

def get_toilet_per_10k(toilet_df, pop_df):
    toilet_by_region = toilet_df["시군구명"].value_counts().reset_index()
    toilet_by_region.columns = ["시군구명", "화장실수"]
    target_regions = toilet_df["시군구명"].dropna().unique()
    pop_df = pop_df[pop_df["시군구명"].isin(target_regions)]

    merged = pd.merge(toilet_by_region, pop_df, on="시군구명", how="inner")
    merged["인구1만명당_화장실수"] = merged["화장실수"] / (merged["총인구"] / 10000)
    merged["색상"] = merged["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#cccccc")
    return merged.sort_values("인구1만명당_화장실수", ascending=False)

def get_toilet_density(toilet_df, area_df):
    toilet_by_region = toilet_df["시군구명"].value_counts().reset_index()
    toilet_by_region.columns = ["시군구명", "화장실수"]
    target_regions = toilet_df["시군구명"].dropna().unique()
    area_df = area_df[area_df["시군구명"].isin(target_regions)]

    merged = pd.merge(toilet_by_region, area_df, on="시군구명", how="inner")
    merged["면적당_화장실수"] = merged["화장실수"] / merged["면적"]
    merged["색상"] = merged["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#cccccc")
    return merged.sort_values("면적당_화장실수", ascending=False)

# =======================
# 3. 증가 추세 분석
# =======================

def get_toilet_growth_trend(df):
    df = df.copy()
    df["설치연도"] = pd.to_datetime(df["설치연월"], errors="coerce").dt.year
    yearly = df.dropna(subset=["설치연도"]).groupby(["시군구명", "설치연도"]).size().reset_index(name="설치수")
    yearly = yearly.sort_values(["시군구명", "설치연도"])
    yearly["누적설치수"] = yearly.groupby("시군구명")["설치수"].cumsum()
    return yearly

def get_combined_growth_comparison(df):
    yearly = get_toilet_growth_trend(df)
    pivot_df = yearly.pivot(index="시군구명", columns="설치연도", values="설치수").fillna(0)
    pivot_df["증가율"] = ((pivot_df[2023] - pivot_df[2015]) / pivot_df[2015].replace(0, 1)) * 100

    top5 = pivot_df.sort_values("증가율", ascending=False).head(5).index.tolist()
    bottom5 = pivot_df.sort_values("증가율", ascending=True).head(5).index.tolist()
    top5_line = yearly[yearly["시군구명"].isin(top5)]
    bottom5_line = yearly[yearly["시군구명"].isin(bottom5)]
    yc = yearly[yearly["시군구명"] == "영천시"]

    combined = pd.concat([top5_line, bottom5_line, yc], ignore_index=True)
    combined = combined.sort_values(["시군구명", "설치연도"])
    combined["누적설치수"] = combined.groupby("시군구명")["설치수"].cumsum()
    return combined

# =======================
# 4. 개방 시간 분류
# =======================

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

def load_processed_opening_data(kb_path, yc_path):
    kb_df = pd.read_csv(kb_path)
    yc_df = pd.read_csv(yc_path)

    kb_df['개방시간유형'] = kb_df.apply(classify_open_type, axis=1)
    kb_df['주말개방여부'] = kb_df.apply(check_weekend_open, axis=1)
    yc_df['개방시간유형'] = yc_df.apply(classify_open_type, axis=1)
    yc_df['주말개방여부'] = yc_df.apply(check_weekend_open, axis=1)

    return kb_df, yc_df

# =======================
# 5. 여성/가족 인프라
# =======================

def prepare_radar_data(kb_path, api_key):
    df_lactation = fetch_lactation_rooms(api_key)
    df = pd.read_csv(kb_path)

    base_cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']
    yeongcheon_base = df[df['시군구명'] == '영천시'][base_cols].mean()
    gyeongbuk_base = df[base_cols].mean()

    lactation_counts = df_lactation['시군구명'].value_counts(normalize=True)
    yeongcheon_lactation = lactation_counts.get('영천시', 0)

    yeongcheon_full = pd.concat([yeongcheon_base, pd.Series({'수유실': yeongcheon_lactation})])
    gyeongbuk_full = pd.concat([gyeongbuk_base, pd.Series({'수유실': 1.0 / len(lactation_counts)})])

    return yeongcheon_full, gyeongbuk_full

def prepare_grouped_bar_data(kb_path, df_lactation):
    df = pd.read_csv(kb_path)
    base_cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']
    grouped = df.groupby('시군구명')[base_cols].mean().reset_index()
    suyusil_counts = df_lactation['시군구명'].value_counts(normalize=True)
    grouped['수유실'] = grouped['시군구명'].map(suyusil_counts).fillna(0)
    df_long = grouped.melt(id_vars='시군구명', var_name='항목', value_name='설치율')
    return df_long

def preprocess_emergency_bell(df):
    df = df.dropna(subset=["비상벨"])
    bell_stats = df.groupby("시군구명")["비상벨"].agg(["mean", "count"]).reset_index()
    bell_stats.columns = ["시군구명", "비상벨설치율", "총화장실수"]
    bell_stats = bell_stats.sort_values("비상벨설치율", ascending=False).reset_index(drop=True)
    bell_stats["색상"] = bell_stats["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#d3d3d3")
    return bell_stats

def preprocess_cctv(df):
    df = df.dropna(subset=["CCTV"])
    cctv_stats = df.groupby("시군구명")["CCTV"].agg(["mean", "count"]).reset_index()
    cctv_stats.columns = ["시군구명", "CCTV설치율", "총화장실수"]
    cctv_stats = cctv_stats.sort_values("CCTV설치율", ascending=False).reset_index(drop=True)
    cctv_stats["색상"] = cctv_stats["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#d3d3d3")
    return cctv_stats

def preprocess_diaper(df):
    df = df.dropna(subset=["기저귀교환대"])
    diaper_stats = df.groupby("시군구명")["기저귀교환대"].agg(["mean", "count"]).reset_index()
    diaper_stats.columns = ["시군구명", "기저귀교환대설치율", "총화장실수"]
    diaper_stats = diaper_stats.sort_values("기저귀교환대설치율", ascending=False).reset_index(drop=True)
    diaper_stats["색상"] = diaper_stats["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#d3d3d3")
    return diaper_stats

def preprocess_lactation_type(api_key):  # ✅ 인자 추가
    df_lactation = fetch_lactation_rooms(api_key)
    df_lactation["유형_아빠이용"] = df_lactation["수유실종류"] + " / " + df_lactation["아빠이용"]
    type_counts = df_lactation["유형_아빠이용"].value_counts().reset_index()
    type_counts.columns = ["수유실유형_아빠이용", "개수"]
    return type_counts

def preprocess_child_fixture_rates(df):
    rename_dict = {
        '남성용-어린이용대변기수': '남아 대변기',
        '남성용-어린이용소변기수': '남아 소변기',
        '여성용-어린이용대변기수': '여아 대변기'
    }
    df = df.rename(columns=rename_dict)
    grouped = df.groupby("시군구명")[list(rename_dict.values())].mean()
    yeongcheon = grouped.loc["영천시"]
    gyeongbuk_avg = grouped.mean()
    return yeongcheon, gyeongbuk_avg