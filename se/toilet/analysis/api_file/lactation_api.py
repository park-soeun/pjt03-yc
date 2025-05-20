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

    return df
