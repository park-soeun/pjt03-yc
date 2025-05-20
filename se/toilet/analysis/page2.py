import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go
from plotly.subplots import make_subplots


birth_df = pd.read_csv('../data/birth.csv')

# 0행을 헤더로 설정
birth_df.columns = birth_df.iloc[0]
birth_df = birth_df.drop(index=0)

# 인덱스 초기화 및 컬럼명 재설정
birth_df.columns = ['시군구명', '2020', '2021', '2022', '2023']
birth_df = birth_df.reset_index(drop=True)

# 2023년 열만 사용 + 시군구명, 출산율만 남기기
birth_df = birth_df[['시군구명', '2023']]
birth_df = birth_df[birth_df['2023'] != '-'].copy()  # 결측 제외
birth_df['출산율'] = pd.to_numeric(birth_df['2023'])
birth_df = birth_df[['시군구명', '출산율']]

# 중복 제거 (의성군 등 중복 존재)
birth_df = birth_df.groupby('시군구명', as_index=False)['출산율'].mean()
birth_df = birth_df[(birth_df['시군구명'] != '경상북도') & (birth_df['시군구명'] != '남구') & (birth_df['시군구명'] != '북구')]


birth_df.to_csv('../data/birth_2023.csv')


birth_df = birth_df[['시군구명', '출산율']].copy()

birth_df['색상'] = birth_df['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
)

top10_df = birth_df.sort_values('출산율', ascending=False).head(10)

fig = px.bar(
    top10_df,
    x='시군구명',
    y='출산율',
    title='경상북도 시군구별 출산율 Top 10 (2023년)',
    color='색상',
    color_discrete_map='identity',
    text='출산율'
)
fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig.update_layout(
    template='plotly_white',
    showlegend=False,
    xaxis_tickangle=-45
)
fig.show()


# ---
# 전체


# 출산율 내림차순 정렬
birth_df_sorted = birth_df.sort_values('출산율', ascending=False)

# 색상 구분 컬럼 추가 (이미 했으면 생략 가능)
birth_df_sorted['색상'] = birth_df_sorted['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
)


fig = px.bar(
    birth_df_sorted,
    x='시군구명',
    y='출산율',
    title='경상북도 시군구별 출산율 (2023년)',
    color='색상',
    color_discrete_map='identity',
    text='출산율'
)

fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig.update_layout(
    template='plotly_white',
    xaxis_tickangle=-45,
    showlegend=False
)
fig.show()




# ===
# [2] 가족 배려 인프라 현황 (영천시)  
# ===


kb_df = pd.read_csv('../data/kb_df.csv')
yc_df = pd.read_csv('../data/yc_df.csv')
kb_df.info()

df = kb_df.copy()

cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']

yeongcheon_rates = df[df['시군구명'] == '영천시'][cols].mean()
gyeongbuk_rates = df[cols].mean()

# 2. 합치기
compare_df = pd.DataFrame({
    '항목': cols,
    '영천시': yeongcheon_rates.values * 100,
    '경북 평균': gyeongbuk_rates.values * 100
})

# 3. melt 형태로 변환
compare_df = compare_df.melt(id_vars='항목', var_name='지역', value_name='설치율')

# 4. 시각화
import plotly.express as px

fig = px.bar(
    compare_df,
    x='항목',
    y='설치율',
    color='지역',
    barmode='group',
    text='설치율',
    title='가족·사회배려 인프라 설치율 비교: 영천시 vs 경북 평균',
    color_discrete_map={'영천시': '#1f77b4', '경북 평균': '#cccccc'}
)

fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(template='plotly_white', yaxis_range=[0, 100])
fig.show()



data = pd.DataFrame({
    '항목': cols,
    '영천시': yeongcheon_rates.values * 100,
    '경북 평균': gyeongbuk_rates.values * 100
})
categories = data['항목']
fig = go.Figure()

# 영천시
fig.add_trace(go.Scatterpolar(
    r=data['영천시'],
    theta=categories,
    fill='toself',
    name='영천시',
    line=dict(color='#1f77b4')
))

# 경북 평균
fig.add_trace(go.Scatterpolar(
    r=data['경북 평균'],
    theta=categories,
    fill='toself',
    name='경북 평균',
    line=dict(color='#cccccc')
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 50]
        )
    ),
    title='영천시 vs 경북 평균: 가족·안전 인프라 설치율 비교',
    showlegend=True,
    template='plotly_white'
)

fig.show()


# --- 도넛차트

# 항목별 설치율 계산
rates = {
    '기저귀교환대': yc_df['기저귀교환대'].mean() * 100,
    '어린이대변기': yc_df['어린이대변기'].mean() * 100,
    'CCTV': yc_df['CCTV'].mean() * 100,
    '비상벨': yc_df['비상벨'].mean() * 100
}


fig = make_subplots(rows=1, cols=4, specs=[[{'type':'domain'}]*4],
                    subplot_titles=list(rates.keys()))

colors = ['#1f77b4', '#d3d3d3']

for i, (label, val) in enumerate(rates.items(), start=1):
    fig.add_trace(go.Pie(
        labels=['설치됨', '미설치됨'],
        values=[val, 100-val],
        hole=0.6,
        marker_colors=colors,
        textinfo='none',
        hoverinfo='label+percent'
    ), row=1, col=i)

fig.update_layout(
    title_text='영천시 가족친화 인프라 설치율 (도넛 차트)',
    showlegend=False,
    template='plotly_white'
)

fig.show()





# ===
# [4] 결합 인사이트 강조 (Optional)
# ===


cols = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨']

# 경북 전체 시군구별 평균 설치율 계산
infra_df = kb_df.groupby('시군구명')[cols].mean().reset_index()
infra_df['시설평균'] = infra_df[cols].mean(axis=1) * 100  # 퍼센트 단위

birth = birth_df[['시군구명', '출산율']].copy()

compare_df = pd.merge(infra_df, birth, on='시군구명', how='inner')
compare_df['색상'] = compare_df['시군구명'].apply(
    lambda x: '#1f77b4' if x == '영천시' else '#d3d3d3'
)



fig = px.scatter(
    compare_df,
    x='출산율',
    y='시설평균',
    text='시군구명',
    color='색상',
    color_discrete_map='identity',
    title='출산율 vs 가족·안전 인프라 설치율 (2023년)',
    size_max=10
)
fig.update_traces(marker=dict(size=12), textposition='top center')
fig.update_layout(template='plotly_white', showlegend=False)
fig.show()