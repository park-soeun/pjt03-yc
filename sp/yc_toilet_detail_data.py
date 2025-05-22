import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import plotly.figure_factory as ff

#  한글 깨짐 방지 설정 (Windows 환경 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 📁 영천시 공공화장실 데이터 로드 (파일 경로는 수정)
yc_df = pd.read_csv("data/yc_df.csv")  # 영천시 공공화장실
toilet_df = pd.read_csv("data/toilet.csv")  # 경북 전체 화장실

#읍면동별  공공 화장실 항목별 설치수 

# 항목들
cols = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
yc_df[cols] = yc_df[cols].astype(bool)

# 설치 항목 수 계산 및 요약 테이블
yc_df["설치된항목수"] = yc_df[cols].sum(axis=1)
summary_df = yc_df.groupby("읍면동명")[cols + ["설치된항목수"]].sum()
summary_df["화장실개수"] = yc_df.groupby("읍면동명").size()

#  항목별 설치 수만 추출 (정렬 포함)
stacked_data = summary_df[cols].astype(int)
stacked_data = stacked_data.loc[summary_df["설치된항목수"].sort_values(ascending=False).index]

#  항목별 색상 지정
colors = {
    "비상벨": "#4daf4a",         # 초록
    "CCTV": "#377eb8",           # 파랑
    "기저귀교환대": "#ff7f00",    # 주황
    "장애인화장실": "#984ea3",    # 보라
    "어린이대변기": "#e41a1c"     # 빨강
}

#  시각화: 누적 막대그래프 + 격자 + 라벨
plt.figure(figsize=(10, 7))
bottom = np.zeros(len(stacked_data))

for col in cols:
    bar = plt.bar(stacked_data.index, stacked_data[col], bottom=bottom, label=col, color=colors[col])
    
    # 값이 2 이상인 경우 텍스트 표시
    for i, value in enumerate(stacked_data[col]):
        if value >= 2:
            plt.text(i, bottom[i] + value / 2, f"{int(value)}", ha='center', va='center', fontsize=9, color='white')
    
    bottom += stacked_data[col]

plt.xticks(rotation=45, ha='right')
plt.ylabel("설치 수 (항목별)")
plt.title("읍면동별 공공화장실 항목별 설치 수 (누적 막대그래프)", fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.legend(title="항목")
plt.tight_layout()
plt.show()

# --------------------------------------------------
# 읍면동별 공공화장실 수 막대그래프

# 읍면동별 공공화장실 수 집계
toilet_count = yc_df["읍면동명"].value_counts().reset_index()
toilet_count.columns = ["읍면동명", "화장실수"]

# 내림차순 정렬
toilet_count_sorted = toilet_count.sort_values("화장실수", ascending=False)

# 시각화: 막대그래프
plt.figure(figsize=(10, 6))
bars = plt.bar(toilet_count_sorted["읍면동명"], toilet_count_sorted["화장실수"], color="cornflowerblue")

# 막대 위 수치 표시
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.3, f"{int(height)}", ha='center', fontsize=9)

# 그래프 설정
plt.xticks(rotation=45, ha='right')
plt.ylabel("공공화장실 수")
plt.title("영천시 읍면동별 공공화장실 수")
plt.tight_layout()
plt.show()

# ---------------------------------------------------
#데이터 프레임
cols = ["읍면동명", "비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
selected_df = yc_df[cols].copy()


summary_df = selected_df.groupby("읍면동명")[cols[1:]].sum().astype(int)
summary_df["총합"] = summary_df.sum(axis=1)
summary_sorted = summary_df.sort_values("총합", ascending=False)

print("📊 [총 설치 항목 수 기준] 읍면동별 공공시설 항목별 설치 수:")
print(summary_sorted)

# -------------------------------------------------------

# ————————————— 파일 로드 ——————————————
yc_df = pd.read_csv("data/yc_df.csv")     # 영천시 화장실
gb_df = pd.read_csv("data/kb_df.csv")     # 경북 전체 화장실
gb_pop = pd.read_csv("data/pop_2023.csv", skiprows=1)  # 경북 인구
yc_pop = pd.read_csv("data/pop_emd_2020.csv", skiprows=1)  # 영천 인구

import pandas as pd
import plotly.graph_objects as go

#  1. 시군구별 화장실 수 집계
city_counts = gb_df["시군구명"].value_counts().reset_index()
city_counts.columns = ["시군구", "화장실 수"]
city_counts = city_counts.sort_values("화장실 수", ascending=False)

#  2. 영천시 순위 및 개수
yc_rank = (city_counts["시군구"] == "영천시").idxmax() + 1
yc_toilet_count = city_counts.loc[city_counts["시군구"] == "영천시", "화장실 수"].values[0]


# 상위 5개 + 생략(...) + 영천시 추출
top5 = city_counts.head(5)
yc_row = city_counts[city_counts["시군구"] == "영천시"]
ellipsis_row = pd.DataFrame([["...", None]], columns=["시군구", "화장실 수"])



# 인구 데이터 병합
gb_pop_fixed = gb_pop.rename(columns={"행정구역별(읍면동)": "시군구"})
top_rows = pd.concat([top5, ellipsis_row, yc_row], ignore_index=True)
top_rows = pd.merge(top_rows, gb_pop_fixed, on="시군구", how="left")
top_rows = top_rows.rename(columns={"총인구 (명)": "총인구수"})

# 필요 컬럼만 정리
display_df = top_rows[["시군구", "화장실 수", "총인구수"]].copy()
display_df.columns = ["시군구", "화장실 수", "인구 수"]

# ⛏️ '...' 행의 수치형 열을 문자열로 바꿔줌
display_df.loc[display_df["시군구"] == "...", ["화장실 수", "인구 수"]] = "..."

# 색상 강조: 영천시는 주황, 나머지는 회색, '...'은 연회색
row_colors = []
for city in display_df["시군구"]:
    if city == "영천시":
        row_colors.append('#ffe0cc')
    elif city == "...":
        row_colors.append('#eeeeee')
    else:
        row_colors.append('#f9f9f9')

# Plotly Table 시각화
fig = go.Figure(data=[go.Table(
    header=dict(
        values=list(display_df.columns),
        fill_color='#1f3b70',
        font=dict(color='white', size=13, family='Arial'),
        align='center',
        height=32
    ),
    cells=dict(
        values=[display_df[col] for col in display_df.columns],
        fill_color=[row_colors],
        font=dict(color='black', size=12),
        align=['center', 'right', 'right'],
        height=28
    )
)])

fig.update_layout(
    title_text=f"영천시는 경북 공공화장실 수 {yc_rank}위 ({yc_toilet_count:,}개)",
    margin=dict(l=20, r=20, t=60, b=20),
    height=480
)

fig.show()

# --------------------------------------------------전처리-------------

import pandas as pd
import plotly.graph_objects as go

# 옵션 항목
features = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
yc_df["읍면동"] = yc_df["소재지도로명주소"].str.extract(r"영천시\s*([^\s]+)")
for f in features:
    yc_df[f] = yc_df[f].map({"Y": 1, "N": 0, 1: 1, 0: 0}).fillna(0).astype(int)

# 각 옵션, 화장실 수 집계
agg_opt = yc_df.groupby("읍면동")[features].sum()
agg_count = yc_df.groupby("읍면동").size().to_frame("화장실수")
agg_df = pd.concat([agg_count, agg_opt], axis=1)
agg_df["총옵션수"] = agg_opt.sum(axis=1)
agg_df["평균옵션수"] = (agg_df["총옵션수"] / agg_df["화장실수"]).round(1)
agg_df = agg_df.reset_index()

# 읍면동 전체 포함
all_emd = (
    yc_pop[["읍면동별(1)", "인구 (명)"]]
    .rename(columns={"읍면동별(1)": "읍면동", "인구 (명)": "총인구"})
    .query("읍면동 != '읍면동별(1)' and 읍면동 != '합계'")
    .assign(총인구=lambda df: pd.to_numeric(df["총인구"], errors="coerce"))["읍면동"]
    .unique()
)
df_all = pd.DataFrame({"읍면동": all_emd})
merged = pd.merge(df_all, agg_df, on="읍면동", how="left").fillna(0)

# 등급 분류
def calc_grade(row):
    if row["화장실수"] == 0:
        return "매우 취약"
    elif row["화장실수"] <= 2 and row["총옵션수"] < 5:
        return "취약"
    elif row["화장실수"] >= 3 and row["총옵션수"] < 8:
        return "보통"
    else:
        return "우수"

merged["등급"] = merged.apply(calc_grade, axis=1)

# 색상 맵핑
등급색 = {
    "우수": "#d4f4dd",
    "보통": "#fff5cc",
    "취약": "#ffd9d9",
    "매우 취약": "#ff9999"
}
# 1. 취약, 매우 취약 필터링 후 정렬
filtered = merged[merged["등급"].isin(["취약", "매우 취약"])].copy()
filtered = filtered.sort_values("화장실수").reset_index(drop=True)

row_colors = [등급색.get(g, "#f0f0f0") for g in filtered["등급"]]

# 3. Plotly 테이블 구성[2번째 시각화]
fig = go.Figure(data=[go.Table(
    header=dict(
        values=["읍면동", "화장실 수", "총 옵션 수", "등급"],
        fill_color='#7f0000',
        font=dict(color='white', size=13),
        align='center',
        height=32
    ),
    cells=dict(
        values=[
            filtered["읍면동"],
            filtered["화장실수"].astype(int),
            filtered["총옵션수"].astype(int),
            filtered["등급"]
        ],
        fill_color=[row_colors],
        font=dict(color='black', size=12),
        align=['center', 'right', 'right', 'center'],
        height=28
    )
)])

fig.update_layout(
    title_text="영천시 공공화장실 취약지역",
    margin=dict(l=20, r=20, t=60, b=20),
    height=460
)

fig.show()


agg_count['화장실수']