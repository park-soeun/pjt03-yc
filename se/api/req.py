import requests
from urllib.parse import urlencode, quote_plus

# 인증키 (URL 인코딩 하지 않은 상태로 붙여주세요)
service_key = "xRmhnrA%2BuKDxdqIjJLpprMj6n7fOpvL3Kqi9ssAcDI3gnBQm6RusMSVVedHHRIsFAAFFELJg1M7SK6%2FwZKecNQ%3D%3D"

# 파라미터
params = {
    'serviceKey': service_key,
    'YM': '201201',                # 필수
    'SIDO': '부산광역시',           # 선택
    'GUNGU': '해운대구',           # 선택
    'RES_NM': '부산시립미술관'      # 선택
}

# URL 구성
base_url = "http://openapi.tour.go.kr/openapi/service/TourismResourceStatsService/getPchrgTrrsrtVisitorList"
response = requests.get(base_url, params=params)

# 응답 처리
if response.status_code == 200:
    print(response.text)  # XML 형태의 응답이 출력됩니다
else:
    print(f"에러 발생: {response.status_code}")
