from shiny import App, ui, render
from htmltools import HTML
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
import os
from matplotlib.colors import LogNorm, to_hex
import matplotlib

# ----------- 폰트 한글 깨짐 방지 (Mac) -------------
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
# ----------------------------------------------------


static_dir = {"C:/Users/USER/Desktop/my_blog/my_blog/project/pjt03-yc/sp/shiny_DB"}
s_dir = "C:/Users/USER/Desktop/my_blog/my_blog/project/pjt03-yc/sp/shiny_DB"

os.chdir("C:/Users/USER/Desktop/my_blog/my_blog/project/pjt03-yc/sp/shiny_DB")

# 데이터 로딩 (경로 수정 필요)
yc_df = pd.read_csv("data/yc_df.csv")
toilet_df = pd.read_csv("data/toilet.csv")
gb_df = pd.read_csv("data/kb_df.csv")
gb_pop = pd.read_csv("data/pop_2023.csv", skiprows=1)
yc_pop = pd.read_csv("data/pop_emd_2020.csv", skiprows=1)

# 지도 파일 데이터
GDF_2KM_PATH = "./2km_grid.geojson"
BOUNDARY_PATH = "./yeongcheon_boundary.geojson"
COORD_CSV_PATH = "./yc_address_coords.csv"
gdf_2km = gpd.read_file(GDF_2KM_PATH)
gdf_boundary = gpd.read_file(BOUNDARY_PATH)
coord_df = pd.read_csv(COORD_CSV_PATH)
geojson_data = gdf_boundary.__geo_interface__

emd_list = sorted(yc_df["읍면동명"].dropna().unique().tolist())

# ---------------- UI 정의 -----------------
app_ui = ui.page_fluid(
    ui.panel_title("영천시 공공화장실·지도 대시보드"),
    ui.layout_columns(
        ui.card(
            ui.input_select("emd", "읍면동 선택", choices=emd_list),
            ui.output_plot("plot_stacked"),
            ui.output_plot("plot_count"),
        ),
        ui.card(
            ui.output_ui("updated_map"),
            ui.output_ui("plot_summary"),
            ui.output_ui("plot_rank"),
            ui.output_ui("plot_vulnerable"),
        ),
    ),
)


# ----------- 함수: 누적 그래프 데이터 --------------
def get_stacked_data(yc_df, cols):
    temp = yc_df.copy()
    temp[cols] = temp[cols].astype(bool)
    temp["설치된항목수"] = temp[cols].sum(axis=1)
    summary_df = temp.groupby("읍면동명")[cols + ["설치된항목수"]].sum()
    summary_df["화장실개수"] = temp.groupby("읍면동명").size()
    stacked_data = summary_df[cols].astype(int)
    stacked_data = stacked_data.loc[
        summary_df["설치된항목수"].sort_values(ascending=False).index
    ]
    return stacked_data


# ---------------- 서버 정의 -----------------
def server(input, output, session):
    @output
    @render.plot
    def plot_stacked():
        selected = input.emd()
        cols = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
        colors = {
            "비상벨": "#4daf4a",
            "CCTV": "#377eb8",
            "기저귀교환대": "#ff7f00",
            "장애인화장실": "#984ea3",
            "어린이대변기": "#e41a1c",
        }
        stacked_data = get_stacked_data(yc_df, cols)
        plt.figure(figsize=(10, 7))
        bottom = np.zeros(len(stacked_data))
        for col in cols:
            barlist = plt.bar(
                stacked_data.index,
                stacked_data[col],
                bottom=bottom,
                label=col,
                color=colors[col],
            )
            for i, emd in enumerate(stacked_data.index):
                if emd == selected:
                    barlist[i].set_color("gold")
                    barlist[i].set_edgecolor("black")
                    barlist[i].set_linewidth(2)
            bottom += stacked_data[col]
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("설치 수 (항목별)")
        plt.title("읍면동별 공공화장실 항목별 설치 수 (누적 그래프)", fontsize=14)
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.legend(title="항목")
        plt.tight_layout()
        return plt.gcf()

    @output
    @render.plot
    def plot_count():
        selected = input.emd()
        toilet_count = yc_df["읍면동명"].value_counts().reset_index()
        toilet_count.columns = ["읍면동명", "화장실수"]
        toilet_count_sorted = toilet_count.sort_values("화장실수", ascending=False)
        bars = plt.bar(
            toilet_count_sorted["읍면동명"],
            toilet_count_sorted["화장실수"],
            color="cornflowerblue",
        )
        for i, emd in enumerate(toilet_count_sorted["읍면동명"]):
            if emd == selected:
                bars[i].set_color("gold")
                bars[i].set_edgecolor("red")
                bars[i].set_linewidth(2)
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.3,
                f"{int(height)}",
                ha="center",
                fontsize=9,
            )
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("공공화장실 수")
        plt.title("영천시 읍면동별 공공화장실 수")
        plt.tight_layout()
        return plt.gcf()

    @output
    @render.ui
    def updated_map():
        # 선택된 읍면동 지도 하이라이트
        selected = input.emd()
        m = folium.Map(
            location=[35.968, 128.941], zoom_start=13, tiles="CartoDB dark_matter"
        )

        # 히트맵 레이어
        vmin = max(gdf_2km["val"][gdf_2km["val"] > 0].min(), 1)
        vmax = gdf_2km["val"].max()
        norm = LogNorm(vmin=vmin, vmax=vmax)
        cmap = matplotlib.colormaps["RdYlGn_r"]

        def get_color(v):
            return "#ffffff" if v <= 0 else to_hex(cmap(norm(v)))

        def get_opacity(v):
            return 0.55 if v > 0 else 0.01

        heat_layer = folium.FeatureGroup(name="2km 격자 히트맵")
        for _, row in gdf_2km.iterrows():
            val = row["val"]
            folium.GeoJson(
                row.geometry,
                style_function=lambda feat, v=val: {
                    "fillColor": get_color(v),
                    "color": "gray",
                    "weight": 0.3,
                    "fillOpacity": get_opacity(v),
                },
                tooltip=folium.Tooltip(
                    f"인구: {val:.0f}<br>읍면동: {row.get('EMD_KOR_NM', '없음')}",
                    sticky=True,
                ),
            ).add_to(heat_layer)
        heat_layer.add_to(m)

        # 마커 클러스터 레이어
        marker_layer = folium.FeatureGroup(name="주소 마커 클러스터")
        cluster = MarkerCluster()
        for _, row in coord_df.iterrows():
            lat, lon, addr = row["lat"], row["lon"], row["address"]
            folium.Marker(
                location=[lat, lon],
                tooltip=addr,
                popup=addr,
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(cluster)
        cluster.add_to(marker_layer)
        marker_layer.add_to(m)

        # 경계선
        folium.GeoJson(
            geojson_data,
            name="영천시 경계",
            style_function=lambda f: {"color": "yellow", "weight": 2, "fill": False},
            tooltip=folium.GeoJsonTooltip(fields=["EMD_KOR_NM"]),
        ).add_to(m)

        # 선택 읍면동 하이라이트
        def style_fn(feature):
            emd = feature["properties"].get("EMD_KOR_NM", "")
            is_selected = emd == selected
            return {
                "fillColor": "red" if is_selected else "transparent",
                "color": "black" if is_selected else "transparent",
                "weight": 4 if is_selected else 0,
                "fillOpacity": 0.5 if is_selected else 0,
            }

        selected_bounds = (
            gdf_boundary[gdf_boundary["EMD_KOR_NM"] == selected]
            .to_crs(4326)
            .geometry.values[0]
            .bounds
        )
        padding = 0.01
        m.fit_bounds(
            [
                [selected_bounds[1] - padding, selected_bounds[0] - padding],
                [selected_bounds[3] + padding, selected_bounds[2] + padding],
            ]
        )

        folium.GeoJson(
            geojson_data,
            name="선택 읍면동",
            style_function=style_fn,
            tooltip=folium.GeoJsonTooltip(
                fields=["EMD_KOR_NM"],
                sticky=False,
                permanent=True,
                direction="center",
                opacity=0.9,
            ),
        ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)
        return HTML(m.get_root().render())

    @output
    @render.ui
    def plot_summary():
        cols = [
            "읍면동명",
            "비상벨",
            "CCTV",
            "기저귀교환대",
            "장애인화장실",
            "어린이대변기",
        ]
        selected = input.emd()
        selected_df = yc_df[cols].copy()
        summary_df = selected_df.groupby("읍면동명")[cols[1:]].sum().astype(int)
        summary_df["총합"] = summary_df.sum(axis=1)
        summary_sorted = summary_df.sort_values("총합", ascending=False).reset_index()

        def _highlight(row):
            if row["읍면동명"] == selected:
                return [f"background-color: gold"] * len(row)
            else:
                return ["" for _ in row]

        html = summary_sorted.style.apply(_highlight, axis=1).to_html()
        return HTML(html)

    @output
    @render.ui
    def plot_rank():
        selected = input.emd()
        city_counts = gb_df["시군구명"].value_counts().reset_index()
        city_counts.columns = ["시군구", "화장실 수"]
        city_counts = city_counts.sort_values("화장실 수", ascending=False)
        yc_rank = (city_counts["시군구"] == "영천시").idxmax() + 1
        yc_toilet_count = city_counts.loc[
            city_counts["시군구"] == "영천시", "화장실 수"
        ].values[0]
        top5 = city_counts.head(5)
        yc_row = city_counts[city_counts["시군구"] == "영천시"]
        top5_plus_yc = (
            pd.concat([top5, yc_row]).drop_duplicates().reset_index(drop=True)
        )
        gb_pop_fixed = gb_pop.rename(columns={"행정구역별(읍면동)": "시군구"})
        top5_plus_yc = pd.merge(top5_plus_yc, gb_pop_fixed, on="시군구", how="left")
        top5_plus_yc = top5_plus_yc.rename(columns={"총인구 (명)": "총인구수"})
        display_df = top5_plus_yc[["시군구", "화장실 수", "총인구수"]].copy()
        display_df.columns = ["시군구", "화장실 수", "인구 수"]

        row_colors = [
            "#ffe0cc" if city == "영천시" else "#f9f9f9"
            for city in display_df["시군구"]
        ]
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(display_df.columns),
                        fill_color="#1f3b70",
                        font=dict(color="white", size=13, family="Arial"),
                        align="center",
                        height=32,
                    ),
                    cells=dict(
                        values=[display_df[col] for col in display_df.columns],
                        fill_color=[row_colors],
                        font=dict(color="black", size=12),
                        align=["center", "right", "right"],
                        height=28,
                    ),
                )
            ]
        )
        fig.update_layout(
            title_text=f"영천시는 경북 공공화장실 수 {yc_rank}위 ({yc_toilet_count:,}개)",
            margin=dict(l=20, r=20, t=60, b=20),
            height=430,
        )
        return HTML(fig.to_html(include_plotlyjs="cdn"))

    @output
    @render.ui
    def plot_vulnerable():
        selected = input.emd()
        features = ["비상벨", "CCTV", "기저귀교환대", "장애인화장실", "어린이대변기"]
        temp = yc_df.copy()
        temp["읍면동"] = temp["소재지도로명주소"].str.extract(r"영천시\s*([^\s]+)")
        for f in features:
            temp[f] = temp[f].map({"Y": 1, "N": 0, 1: 1, 0: 0}).fillna(0).astype(int)
        agg_opt = temp.groupby("읍면동")[features].sum()
        agg_count = temp.groupby("읍면동").size().to_frame("화장실수")
        agg_df = pd.concat([agg_count, agg_opt], axis=1)
        agg_df["총옵션수"] = agg_opt.sum(axis=1)
        agg_df["평균옵션수"] = (agg_df["총옵션수"] / agg_df["화장실수"]).round(1)
        agg_df = agg_df.reset_index()

        all_emd = (
            yc_pop[["읍면동별(1)", "인구 (명)"]]
            .rename(columns={"읍면동별(1)": "읍면동", "인구 (명)": "총인구"})
            .query("읍면동 != '읍면동별(1)' and 읍면동 != '합계'")
            .assign(총인구=lambda df: pd.to_numeric(df["총인구"], errors="coerce"))[
                "읍면동"
            ]
            .unique()
        )
        df_all = pd.DataFrame({"읍면동": all_emd})
        merged = pd.merge(df_all, agg_df, on="읍면동", how="left").fillna(0)

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
        등급색 = {
            "우수": "#d4f4dd",
            "보통": "#fff5cc",
            "취약": "#ffd9d9",
            "매우 취약": "#ff9999",
        }
        filtered = merged[merged["등급"].isin(["취약", "매우 취약"])].copy()
        filtered = filtered.sort_values("화장실수").reset_index(drop=True)
        row_colors = [
            "#ffe066" if emd == selected else 등급색.get(g, "#f0f0f0")
            for emd, g in zip(filtered["읍면동"], filtered["등급"])
        ]
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["읍면동", "화장실 수", "총 옵션 수", "등급"],
                        fill_color="#7f0000",
                        font=dict(color="white", size=13),
                        align="center",
                        height=32,
                    ),
                    cells=dict(
                        values=[
                            filtered["읍면동"],
                            filtered["화장실수"].astype(int),
                            filtered["총옵션수"].astype(int),
                            filtered["등급"],
                        ],
                        fill_color=[row_colors],
                        font=dict(color="black", size=12),
                        align=["center", "right", "right", "center"],
                        height=28,
                    ),
                )
            ]
        )
        fig.update_layout(
            title_text="영천시 공공화장실 취약지역",
            margin=dict(l=20, r=20, t=60, b=20),
            height=460,
        )
        return HTML(fig.to_html(include_plotlyjs="cdn"))


# 앱 실행
app = App(app_ui, server, static_assets=s_dir)
