import requests
import pandas as pd
import time

KAKAO_API_KEY = "fe0c4ebbe878bf51f535c24615d3ca23"
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

search_targets = [
    {"query": "영천 관광지", "code": "AT4", "분류": "관광지"},
    {"query": "영천 캠핑장", "code": "OL7", "분류": "캠핑장"},
    {"query": "영천 체험", "code": "", "분류": "체험시설"},  # 키워드 검색
    {"query": "영천 문화시설", "code": "CT1", "분류": "문화시설"},
    {"query": "영천 전통시장", "code": "PM9", "분류": "전통시장"},
]

all_results = []

for target in search_targets:
    for page in range(1, 6):
        params = {
            "query": target["query"],
            "page": page,
            "size": 15
        }
        if target["code"]:
            params["category_group_code"] = target["code"]

        res = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params=params)
        data = res.json()

        if "documents" not in data or not data["documents"]:
            break

        for doc in data["documents"]:
            all_results.append({
                "이름": doc.get("place_name"),
                "카테고리": doc.get("category_name"),
                "분류": target["분류"],
                "분류코드": target["code"],
                "주소": doc.get("address_name"),
                "도로명주소": doc.get("road_address_name"),
                "전화번호": doc.get("phone"),
                "위도": doc.get("y"),
                "경도": doc.get("x"),
                "URL": doc.get("place_url")
            })

        time.sleep(0.2)

df = pd.DataFrame(all_results)
df.to_excel("영천_관광_통합장소.xlsx", index=False)


