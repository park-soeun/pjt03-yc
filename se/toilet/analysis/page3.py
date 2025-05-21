import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from api_file.lactation_api import fetch_lactation_rooms
import folium
from folium.plugins import MarkerCluster

API_KEY = "42CA-2DDB-565B-5200-FD2F-F620-ADB3-718A"
df_lactation = fetch_lactation_rooms(API_KEY)

print(df_lactation.head())

df_lactation.columns

df_lactation[df_lactation['cityName'] == '영천시']

kb_df = pd.read_csv('../data/kb_df.csv')

df = kb_df.copy()


# 기존 항목
cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']

# 기존 4개 항목에 대한 비율
yeongcheon_base = df[df['시군구명'] == '영천시'][cols].mean()
gyeongbuk_base = df[cols].mean()

# 수유실 비율 (시군구별 수유실 수 / 전체 수유실 수)
# 전체 시군구 수유실 수 세기
lactation_counts = df_lactation['cityName'].value_counts(normalize=True)

yeongcheon_suyusil = lactation_counts.get('영천시', 0)

# 시리즈로 변환
yeongcheon_full = pd.concat([yeongcheon_base, pd.Series({'수유실': yeongcheon_suyusil})])
gyeongbuk_full = pd.concat([gyeongbuk_base, pd.Series({'수유실': 1.0 / len(lactation_counts)})])  # 평균 분포

yeongcheon_rates = yeongcheon_full
gyeongbuk_rates = gyeongbuk_full




import plotly.graph_objects as go

# 항목 레이블
labels = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨', '수유실']

# 수유실은 lactation API로부터 가져온 개수 기준으로 추가
yeongcheon_lactation = len(df_lactation[df_lactation['cityName'] == '영천시'])
gyeongbuk_lactation = df_lactation['cityName'].value_counts(normalize=True).mean() * 100  # 평균 비율로 대략 설정

# 기존 비율에 수유실 비율 추가
yeongcheon_values = yeongcheon_rates.tolist()[:-1] + [yeongcheon_lactation / 100]  # 임의 정규화
gyeongbuk_values = gyeongbuk_rates.tolist()[:-1] + [gyeongbuk_lactation / 100]      # 임의 정규화

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=yeongcheon_values,
    theta=labels,
    fill='toself',
    name='영천시',
    line=dict(color='#1f77b4')
))

fig_radar.add_trace(go.Scatterpolar(
    r=gyeongbuk_values,
    theta=labels,
    fill='toself',
    name='경북 평균',
    line=dict(color='gray')
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 0.5]
        )
    ),
    title="영천시 vs 경북 평균 (여성친화시설 설치율)",
    showlegend=True,
    template="plotly_white"
)

fig_radar.show()




# ===
import pandas as pd
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# 1. 기본 항목 + 수유실 포함
base_cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']
grouped = df.groupby('시군구명')[base_cols].mean().reset_index()

# 수유실: 경상북도 전체 시군구 기준 비율로 매핑
suyusil_counts = df_lactation['cityName'].value_counts(normalize=True)
grouped['수유실'] = grouped['시군구명'].map(suyusil_counts).fillna(0)

# Melt
df_long = grouped.melt(id_vars='시군구명', var_name='항목', value_name='설치율')

# 항목별 trace로 나눠서 추가
fig = go.Figure()
항목리스트 = df_long['항목'].unique()

for 항목 in 항목리스트:
    temp = df_long[df_long['항목'] == 항목]
    
    colors = temp['시군구명'].apply(lambda x: '#1f77b4' if x == '영천시' else '#d3d3d3')

    fig.add_trace(go.Bar(
        x=temp['시군구명'],
        y=temp['설치율'],
        name=항목,
        marker_color=colors
    ))

fig.update_layout(
    title='시군구별 여성친화 시설 설치율 (영천시 강조)',
    barmode='group',
    xaxis_tickangle=-45,
    template='plotly_white'
)

fig.show()


# ------------------------



# ✅ 수유실 유형 + 아빠이용 여부 결합
df["유형_아빠이용"] = df["수유실종류"] + " / " + df["아빠이용"]

# ✅ 카운트 집계
type_counts = df["유형_아빠이용"].value_counts().reset_index()
type_counts.columns = ["수유실유형_아빠이용", "개수"]

# ✅ 파이차트 그리기
fig = px.pie(
    type_counts,
    names="수유실유형_아빠이용",
    values="개수",
    title="경상북도 수유실 유형 + 아빠이용 여부 분포",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(textinfo='label+percent')
fig.update_layout(template="plotly_white")
fig.show()

df_lactation.columns

# 컬럼 리네이밍
df_lactation = df_lactation.rename(columns={
    "roomNo": "ID",
    "roomName": "수유실명",
    "cityName": "시군구명",        # 요기!!
    "zoneName": "광역시도",
    "townName": "도로명",
    "roomTypeName": "수유실종류",
    "managerTelNo": "연락처",
    "address": "주소",
    "location": "상세위치",
    "fatherUseNm": "아빠이용",
    "gpsLat": "위도",
    "gpsLong": "경도"
})

df_lactation['수유실종류']

df_lactation["유형_아빠이용"] = df_lactation["수유실종류"] + " / " + df_lactation["아빠이용"]



# ✅ 카운트 집계
type_counts = df_lactation["유형_아빠이용"].value_counts().reset_index()
type_counts.columns = ["수유실유형_아빠이용", "개수"]

# ✅ 파이차트 그리기
fig = px.pie(
    type_counts,
    names="수유실유형_아빠이용",
    values="개수",
    title="경상북도 수유실 유형 + 아빠이용 여부 분포",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(textinfo='label+percent')
fig.update_layout(template="plotly_white")
fig.show()



# -----
# 비상벨 3


# NaN 제거 (비상벨 정보가 없는 행 제거)
kb_df = kb_df.dropna(subset=["비상벨"])

# 시군구별 비상벨 설치율 계산
bell_stats = kb_df.groupby("시군구명")["비상벨"].agg(["mean", "count"]).reset_index()
bell_stats.columns = ["시군구명", "비상벨설치율", "총화장실수"]

# 정렬: 비상벨설치율 내림차순
bell_stats = bell_stats.sort_values("비상벨설치율", ascending=False).reset_index(drop=True)

# 색상 지정
bell_stats["색상"] = bell_stats["시군구명"].apply(
    lambda x: "#1f77b4" if x == "영천시" else "#d3d3d3"
)

# 시각화
fig = go.Figure()

fig.add_trace(go.Bar(
    x=bell_stats["시군구명"],
    y=bell_stats["비상벨설치율"],
    text=[f"{x:.0%}" for x in bell_stats["비상벨설치율"]],
    marker_color=bell_stats["색상"],
    textposition="outside",
    name="비상벨 설치율"
))

fig.update_layout(
    title="경상북도 시군구별 비상벨 설치율",
    xaxis_title="시군구",
    yaxis_title="설치율",
    template="plotly_white",
    yaxis_tickformat=".0%",
    xaxis_tickangle=-45
)

fig.show()



kb_df.columns

kb_df


# 컬럼 이름 변경
rename_dict = {
    '남성용-어린이용대변기수': '남아 대변기',
    '남성용-어린이용소변기수': '남아 소변기',
    '여성용-어린이용대변기수': '여아 대변기'
}
kb_df = kb_df.rename(columns=rename_dict)

# 시군구별 평균
grouped = kb_df.groupby("시군구명")[list(rename_dict.values())].mean()

# 영천시와 전체 평균
yeongcheon = grouped.loc["영천시"]
gyeongbuk_avg = grouped.mean()

# 레이더 차트
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=yeongcheon.tolist(),
    theta=yeongcheon.index.tolist(),
    fill='toself',
    name='영천시',
    line=dict(color='#1f77b4')
))
fig.add_trace(go.Scatterpolar(
    r=gyeongbuk_avg.tolist(),
    theta=gyeongbuk_avg.index.tolist(),
    fill='toself',
    name='경북 평균',
    line=dict(color='gray')
))
fig.update_layout(
    title='영천시 vs 경북 평균 (어린이용 기기 설치 평균)',
    polar=dict(radialaxis=dict(visible=True, range=[0, max(yeongcheon.max(), gyeongbuk_avg.max()) * 1.1])),
    showlegend=True,
    template='plotly_white'
)
fig.show()