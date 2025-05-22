import plotly.express as px
import plotly.graph_objects as go
import processing
import numpy as np


def plot_total_count(df1):
    df1['색상'] = df1['시군구명'].apply(
        lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
    )

    # Plotly bar chart
    fig = px.bar(
        df1,
        x='시군구명',
        y='화장실수',
        labels={'시군구명': '시군구', '화장실수': '화장실 수'},
        color='색상',  # 색상 구분에 사용할 컬럼
        color_discrete_map='identity',  # HEX 색상 직접 적용
        category_orders={'시군구명': df1['시군구명'].tolist()}  # ✅ x축 순서 고정

    )

    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,  # 범례 숨기기
        template='plotly_white'
    )

    return fig



# 2

def plot_per_10k(df):
    fig = px.bar(
        df,
        x="시군구명",
        y="인구1만명당_화장실수",
        labels={"시군구명": "시군구", "인구1만명당_화장실수": "1만명당 화장실 수"},
        color="색상",
        color_discrete_map="identity",
        category_orders={"시군구명": df["시군구명"].tolist()}  # ✅ 순서 고정!
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_white"
    )
    return fig


def plot_density(df):
    df["면적당_화장실수"] *= 1_000_000
    fig = px.bar(
        df,
        x="시군구명",
        y="면적당_화장실수",
        labels={"시군구명": "시군구", "면적당_화장실수": "면적당 화장실 수"},
        color="색상",
        color_discrete_map="identity",
        category_orders={"시군구명": df["시군구명"].tolist()} 
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_white",
        yaxis=dict(
            tickformat=".0f",        # ✅ 정수로
            exponentformat="none"   # ✅ 지수, 단위 축약 금지
        )
    )
    return fig

def plot_growth_rate(df):
    fig = px.line(
        df,
        x="설치연도",
        y="누적설치수",
        color="시군구명",
        title="시군구별 공공화장실 누적 설치 수 추이",
        markers=True
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="설치연도",
        yaxis_title="누적 설치 수",
    )
    return fig



# 4
def plot_growth_rate(df):
    fig = px.line(
        df,
        x="설치연도",
        y="누적설치수",
        color="시군구명",
        title="시군구별 공공화장실 누적 설치 수 추이",
        markers=True
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="설치연도",
        yaxis_title="누적 설치 수"
    )
    return fig


def plot_growth_comparison(df):
    fig = go.Figure()
    for region in df["시군구명"].unique():
        region_df = df[df["시군구명"] == region]
        color = "#1f77b4" if region == "영천시" else "#d3d3d3"
        fig.add_trace(go.Scatter(
            x=region_df["설치연도"],
            y=region_df["누적설치수"],
            mode="lines+markers",
            name=region,
            line=dict(color=color, width=4 if region == "영천시" else 1.5),
            marker=dict(size=6 if region == "영천시" else 4),
            opacity=1 if region == "영천시" else 0.5
        ))
    fig.update_layout(
        template="plotly_white",
        xaxis_title="설치연도",
        yaxis_title="누적 설치 수",
        xaxis=dict(range=[1960, df["설치연도"].max()])  # 🎯 여기 핵심
    )
    return fig


# 5
import plotly.express as px
import pandas as pd

def plot_open_type_pie(df: pd.DataFrame, region_name: str):
    count_df = df['개방시간유형'].value_counts().reset_index()
    count_df.columns = ['개방시간유형', '화장실수']

    exclude_labels = ['제한적 운영', '정보없음']
    count_df = count_df[~count_df['개방시간유형'].isin(exclude_labels)]

    fig = px.pie(
        count_df,
        names='개방시간유형',
        values='화장실수',
        title=f'{region_name} 공공화장실 개방시간 유형 분포',
        hole=0.5,
        color='개방시간유형',
        color_discrete_map={
            '24시간': '#1f77b4',
            '주간개방': '#aec7e8',
        }
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(template='plotly_white')
    return fig

def plot_weekend_pie(df: pd.DataFrame, region_name: str):
    count_df = df['주말개방여부'].value_counts().reset_index()
    count_df.columns = ['주말개방여부', '화장실수']

    # ✅ '미개방' 제외
    count_df = count_df[~count_df['주말개방여부'].isin(['미개방'])]

    fig = px.pie(
        count_df,
        names='주말개방여부',
        values='화장실수',
        title=f'{region_name} 주말 개방 여부',
        hole=0.5,
        color='주말개방여부',
        color_discrete_map={
            '개방': '#1f77b4',
            '불명확': '#cccccc'
        }
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(template='plotly_white')
    return fig



# ===============================
# 2페이지
# ===============================


def plot_infra_comparison(compare_df):
    fig = px.bar(
        compare_df,
        x='항목',
        y='설치율',
        color='지역',
        barmode='group',
        text='설치율',
        color_discrete_map={'영천시': '#1f77b4', '경북 평균': '#cccccc'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(template='plotly_white', yaxis_range=[0, 60])
    return fig


# 1
def plot_radar_install_compare(yeongcheon_rates, gyeongbuk_rates):
    labels = ['기저귀교환대', '어린이대변기', 'CCTV', '비상벨', '수유실']
    yeongcheon_values = yeongcheon_rates.tolist()
    gyeongbuk_values = gyeongbuk_rates.tolist()

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=yeongcheon_values,
        theta=labels,
        fill='toself',
        name='영천시',
        line=dict(color='#1f77b4')
    ))

    fig.add_trace(go.Scatterpolar(
        r=gyeongbuk_values,
        theta=labels,
        fill='toself',
        name='경북 평균',
        line=dict(color='gray')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 0.5])
        ),
        title="영천시 vs 경북 평균 (여성친화시설 설치율)",
        template="plotly_white"
    )

    return fig


# 2
def plot_grouped_bar(df_long):
    fig = go.Figure()

    항목리스트 = df_long['항목'].unique()

    for 항목 in 항목리스트:
        temp = df_long[df_long['항목'] == 항목]

        colors = temp['시군구명'].apply(
            lambda x: '#1f77b4' if x == '영천시' else '#d3d3d3'
        )

        fig.add_trace(go.Bar(
            x=temp['시군구명'],
            y=temp['설치율'],
            name=항목,
            marker_color=colors
        ))

    fig.update_layout(
        title='시군구별 여성친화 시설 설치율 (영천시 강조)',
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly_white'
    )

    return fig


# 3 비상벨

def plot_emergency_bell(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["시군구명"],
        y=df["비상벨설치율"],
        text=[f"{x:.0%}" for x in df["비상벨설치율"]],
        marker_color=df["색상"],
        textposition="outside",
        name="비상벨 설치율"
    ))

    fig.update_layout(
        xaxis_title="시군구",
        yaxis_title="설치율",
        template="plotly_white",
        yaxis_tickformat=".0%",
        xaxis_tickangle=-45
    )

    return fig



def plot_cctv(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["시군구명"],
        y=df["CCTV설치율"],
        text=[f"{x:.0%}" for x in df["CCTV설치율"]],
        marker_color=df["색상"],
        textposition="outside",
        name="CCTV 설치율"
    ))

    fig.update_layout(
        xaxis_title="시군구",
        yaxis_title="설치율",
        template="plotly_white",
        yaxis_tickformat=".0%",
        xaxis_tickangle=-45
    )

    return fig

# 기저귀 교환대

def plot_diaper(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["시군구명"],
        y=df["기저귀교환대설치율"],
        text=[f"{x:.0%}" for x in df["기저귀교환대설치율"]],
        marker_color=df["색상"],
        textposition="outside",
        name="기저귀 교환대 설치율"
    ))

    fig.update_layout(
        xaxis_title="시군구",
        yaxis_title="설치율",
        template="plotly_white",
        yaxis_tickformat=".0%",
        xaxis_tickangle=-45
    )

    return fig






# 수유실 6


def plot_lactation_type_pie(df):
    fig = px.pie(
        df,
        names="수유실유형_아빠이용",
        values="개수",
        title="경상북도 수유실 유형 + 아빠이용 여부 분포",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(template="plotly_white")
    return fig


# 어린이 변기

def plot_child_fixture_radar(yeongcheon, gyeongbuk_avg):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=yeongcheon.tolist(),
        theta=yeongcheon.index.tolist(),
        fill='toself',
        name='영천시',
        line=dict(color='#1f77b4')
    ))
    fig.add_trace(go.Scatterpolar(
        r=gyeongbuk_avg.tolist(),
        theta=gyeongbuk_avg.index.tolist(),
        fill='toself',
        name='경북 평균',
        line=dict(color='gray')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(yeongcheon.max(), gyeongbuk_avg.max()) * 1.1])),
        showlegend=True,
        template='plotly_white'
    )
    return fig


# ===
# 3페이지
# ===

def plot_stacked(yc_df, selected_emd):
    cols = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
    colors = {
        "비상벨": "#4daf4a",
        "CCTV": "#377eb8",
        "기저귀교환대": "#ff7f00",
        "장애인화장실": "#984ea3",
        "어린이대변기": "#e41a1c",
    }

    stacked_data = processing.get_stacked_data(yc_df, cols)
    emd_list = stacked_data.index.tolist()
    fig = go.Figure()
    bottom = np.zeros(len(stacked_data))

    for col in cols:
        values = stacked_data[col].values
        fig.add_trace(go.Bar(
            x=emd_list,
            y=values,
            name=col,
            marker_color=colors[col],
            offsetgroup=0,
            base=bottom,
            hovertemplate=f"{col}: %{{y}}<extra></extra>",
        ))
        bottom += values

    if selected_emd in emd_list:
        idx = emd_list.index(selected_emd)
        y_max = bottom[idx]
        fig.add_shape(
            type="rect",
            x0=idx - 0.4, x1=idx + 0.4,
            y0=0, y1=y_max,
            line=dict(color="gold", width=3),
        )

    fig.update_layout(
        barmode="stack",
        xaxis_title="읍면동",
        yaxis_title="설치 수 (항목별)",
        title="읍면동별 공공화장실 항목별 설치 수 (누적 그래프)",
        xaxis_tickangle=-45,
        template="plotly_white",
        legend_title="항목"
    )
    return fig
