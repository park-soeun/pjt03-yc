import plotly.express as px
import plotly.graph_objects as go


def plot_total_count(df1):
    df1['색상'] = df1['시군구명'].apply(
        lambda x: '#1f77b4' if x == '영천시' else '#cccccc'
    )

    # Plotly bar chart
    fig = px.bar(
        df1,
        x='시군구명',
        y='화장실수',
        title='경상북도 시군구별 공공화장실 수',
        labels={'시군구명': '시군구', '화장실수': '화장실 수'},
        color='색상',  # 색상 구분에 사용할 컬럼
        color_discrete_map='identity'  # HEX 색상 직접 적용
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
        title="경상북도 시군구별 인구 1만명당 공공화장실 수",
        labels={"시군구명": "시군구", "인구1만명당_화장실수": "1만명당 화장실 수"},
        color="색상",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_white"
    )
    return fig


def plot_density(df):
    fig = px.bar(
        df,
        x="시군구명",
        y="면적당_화장실수",
        title="경상북도 시군구별 면적당 공공화장실 수 (개/m²)",
        labels={"시군구명": "시군구", "면적당_화장실수": "면적당 화장실 수"},
        color="색상",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_white"
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
        yaxis_title="누적 설치 수"
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
        title="공공화장실 누적 설치 수 추이 (영천시 강조)",
        template="plotly_white",
        xaxis_title="설치연도",
        yaxis_title="누적 설치 수"
    )
    return fig



# 5
import plotly.express as px
import pandas as pd

def plot_open_type_pie(df: pd.DataFrame, region_name: str):
    count_df = df['개방시간유형'].value_counts().reset_index()
    count_df.columns = ['개방시간유형', '화장실수']

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
            '제한적 운영': '#ffbb78',
            '정보없음': '#d3d3d3'
        }
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(template='plotly_white')
    return fig

def plot_weekend_pie(df: pd.DataFrame, region_name: str):
    count_df = df['주말개방여부'].value_counts().reset_index()
    count_df.columns = ['주말개방여부', '화장실수']

    fig = px.pie(
        count_df,
        names='주말개방여부',
        values='화장실수',
        title=f'{region_name} 주말 개방 여부',
        hole=0.5,
        color='주말개방여부',
        color_discrete_map={
            '개방': '#1f77b4',
            '미개방': '#d62728',
            '불명확': '#cccccc'
        }
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(template='plotly_white')
    return fig
