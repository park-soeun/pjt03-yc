import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import folium
from folium.plugins import MarkerCluster


df = pd.read_csv('./data/toilet.csv')

df.columns

# 시군구명 추출
df['시군구명'] = df['소재지지번주소'].str.extract(r'경상북도\s+([^\s]+)')

# 읍면동명 추출
df['읍면동명'] = df['소재지지번주소'].str.extract(r'경상북도\s+[^\s]+\s+([^\s]+)')

# 결과 확인
print(df[['소재지지번주소', '시군구명', '읍면동명']])

df['설치연월']
df['리모델링연월']

df.info()

df['설치연도'] = pd.to_datetime(df['설치연월'], errors='coerce').dt.year
df['설치연도'] = df['설치연도'].fillna('미상')


fig = px.bar(df, x='설치연도', title='연도별 공공화장실 설치 현황')
fig.show()

# --- 전처리


# 4. 시설 여부 컬럼 이진화 (Yes/No → True/False)
def yesno_to_bool(val):
    return str(val).strip() == 'Yes' or str(val).strip() == 'Y'

df['기저귀교환대'] = df['기저귀교환대유무'].apply(yesno_to_bool)
df['CCTV'] = df['화장실입구CCTV설치유무'].apply(yesno_to_bool)
df['비상벨'] = df['비상벨설치여부'].apply(yesno_to_bool)

# 5. 장애인 화장실 유무 판단
df['장애인화장실'] = (df['남성용-장애인용대변기수'] + df['여성용-장애인용대변기수']) > 0

# 6. 어린이용 대변기 유무
df['어린이대변기'] = (df['남성용-어린이용대변기수'] + df['여성용-어린이용대변기수']) > 0

yc_df = df[df['시군구명'] == '영천시'].copy()
yc_df.to_csv('./data/yc_df.csv')
kb_df = df

kb_df['시군구명'].unique()
len(kb_df['시군구명'].unique())
kb_df[kb_df['시군구명'] == '수륜면']
kb_df[kb_df['시군구명'] == '용암면']
kb_df.loc
kb_df.loc[kb_df['시군구명'].str.contains('성주군', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('안동시', na=False), '시군구명'] = '안동시'
kb_df.loc[kb_df['시군구명'].str.contains('수륜면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('용암면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('가천면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('선남면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('대가면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('벽진면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('초전면', na=False), '시군구명'] = '성주군'
kb_df.loc[kb_df['시군구명'].str.contains('남산면', na=False), '시군구명'] = '경산시'
kb_df.loc[kb_df['시군구명'].str.contains('공성면', na=False), '시군구명'] = '상주시'
kb_df.loc[kb_df['시군구명'].str.contains('청송읍', na=False), '시군구명'] = '청송군'
kb_df.loc[kb_df['시군구명'].str.contains('봉성면', na=False), '시군구명'] = '봉화군'
kb_df.loc[kb_df['시군구명'].str.contains('가은읍', na=False), '시군구명'] = '문경시'
kb_df.to_csv('./data/kb_df.csv')

kb_df.info()

# 1. 시군구명 결측값을 소재지도로명주소에서 추출
mask_sgg_null = kb_df['시군구명'].isna() & kb_df['소재지도로명주소'].notna()
kb_df.loc[mask_sgg_null, '시군구명'] = kb_df.loc[mask_sgg_null, '소재지도로명주소'].str.extract(r'경상북도\s+([^\s]+)')

# 2. 읍면동명 결측값도 동일하게 시도
mask_emdong_null = kb_df['읍면동명'].isna() & kb_df['소재지도로명주소'].notna()
kb_df.loc[mask_emdong_null, '읍면동명'] = kb_df.loc[mask_emdong_null, '소재지도로명주소'].str.extract(r'경상북도\s+[^\s]+\s+([^\s]+)')


# --- folium 시각화

# 지도 초기화 (영천시 중심)
center_lat = yc_df['WGS84위도'].mean()
center_lon = yc_df['WGS84경도'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

# 마커 클러스터
marker_cluster = MarkerCluster().add_to(m)

# 마커 색상 지정 함수
def get_marker_color(row):
    if row['장애인화장실']:
        return 'blue'
    elif row['기저귀교환대']:
        return 'green'
    elif row['비상벨']:
        return 'orange'
    else:
        return 'gray'

# 팝업 HTML 템플릿
def generate_popup(row):
    return folium.Popup(f"""
    <b>{row['화장실명']}</b><br>
    📍 <b>주소:</b> {row['시군구명']} {row['읍면동명']}<br>
    🗓️ <b>설치연도:</b> {row['설치연도']}<br>
    ⏰ <b>개방시간:</b> {row['개방시간']}<br>
    ♿ <b>장애인 화장실:</b> {'O' if row['장애인화장실'] else 'X'}<br>
    👶 <b>기저귀 교환대:</b> {'O' if row['기저귀교환대'] else 'X'}<br>
    🚨 <b>비상벨:</b> {'O' if row['비상벨'] else 'X'}<br>
    📹 <b>CCTV:</b> {'O' if row['CCTV'] else 'X'}<br>
    👧 <b>어린이용 대변기:</b> {'O' if row['어린이대변기'] else 'X'}
    """, max_width=300)
# 필터링 추가
yc_df_map = yc_df.dropna(subset=['WGS84위도', 'WGS84경도']).copy()

# 마커 찍기
for _, row in yc_df_map.iterrows():
    color = get_marker_color(row)
    folium.CircleMarker(
        location=[row['WGS84위도'], row['WGS84경도']],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=generate_popup(row)
    ).add_to(marker_cluster)

# 결과 저장
m.save("yeongcheon_toilets_map.html")