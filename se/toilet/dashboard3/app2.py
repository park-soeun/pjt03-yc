from shiny import App, ui
from shinywidgets import render_widget, output_widget
import plotly.express as px
import pandas as pd

# 전처리
df = pd.DataFrame({
    "시군구명": ["영천시", "포항시", "안동시"],
    "화장실수": [92, 130, 110]
})
df["색상"] = df["시군구명"].apply(lambda x: "#1f77b4" if x == "영천시" else "#cccccc")

# UI 구성
app_ui = ui.page_fluid(
    output_widget("plot_total_count_")
)

# 서버 구성
def server(input, output, session):
    def plot_total_count_():
        fig = px.bar(
            df,
            x="시군구명",
            y="화장실수",
            color="색상",
            color_discrete_map="identity"
        )
        fig.update_layout(showlegend=False, template="plotly_white")
        return fig

    output.plot_total_count_ = render_widget(plot_total_count_)

# 앱 실행
app = App(app_ui, server)
