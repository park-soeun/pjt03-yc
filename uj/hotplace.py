# 유동인구/혼잡도
import pandas as pd

# 관광지 데이터
df_attract = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/public/asset/data/KC_495_LLR_ATRCTN_2023.csv')
# print(df_attract.columns.tolist())

# 유동인구 데이터
df_pop = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/원본/경상북도 영천시 유동인구 수.CSV')
# print(df_pop.columns.tolist())

# 관광지 데이터 컬럼명 맞추기
df_attract = df_attract.rename(columns={'SIGNGU_NM': 'SGG_NM'})

# 관광지 데이터와 유동인구 데이터의 가장 세분화된 공간 컬럼명을 확인
print(df_attract.columns)
print(df_pop.columns)

# 예시: 법정동명 기준 병합 (가능할 때)
if 'LEGALDONG_NM' in df_attract.columns and 'LEGALDONG_NM' in df_pop.columns:
    df_merged = pd.merge(
        df_attract,
        df_pop,
        on='LEGALDONG_NM',
        how='left'
    )
else:
    # 없으면 시군구명 기준 병합(관광지별 값이 같아짐)
    df_merged = pd.merge(
        df_attract,
        df_pop,
        on='SGG_NM',
        how='left'
    )

# 관광지별 유동인구 합계 (이동인구 기준)
tour_pop = df_merged.groupby(['POI_NM', 'LC_LA', 'LC_LO'])['REVISN_AMBLT_PUL_CNT'].sum().reset_index()
tour_pop = tour_pop.sort_values('REVISN_AMBLT_PUL_CNT', ascending=False)
print(tour_pop.head(10))
# print(tour_pop.columns.tolist())

# 시각화 코드는 동일하게 사용


# 지도 히트맵 시각화
import folium
from folium.plugins import HeatMap

import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'  # '맑은 고딕' 폰트 사용
plt.rcParams['axes.unicode_minus'] = False     # 마이너스(-) 기호 깨짐 방지

# NaN 좌표 제거
tour_pop = tour_pop.dropna(subset=['LC_LA', 'LC_LO'])

# folium 지도 생성
m = folium.Map(location=[tour_pop['LC_LA'].mean(), tour_pop['LC_LO'].mean()], zoom_start=12)

# 히트맵 데이터 준비
heat_data = list(zip(tour_pop['LC_LA'], tour_pop['LC_LO'], tour_pop['REVISN_AMBLT_PUL_CNT']))

# 히트맵 추가
HeatMap(heat_data, radius=20, max_zoom=13).add_to(m)
m.save('heatmap.html')


# 인기 관광지 랭킹 상위 10개 표
top10 = tour_pop.head(10).copy()

# 순위(1부터 시작) 컬럼 추가
top10.insert(0, '순위', range(1, len(top10)+1))

# 유동인구수에 콤마 넣기
top10['유동인구수'] = top10['REVISN_AMBLT_PUL_CNT'].apply(lambda x: f"{int(x):,}")

# 필요한 컬럼만 남기고 이름 보기 좋게 변경
top10 = top10[['순위', 'POI_NM', 'LC_LA', 'LC_LO', '유동인구수']]
top10 = top10.rename(columns={
    'POI_NM': '관광지명',
    'LC_LA': '위도',
    'LC_LO': '경도'
})

# 표 형태로 출력
print(top10.to_string(index=False))


# 한적한 관광지(유동인구 적은 곳) 지도
# 유동인구수 하위 10개(한적한 관광지)
quiet_spots = tour_pop.nsmallest(10, 'REVISN_AMBLT_PUL_CNT')

m = folium.Map(location=[quiet_spots['LC_LA'].mean(), quiet_spots['LC_LO'].mean()], zoom_start=12)
for idx, row in quiet_spots.iterrows():
    folium.Marker([row['LC_LA'], row['LC_LO']], popup=row['POI_NM']).add_to(m)
m.save('quiet_spots.html')


# 요일/시간대별 유동인구 히트맵
# 원하는 요일 순서 지정
day_order = ['월', '화', '수', '목', '금', '토', '일']

# 피벗테이블 생성
pivot = df_pop.pivot_table(
    index='TMZN_CD',
    columns='DWK_NM',
    values='REVISN_AMBLT_PUL_CNT',
    aggfunc='sum'
)

# 열 순서 재정렬
pivot = pivot[day_order]

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.0f')
plt.title('요일/시간대별 유동인구 히트맵')
plt.xlabel('요일')
plt.ylabel('시간대')
plt.show()


# 시간대별 전체 유동인구 변화 추이
trend = df_pop.groupby('TMZN_CD')['REVISN_AMBLT_PUL_CNT'].sum().reset_index()
plt.figure(figsize=(10,4))
plt.plot(trend['TMZN_CD'], trend['REVISN_AMBLT_PUL_CNT'], marker='o')
plt.title('시간대별 유동인구 변화 추이')
plt.xlabel('시간대')
plt.ylabel('유동인구수')
plt.grid(True)
plt.show()


# 연령대별 유동인구
age_pop = df_pop.groupby('AGRDE_CLS')['REVISN_AMBLT_PUL_CNT'].sum().reset_index()
plt.figure(figsize=(8,4))
plt.bar(age_pop['AGRDE_CLS'].astype(str), age_pop['REVISN_AMBLT_PUL_CNT'])
plt.title('연령대별 유동인구')
plt.xlabel('연령대')
plt.ylabel('유동인구수')
plt.show()

# 성별 유동인구
sex_pop = df_pop.groupby('SEX_DV')['REVISN_AMBLT_PUL_CNT'].sum().reset_index()
plt.pie(sex_pop['REVISN_AMBLT_PUL_CNT'], labels=sex_pop['SEX_DV'].map({1:'남',2:'여'}), autopct='%1.1f%%')
plt.title('성별 유동인구 비율')
plt.show()


# 주중/주말 비교
df_pop['is_weekend'] = df_pop['DWK_NM'].isin(['토', '일'])
weekend_pop = df_pop.groupby('is_weekend')['REVISN_AMBLT_PUL_CNT'].sum()
plt.bar(['주중', '주말'], weekend_pop)
plt.title('주중 vs 주말 유동인구')
plt.ylabel('유동인구수')
plt.show()


# 시간대별 유동인구 랭킹
top_times['유동인구수(만)'] = top_times['REVISN_AMBLT_PUL_CNT'] / 10000
top_times['유동인구수(만)'] = top_times['유동인구수(만)'].apply(lambda x: f"{x:.2f}만")
print(top_times[['TMZN_CD', '유동인구수(만)']])



import geopandas as gpd

# SHP 파일 로드
yeongcheon = gpd.read_file("C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/ychsi-map/ychsi.shp")

# 좌표계 확인 및 변환 (WGS84 기준)
print(yeongcheon.crs)  # 현재 좌표계 확인
yeongcheon = yeongcheon.to_crs(epsg=4326)  # WGS84로 변환

# 기본 지도 시각화
yeongcheon.plot(figsize=(10,10), edgecolor='black')
plt.title("영천시 읍면동 행정구역")
plt.show()
