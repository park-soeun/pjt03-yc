import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go


# ===
# [1] 시군구별 전체 화장실 수
# ===



df = pd.read_csv('../data/kb_df.csv')

# 시군구명 기준으로 화장실 수 카운트
toilet_by_region = df['시군구명'].value_counts(dropna=False).reset_index()
toilet_by_region.columns = ['시군구명', '화장실수']


# 정렬
df_plot = toilet_by_region.sort_values('화장실수', ascending=False)

# 색상 컬럼 만들기
df_plot['색상'] = df_plot['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
)

# Plotly bar chart
fig = px.bar(
    df_plot,
    x='시군구명',
    y='화장실수',
    title='경상북도 시군구별 공공화장실 수',
    labels={'시군구명': '시군구', '화장실수': '화장실 수'},
    color='색상',  # 색상 구분에 사용할 컬럼
    color_discrete_map='identity'  # HEX 색상 직접 적용
)

fig.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,  # 범례 숨기기
    template='plotly_white'
)

fig.show()


# ===
# [2] 인구 1만명당 화장실 수
# ===

kb_df = pd.read_csv('../data/kb_df.csv')
pop_df = pd.read_csv('../data/pop_2023.csv')

pop_df

target_regions = kb_df['시군구명'].dropna().unique()

# 시군구명 + 총인구 열만 추출
pop_df = pop_df.iloc[:, [0, 1]].copy()
pop_df.columns = ['행정구역별(읍면동)', '총인구(명)']

# 문자열 정제
pop_df['행정구역별(읍면동)'] = pop_df['행정구역별(읍면동)'].str.strip()
pop_df['총인구(명)'] = pd.to_numeric(pop_df['총인구(명)'], errors='coerce')

# 필터링: kb_df에 존재하는 시군구만
pop_df_filtered = pop_df[pop_df['행정구역별(읍면동)'].isin(target_regions)].copy()
pop_df = pop_df_filtered

pop_df.columns = ['시군구명', '총인구']

merged_df = pd.merge(toilet_by_region, pop_df, on='시군구명', how='inner')
merged_df['인구1만명당_화장실수'] = merged_df['화장실수'] / (merged_df['총인구'] / 10000)



# 색상 지정: 영천시만 강조
merged_df['색상'] = merged_df['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
)

# 정렬
merged_df_sorted = merged_df.sort_values('인구1만명당_화장실수', ascending=False)

# 시각화
fig = px.bar(
    merged_df_sorted,
    x='시군구명',
    y='인구1만명당_화장실수',
    title='경상북도 시군구별 인구 1만명당 공공화장실 수',
    labels={'시군구명': '시군구', '인구1만명당_화장실수': '1만명당 화장실 수'},
    color='색상',
    color_discrete_map='identity'
)

fig.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    template='plotly_white'
)

fig.show()



# ===
# [3] 행정면적당 화장실 수
# ===

area_df = pd.read_csv('../data/area_2023.csv')

area_df.columns = ['시군구명', '면적']

area_df_filtered = area_df[area_df['시군구명'].isin(target_regions)].copy()
area_df = area_df_filtered

merged_area = pd.merge(toilet_by_region, area_df, on='시군구명', how='inner')

merged_area['면적당_화장실수'] = merged_area['화장실수'] / merged_area['면적']


# 색상 구분
merged_area['색상'] = merged_area['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
)

# 정렬
merged_area_sorted = merged_area.sort_values('면적당_화장실수', ascending=False)

# 바차트 그리기
fig = px.bar(
    merged_area_sorted,
    x='시군구명',
    y='면적당_화장실수',
    title='경상북도 시군구별 면적당 공공화장실 수 (개/m²)',
    labels={'시군구명': '시군구', '면적당_화장실수': '면적당 화장실 수'},
    color='색상',
    color_discrete_map='identity'
)

fig.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    template='plotly_white'
)

fig.show()





# ===
# [4] 연도별 증가율 상/하위 시군구
# ===
kb_df['설치연도'] = pd.to_datetime(kb_df['설치연월'], errors='coerce').dt.year

yearly = df.dropna(subset=['설치연도']).groupby(['시군구명', '설치연도']).size().reset_index(name='설치수')
# 연도 오름차순 정렬
yearly['설치연도'] = pd.to_numeric(yearly['설치연도'], errors='coerce')
# 연도별 정렬 필수!
yearly_sorted = yearly.sort_values(['시군구명', '설치연도'])

# 시군구별 누적 설치수 계산
yearly_sorted['누적설치수'] = (
    yearly_sorted
    .groupby('시군구명')['설치수']
    .cumsum()
)

fig = px.line(
    yearly_sorted,
    x='설치연도',
    y='누적설치수',
    color='시군구명',
    title='시군구별 공공화장실 누적 설치 수 추이',
    markers=True
)

fig.update_layout(
    template='plotly_white',
    xaxis_title='설치연도',
    yaxis_title='누적 설치 수'
)

fig.show()

# -----------

yearly = yearly_sorted
# 피벗테이블: 시군구 × 연도
pivot_df = yearly.pivot(index='시군구명', columns='설치연도', values='설치수').fillna(0)

# 분석할 연도 선택
start_year = 2015
end_year = 2023

# 증가율 계산
pivot_df['증가율'] = ((pivot_df[end_year] - pivot_df[start_year]) / pivot_df[start_year].replace(0, 1)) * 100

# Top 5 증가 시군구
top5 = pivot_df.sort_values('증가율', ascending=False).head(5)[['증가율']]

# Bottom 5 증가 시군구
bottom5 = pivot_df.sort_values('증가율', ascending=True).head(5)[['증가율']]


# Top 5 증가율 바차트
fig = go.Figure()
fig.add_trace(go.Bar(
    x=top5.index,
    y=top5['증가율'],
    name='증가율 Top 5',
    marker_color='seagreen'
))
fig.update_layout(
    title='2015~2023 공공화장실 증가율 Top 5 시군구',
    template='plotly_white',
    yaxis_title='증가율 (%)'
)
fig.show()

# ---------------------------

# 1. 상하위 시군구 이름 리스트
top5_regions = top5.index.tolist()
bottom5_regions = bottom5.index.tolist()

# 2. 원본 연도별 설치 수 데이터에서 필터링
top5_line_df = yearly[yearly['시군구명'].isin(top5_regions)]
bottom5_line_df = yearly[yearly['시군구명'].isin(bottom5_regions)]

# 3. 정렬 보장
top5_line_df = top5_line_df.sort_values(['시군구명', '설치연도'])
bottom5_line_df = bottom5_line_df.sort_values(['시군구명', '설치연도'])

# 누적합 계산
top5_line_df['누적설치수'] = (
    top5_line_df.sort_values(['시군구명', '설치연도'])
    .groupby('시군구명')['설치수']
    .cumsum()
)

bottom5_line_df['누적설치수'] = (
    bottom5_line_df.sort_values(['시군구명', '설치연도'])
    .groupby('시군구명')['설치수']
    .cumsum()
)



fig_top = px.line(
    top5_line_df,
    x='설치연도',
    y='누적설치수',
    color='시군구명',
    markers=True,
    title='누적 설치 수 추이 (증가율 Top 5 시군구)'
)
fig_top.update_layout(
    template='plotly_white',
    yaxis_title='누적 설치 수'
)
fig_top.show()


fig_bottom = px.line(
    bottom5_line_df,
    x='설치연도',
    y='누적설치수',
    color='시군구명',
    markers=True,
    title='누적 설치 수 추이 (증가율 Bottom 5 시군구)'
)
fig_bottom.update_layout(
    template='plotly_white',
    yaxis_title='누적 설치 수'
)
fig_bottom.show()


# ---- 영천시 까지 함께 그리기

# Top 5 + Bottom 5 결합
combined_df = pd.concat([top5_line_df, bottom5_line_df], ignore_index=True)

# 누적설치수 다시 한 번 안전하게 정리 (혹시 안 되어 있을 수도 있으니까!)
combined_df = combined_df.sort_values(['시군구명', '설치연도'])
combined_df['누적설치수'] = combined_df.groupby('시군구명')['설치수'].cumsum()

yeongcheon_df = yearly[yearly['시군구명'] == '영천시'].copy()
yeongcheon_df = yeongcheon_df.sort_values('설치연도')
yeongcheon_df['누적설치수'] = yeongcheon_df['설치수'].cumsum()
yeongcheon_df['색상'] = '#1f77b4'  # 진한 파랑

combined_with_yc = pd.concat([combined_df, yeongcheon_df], ignore_index=True)


fig = go.Figure()

for region in combined_with_yc['시군구명'].unique():
    region_df = combined_with_yc[combined_with_yc['시군구명'] == region]
    color = '#1f77b4' if region == '영천시' else '#d3d3d3'

    fig.add_trace(go.Scatter(
        x=region_df['설치연도'],
        y=region_df['누적설치수'],
        mode='lines+markers',
        name=region,
        line=dict(color=color, width=4 if region == '영천시' else 1.5),
        marker=dict(size=6 if region == '영천시' else 4),
        opacity=1 if region == '영천시' else 0.5,
        showlegend=True
    ))

fig.update_layout(
    title='공공화장실 누적 설치 수 추이 (영천시 강조)',
    xaxis_title='설치연도',
    yaxis_title='누적 설치 수',
    template='plotly_white'
)

fig.show()




# ===
# [5] 시 vs 군 화장실 분포 
# ===


toilet_by_region['지역유형'] = toilet_by_region['시군구명'].str[-1].map({
    '시': '시',
    '군': '군'
})

region_type_df = toilet_by_region.groupby('지역유형')['화장실수'].sum().reset_index()


import plotly.express as px

fig_pie = px.pie(
    region_type_df,
    names='지역유형',
    values='화장실수',
    title='도시 vs 농촌 공공화장실 비율',
    color='지역유형',
    color_discrete_map={'시': '#1f77b4', '군': '#d3d3d3'}
)

fig_pie.update_traces(textinfo='label+percent', pull=[0.05, 0])
fig_pie.update_layout(template='plotly_white')
fig_pie.show()


fig_bar = px.bar(
    region_type_df,
    x='지역유형',
    y='화장실수',
    title='도시 vs 농촌 공공화장실 수 비교',
    color='지역유형',
    color_discrete_map={'도시': '#1f77b4', '농촌': '#d3d3d3'},
    text='화장실수'
)

fig_bar.update_layout(template='plotly_white', showlegend=False)
fig_bar.show()



# ===
# [6] 개방 시간
# === 


kb_df['개방시간'].unique()
kb_df['개방시간상세'].unique()


def classify_open_type(row):
    기본 = str(row['개방시간']) if pd.notna(row['개방시간']) else ''
    상세 = str(row['개방시간상세']) if pd.notna(row['개방시간상세']) else ''
    combined = 기본 + ' ' + 상세  # 하나의 문자열로 합치고 분류

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
yc_df = pd.read_csv('../data/yc_df.csv')
yc_df['개방시간유형'] = yc_df.apply(classify_open_type, axis=1)
yc_df['주말개방여부'] = yc_df.apply(check_weekend_open, axis=1)


print(kb_df['개방시간유형'].value_counts())

# 이건 경북
open_type_kb_df = kb_df['개방시간유형'].value_counts().reset_index()
open_type_kb_df.columns = ['개방시간유형', '화장실수']

fig = px.pie(
    open_type_kb_df,
    names='개방시간유형',
    values='화장실수',
    title='경북 전체 공공화장실 개방시간 유형 분포',
    hole=0.5,
    color='개방시간유형',
    color_discrete_map={
        '24시간': '#1f77b4',
        '주간개방': '#aec7e8',
        '제한적 운영': '#ffbb78',
        '정보없음': '#d3d3d3'
    }
)

fig.update_traces(textinfo='label+percent')
fig.update_layout(template='plotly_white')
fig.show()

# -- 이건 영천
open_type_yc_df = yc_df['개방시간유형'].value_counts().reset_index()
open_type_yc_df.columns = ['개방시간유형', '화장실수']

fig = px.pie(
    open_type_yc_df,
    names='개방시간유형',
    values='화장실수',
    title='영천시 공공화장실 개방시간 유형 분포',
    hole=0.5,
    color='개방시간유형',
    color_discrete_map={
        '24시간': '#1f77b4',
        '주간개방': '#aec7e8',
        '제한적 운영': '#ffbb78',
        '정보없음': '#d3d3d3'
    }
)

fig.update_traces(textinfo='label+percent')
fig.update_layout(template='plotly_white')
fig.show()


# -- 영천 주말
weekend_open_df = yc_df['주말개방여부'].value_counts().reset_index()
weekend_open_df.columns = ['주말개방여부', '화장실수']



fig = px.pie(
    weekend_open_df,
    names='주말개방여부',
    values='화장실수',
    title='공공화장실 주말 개방 여부',
    hole=0.5,
    color='주말개방여부',
    color_discrete_map={
        '개방': '#1f77b4',
        '미개방': '#d62728',
        '불명확': '#cccccc'
    }
)

fig.update_traces(textinfo='label+percent')
fig.update_layout(template='plotly_white')
fig.show()


# ===
# [7] 관리기관별 분포   
# ===

kb_df.info()
yc_df['관리기관명'].unique()


kb_df.info()