import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")


# =========================================================
# 데이터 불러오기
# =========================================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 여러 장르가 | 로 연결되어 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


df = load_data()


# =========================================================
# 1. 장르별 영화 편수 - 도넛 그래프
# =========================================================
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]


fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig.update_layout(
    legend_title="장르",
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "1번 그래프 설명",
    placeholder="예: 가장 많은 영화가 속한 장르와 그 비율을 알 수 있다.",
    label_visibility="collapsed",
    key="explanation_1"
)


# =========================================================
# 2. 장르 안에 영화가 들어 있는 트리맵
# =========================================================
st.header("2. 장르 안에 들어 있는 영화")

treemap_data = df.dropna(
    subset=["genre", "movieNm", "total_audi"]
).copy()

fig_treemap = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객"
)

fig_treemap.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig_treemap.update_layout(
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_treemap,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "2번 그래프 설명",
    placeholder="예: 같은 장르 안에서도 총 관객이 많은 영화와 적은 영화를 비교할 수 있다.",
    label_visibility="collapsed",
    key="explanation_2"
)


# =========================================================
# 3. 총 관객수 히스토그램
# =========================================================
st.header("3. 영화별 총 관객수 분포")

hist_data = df.dropna(
    subset=["total_audi"]
).copy()

# 20개 구간으로 나누기
hist_data["관객수_구간"] = pd.cut(
    hist_data["total_audi"],
    bins=20,
    include_lowest=True
)

bin_counts = (
    hist_data["관객수_구간"]
    .value_counts()
    .sort_index()
)

# 가장 많은 영화가 들어 있는 구간
most_common_bin = bin_counts.idxmax()

bin_start = int(most_common_bin.left)
bin_end = int(most_common_bin.right)

# 가장 관객이 많은 영화
max_audience_row = hist_data.loc[
    hist_data["total_audi"].idxmax()
]

max_movie_name = max_audience_row["movieNm"]
max_audience = int(max_audience_row["total_audi"])


fig_hist = px.histogram(
    hist_data,
    x="total_audi",
    nbins=20,
    title="총 관객수 분포",
    labels={
        "total_audi": "총 관객수"
    }
)

fig_hist.update_traces(
    hovertemplate=(
        "총 관객수 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig_hist.update_layout(
    xaxis_title="총 관객수",
    yaxis_title="영화 편수",
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.write(
    f"📊 **대부분의 영화가 몰려 있는 구간:** "
    f"{bin_start:,}명 ~ {bin_end:,}명"
)

st.write(
    f"🎬 **가장 관객이 많은 영화:** "
    f"{max_movie_name} — {max_audience:,}명"
)


# =========================================================
# 4. 개봉일 스크린수와 총 관객의 관계 - 산점도
# =========================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계")

scatter_data = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "movieNm",
        "genre"
    ]
).copy()

scatter_data["first_scrn"] = pd.to_numeric(
    scatter_data["first_scrn"],
    errors="coerce"
)

scatter_data["total_audi"] = pd.to_numeric(
    scatter_data["total_audi"],
    errors="coerce"
)

scatter_data = scatter_data.dropna(
    subset=["first_scrn", "total_audi"]
)


fig_scatter = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre": "장르"
    },
    opacity=0.7
)

fig_scatter.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "4번 그래프 설명",
    placeholder="예: 개봉일 스크린수와 총 관객수 사이의 관계를 영화별로 비교할 수 있다.",
    label_visibility="collapsed",
    key="explanation_4"
)


# =========================================================
# 5. 장르별 총 관객수 박스플롯
# =========================================================
st.header("5. 장르별 총 관객수 분포")

boxplot_data = df.dropna(
    subset=["genre", "total_audi"]
).copy()

# 장르별 영화 편수
genre_movie_counts = (
    boxplot_data["genre"]
    .value_counts()
)

# 영화가 10편 이상인 장르만 선택
selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

boxplot_data = boxplot_data[
    boxplot_data["genre"].isin(selected_genres)
]


fig_box = px.box(
    boxplot_data,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    custom_data=["movieNm"],
    title="영화가 10편 이상인 장르의 총 관객수 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객수"
    }
)

fig_box.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수",
    showlegend=False,
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_box,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "5번 그래프 설명",
    placeholder="예: 영화가 많은 장르끼리 총 관객수의 분포와 차이를 비교할 수 있다.",
    label_visibility="collapsed",
    key="explanation_5"
)


# =========================================================
# 6. 버블 차트
# =========================================================
st.header("6. 개봉일 스크린수와 총 관객의 관계 — 첫 주 관객수 크기")

bubble_data = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "genre"
    ]
).copy()

for column in [
    "first_scrn",
    "total_audi",
    "first_week_audi"
]:
    bubble_data[column] = pd.to_numeric(
        bubble_data[column],
        errors="coerce"
    )

bubble_data = bubble_data.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

# 음수 값 제거
bubble_data = bubble_data[
    (bubble_data["first_scrn"] >= 0) &
    (bubble_data["total_audi"] >= 0) &
    (bubble_data["first_week_audi"] >= 0)
]


fig_bubble = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계 — 첫 주 관객수 크기",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "first_week_audi": "첫 주 관객수",
        "genre": "장르"
    },
    size_max=50,
    opacity=0.65
)

fig_bubble.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객수: %{y:,.0f}명<br>"
        "첫 주 관객수: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)

fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_bubble,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "6번 그래프 설명",
    placeholder="예: 개봉일 스크린수와 총 관객수의 관계에 첫 주 관객 규모까지 함께 비교할 수 있다.",
    label_visibility="collapsed",
    key="explanation_6"
)


# =========================================================
# 7. 제작 국가 → 장르 선버스트
# =========================================================
st.header("7. 제작 국가와 장르별 영화 구성")

sunburst_data = df.dropna(
    subset=["nation", "genre"]
).copy()

# 빈 값 제거
sunburst_data = sunburst_data[
    (sunburst_data["nation"].astype(str).str.strip() != "") &
    (sunburst_data["genre"].astype(str).str.strip() != "")
]

fig_sunburst = px.sunburst(
    sunburst_data,
    path=["nation", "genre"],
    title="제작 국가 → 장르별 영화 구성"
)

fig_sunburst.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig_sunburst.update_layout(
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_sunburst,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "7번 그래프 설명",
    placeholder="예: 제작 국가별로 어떤 장르의 영화가 많이 만들어졌는지 비교할 수 있다.",
    label_visibility="collapsed",
    key="explanation_7"
)


# =========================================================
# 8. 10위권 체류 기간과 총 관객의 관계
# =========================================================
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

scatter_top10_data = df.dropna(
    subset=[
        "days_in_top10",
        "total_audi",
        "movieNm"
    ]
).copy()

scatter_top10_data["days_in_top10"] = pd.to_numeric(
    scatter_top10_data["days_in_top10"],
    errors="coerce"
)

scatter_top10_data["total_audi"] = pd.to_numeric(
    scatter_top10_data["total_audi"],
    errors="coerce"
)

scatter_top10_data = scatter_top10_data.dropna(
    subset=[
        "days_in_top10",
        "total_audi"
    ]
)


fig_top10 = px.scatter(
    scatter_top10_data,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={
        "days_in_top10": "10위권에 머문 날수",
        "total_audi": "총 관객수"
    },
    opacity=0.7
)

fig_top10.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "10위권에 머문 날수: %{x:,.0f}일<br>"
        "총 관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_top10.update_layout(
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객수",
    margin=dict(t=70, b=20, l=20, r=20)
)

st.plotly_chart(
    fig_top10,
    use_container_width=True
)

st.divider()
st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "8번 그래프 설명",
    placeholder="예: 10위권에 머문 날수와 총 관객수 사이의 관계를 영화별로 살펴볼 수 있다.",
    label_visibility="collapsed",
    key="explanation_8"
)
