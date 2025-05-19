import requests
import pandas as pd
from datetime import datetime

# 🔹 날짜/시간 설정
def get_recent_base_time():
    now = datetime.now()
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = now.hour
    recent = max([h for h in base_hours if h <= hour], default=23)
    return f"{recent:02d}00"

base_date = datetime.now().strftime('%Y%m%d')
base_time = get_recent_base_time()

# 🔹 격자 위치 불러오기
latlot = pd.read_excel('../data/latlot.xlsx')
yc_latlot = latlot[latlot['2단계'] == '영천시']
nx_ny_dict = dict(zip(
    yc_latlot['3단계'],
    zip(yc_latlot['격자 X'], yc_latlot['격자 Y'])
))

# 🔹 날씨 API URL
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
service_key = 'xRmhnrA+uKDxdqIjJLpprMj6n7fOpvL3Kqi9ssAcDI3gnBQm6RusMSVVedHHRIsFAAFFELJg1M7SK6/wZKecNQ=='

weather_data = []

# 🔹 읍면동별 날씨 수집
for town, (nx, ny) in nx_ny_dict.items():
    params = {
        'serviceKey': service_key,
        'numOfRows': '1000',
        'pageNo': '1',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data['response']['body']['items']['item']

        # TMP = 1시간 기온, REH = 습도
        tmp_list = [i for i in items if i['category'] == 'TMP']
        reh_list = [i for i in items if i['category'] == 'REH']
        pcp_list = [i for i in items if i['category'] == 'PCP']  
        sno_list = [i for i in items if i['category'] == 'SNO']  
        wsd_list = [i for i in items if i['category'] == 'WSD']  

        # 가장 가까운 시간 예보 추출
        now_hm = int(datetime.now().strftime('%H%M'))

        if all([tmp_list, reh_list, pcp_list, sno_list, wsd_list]):
            tmp_nearest = min(tmp_list, key=lambda x: abs(int(x['fcstTime']) - now_hm))
            reh_nearest = min(reh_list, key=lambda x: abs(int(x['fcstTime']) - now_hm))
            pcp_nearest = min(pcp_list, key=lambda x: abs(int(x['fcstTime']) - now_hm))
            sno_nearest = min(sno_list, key=lambda x: abs(int(x['fcstTime']) - now_hm))
            wsd_nearest = min(wsd_list, key=lambda x: abs(int(x['fcstTime']) - now_hm))

            weather_data.append({
                '읍면동': town,
                '격자_x': nx,
                '격자_y': ny,
                '기온': tmp_nearest['fcstValue'],
                '습도': reh_nearest['fcstValue'],
                '강수량': pcp_nearest['fcstValue'],
                '신적설': sno_nearest['fcstValue'],      
                '풍속': wsd_nearest['fcstValue'],        
                '예보시간': tmp_nearest['fcstTime']
            })
        else:
            print(f"[{town}] TMP 또는 REH 예보가 없음")

    except Exception as e:
        print(f"[{town}] API 요청/처리 실패: {e}")
        print("응답 원문:", response.text[:300])  # 일부만 출력

# 🔹 결과 DataFrame
df_weather = pd.DataFrame(weather_data)
