import requests
import pandas as pd

def fetch_lactation_rooms(api_key: str, zone_name: str = "경북") -> pd.DataFrame:
    url = "https://sooyusil.com/api/nursingRoomJSON.do"
    params = {
        "confirmApiKey": api_key,
        "zoneName": zone_name
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if "roomList" not in data:
        raise ValueError("응답에 roomList가 없습니다.")

    df = pd.json_normalize(data["roomList"])

    # 컬럼 리네이밍
    df = df.rename(columns={
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

    return df
