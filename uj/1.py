import pandas as pd
import re

# 데이터 불러오기
tour_df = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/원본/영천_전체관광지_위경도_포함.csv', encoding='utf-8-sig')
cafe_df = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/영천_가성비_카페정보_위경도포함(최종).csv')
event_df = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/원본/경상북도 영천시_행사및축제_20221128.csv', encoding='cp949')
camp_df = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/원본/경상북도_영천시_캠핑장_현황_위경도_포함.csv')
temple_df = pd.read_csv('C:/Users/USER/Documents/test-project/ycproject/pjt03-yc/uj/data/영천_사찰정보_전화번호포함(최종).csv')

# 필요한 컬럼만 추출
tour_df = tour_df[['관광지명', '지역(광역)', '지역(기초)', '주소', '대분류', '중분류', '소분류', '위도', '경도']]
cafe_df = cafe_df[['업체명', '주소', '위도', '경도']]
event_df = event_df[['행사명', '행사내용', '장소명', '행사시작일자', '행사종료일자']]
camp_df = camp_df[['상호', '주소', '위도', '경도']]
temple_df = temple_df[['업체명', '주소', '전화번호', '위도', '경도']]

# 주소에서 읍/면/동 키워드 추출 함수
def extract_town(addr):
    if pd.isnull(addr):
        return ''
    m = re.search(r'([가-힣]+[읍면동])', addr)
    return m.group(1) if m else ''

# 각 데이터셋에 '읍면동' 컬럼 추가
tour_df['읍면동'] = tour_df['주소'].apply(extract_town)
cafe_df['읍면동'] = cafe_df['주소'].apply(extract_town)
camp_df['읍면동'] = camp_df['주소'].apply(extract_town)
temple_df['읍면동'] = temple_df['주소'].apply(extract_town)

# 병합(읍면동 기준, 관광지명 기준)
merged = tour_df.copy()

# 카페 정보 병합 (읍면동 기준)
merged = pd.merge(merged, cafe_df, on='읍면동', how='left', suffixes=('', '_카페'))

# 캠핑장 정보 병합 (읍면동 기준)
merged = pd.merge(merged, camp_df[['상호', '읍면동', '위도', '경도']], on='읍면동', how='left', suffixes=('', '_캠핑장'))

# 사찰 정보 병합 (읍면동 기준)
merged = pd.merge(merged, temple_df[['업체명', '읍면동', '전화번호', '위도', '경도']], on='읍면동', how='left', suffixes=('', '_사찰'))

# 행사/축제 병합 (관광지명과 장소명 기준)
merged = pd.merge(merged, event_df, left_on='관광지명', right_on='장소명', how='left')

# 결측치 처리 (예시: 빈 문자열로 채우기)
merged = merged.fillna('')

# 저장
merged.to_csv('영천_관광_통합데이터셋_읍면동기준.csv', index=False)
print(merged.head())

# 주소 기준으로 중복 제거
unique_tour = tour_df.drop_duplicates(subset=['주소'], keep='first').reset_index(drop=True)

# 파일로 저장
unique_tour.to_csv('영천_전체관광지_위경도_포함_주소기준_중복제거.csv', index=False, encoding='utf-8-sig')

# 결과 확인
print(unique_tour.head())
print(f"중복 제거 후 행 개수: {len(unique_tour)}")



# 읍면동 추출 함수
def extract_town(addr):
    if pd.isnull(addr):
        return ''
    m = re.search(r'([가-힣]+[읍면동])', addr)
    return m.group(1) if m else ''

# 각 테마별로 표준화
cafe_df['읍면동'] = cafe_df['주소'].apply(extract_town)
cafe_df['이름'] = cafe_df['업체명']
cafe_df['테마'] = '카페'
cafe_df = cafe_df[['이름', '주소', '위도', '경도', '읍면동', '테마']]

camp_df['읍면동'] = camp_df['주소'].apply(extract_town)
camp_df['이름'] = camp_df['상호']
camp_df['테마'] = '캠핑장'
camp_df = camp_df[['이름', '주소', '위도', '경도', '읍면동', '테마']]

temple_df['읍면동'] = temple_df['주소'].apply(extract_town)
temple_df['이름'] = temple_df['업체명']
temple_df['테마'] = '사찰'
temple_df = temple_df[['이름', '주소', '위도', '경도', '읍면동', '테마']]

event_df['이름'] = event_df['행사명']
event_df['테마'] = '행사/축제'
event_df['위도'] = ''  # 위경도 정보가 없다면 빈 칸
event_df['경도'] = ''
event_df['읍면동'] = event_df['장소명'].apply(extract_town)
event_df['주소'] = event_df['장소명']  # 장소명을 주소로 임시 활용
event_df = event_df[['이름', '주소', '위도', '경도', '읍면동', '테마']]

# 모두 합치기
all_theme = pd.concat([cafe_df, camp_df, temple_df, event_df], ignore_index=True)

# 주소 기준 중복 제거
all_theme = all_theme.drop_duplicates(subset=['이름', '주소'])

# 저장
all_theme.to_csv('영천_카페_캠핑장_사찰_행사_통합_테마기준.csv', index=False, encoding='utf-8-sig')
print(all_theme.head())
print(f"최종 행 개수: {len(all_theme)}")

# 테마별 통합
all_theme = pd.concat([cafe_df, camp_df, temple_df, event_df], ignore_index=True)

# 이름, 주소, 테마 기준 중복 제거(추천)
all_theme = all_theme.drop_duplicates(subset=['이름', '주소', '테마'], keep='first').reset_index(drop=True)

all_theme.to_csv('영천_카페_캠핑장_사찰_행사_통합_테마기준.csv', index=False, encoding='utf-8-sig')