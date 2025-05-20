import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ✅ 한글 깨짐 방지 설정 (Windows 환경 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 📁 영천시 공공화장실 데이터 로드 (파일 경로는 수정)
df = pd.read_csv("yc_df.csv")



#읍면동별  공공 화장실 항목별 설치수 

# 항목들
cols = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
df[cols] = df[cols].astype(bool)

# 설치 항목 수 계산 및 요약 테이블
df["설치된항목수"] = df[cols].sum(axis=1)
summary_df = df.groupby("읍면동명")[cols + ["설치된항목수"]].sum()
summary_df["화장실개수"] = df.groupby("읍면동명").size()

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
toilet_count = df["읍면동명"].value_counts().reset_index()
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
selected_df = df[cols].copy()


summary_df = selected_df.groupby("읍면동명")[cols[1:]].sum().astype(int)
summary_df["총합"] = summary_df.sum(axis=1)
summary_sorted = summary_df.sort_values("총합", ascending=False)

print("📊 [총 설치 항목 수 기준] 읍면동별 공공시설 항목별 설치 수:")
print(summary_sorted)