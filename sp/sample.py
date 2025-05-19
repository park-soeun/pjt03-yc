import seaborn as sns
from faicons import icon_svg

from shiny import App, reactive, render, ui
from shared import  df
app_ui = ui.page_navbar(
    ui.nav_panel(
        "[1] 테마별 관광 통합 지도",
        ui.page_sidebar(
            ui.sidebar(
                ui.input_slider("mass", "Mass", 2000, 6000, 6000),
                ui.input_checkbox_group(
                    "species",
                    "Species",
                    ["Adelie", "Gentoo", "Chinstrap"],
                    selected=["Adelie", "Gentoo", "Chinstrap"],
                ),
                title="Filter controls",
            ),
            ui.layout_column_wrap(
                ui.value_box(
                    "Number of penguins",
                    ui.output_text("count"),
                    showcase=icon_svg("earlybirds"),
                ),
                ui.value_box(
                    "Average bill length",
                    ui.output_text("bill_length"),
                    showcase=icon_svg("ruler-horizontal"),
                ),
                ui.value_box(
                    "Average bill depth",
                    ui.output_text("bill_depth"),
                    showcase=icon_svg("ruler-vertical"),
                ),
                fill=False,
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Bill length and depth"),
                    ui.output_plot("length_depth"),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("Penguin data"),
                    ui.output_data_frame("summary_statistics"),
                    full_screen=True,
                ),
            ),
            fillable=True,
        ),
    ),
    ui.nav_panel("[2] 축제/이벤트 캘린더(달력기반)", "Page B content"),
    ui.nav_panel("[3] 기후 예보 기반 대응 시뮬레이션", "Page C content"),
    ui.nav_panel("[4] 혼잡도/인기 스팟	유동인구 히트맵, 인기 명소 랭킹", "Page C content"),
    ui.nav_panel("[5] 내 일정 만들기", "Page C content"),
    title="8.5조",
    id="page",
)


def server(input, output, session):
    @reactive.calc
    def filtered_df():
        filt_df = df[df["species"].isin(input.species())]
        filt_df = filt_df.loc[filt_df["body_mass_g"] < input.mass()]
        return filt_df

    @render.text
    def count():
        return filtered_df().shape[0]

    @render.text
    def bill_length():
        return f"{filtered_df()['bill_length_mm'].mean():.1f} mm"

    @render.text
    def bill_depth():
        return f"{filtered_df()['bill_depth_mm'].mean():.1f} mm"

    @render.plot
    def length_depth():
        return sns.scatterplot(
            data=filtered_df(),
            x="bill_length_mm",
            y="bill_depth_mm",
            hue="species",
        )

    @render.data_frame
    def summary_statistics():
        cols = [
            "species",
            "island",
            "bill_length_mm",
            "bill_depth_mm",
            "body_mass_g",
        ]
        return render.DataGrid(filtered_df()[cols], filters=True)


app = App(app_ui, server)