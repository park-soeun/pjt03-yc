import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

# 필수 파라미터만 사용
sido = quote_plus("경상북도")
gungu = quote_plus("영천시")
ym = "202401"

service_key = '0OhBU7ZCGIobDVKDeBJDpmDRqK3IRNF6jlf%2FJB2diFAf%2FfR2czYO9A4UTGcsOwppV6W2HVUeho%2FFPwXoL6DwqA%3D%3D'

url = (
    f"http://openapi.tour.go.kr/openapi/service/TourismResourceStatsService/getPchrgTrrsrtVisitorList"
    f"?serviceKey={service_key}&YM={ym}&SIDO={sido}&GUNGU={gungu}"
)

response = requests.get(url)


# XML 파싱
root = ET.fromstring(response.content)

# item 단위로 반복
for item in root.iter("item"):
    res_nm = item.findtext("resNm")         # 관광지명
    forgn_cnt = item.findtext("forgnVstrCnt")  # 외국인 수
    natl_cnt = item.findtext("natlVstrCnt")    # 내국인 수
    print(f"[{res_nm}] 내국인: {natl_cnt}, 외국인: {forgn_cnt}")

def safe_int(text):
    return int(text) if text and text.isdigit() else 0

import pandas as pd
data = []
for item in root.iter("item"):
    res_nm = item.findtext("resNm")
    natl = safe_int(item.findtext("natlVstrCnt"))
    forgn = safe_int(item.findtext("forgnVstrCnt"))

    data.append({
        "관광지명": res_nm,
        "내국인": natl,
        "외국인": forgn,
        "총합": natl + forgn,
    })

df = pd.DataFrame(data)
print(df.head())


df