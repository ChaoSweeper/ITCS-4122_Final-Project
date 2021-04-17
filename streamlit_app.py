from pandas.core.frame import DataFrame
import streamlit as st
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


def load_data():
    df_data = pd.read_csv("Data/athlete_events.csv")
    df_regions = pd.read_csv("Data/noc_regions.csv")
    df = pd.merge(df_data, df_regions, on="NOC", how="left")
    return df


# Load data
df = load_data()

# Change app background
st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://wallpaperaccess.com/full/317308.jpg")
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.checkbox("Gender Representation"):
    male = df[df["Sex"] == "M"]["ID"].agg("count")
    female = df[df["Sex"] == "F"]["ID"].agg("count")

    fig1 = px.histogram(
        df, x="Year", color="Sex", title="Gender Representation 1896-2016"
    )
    st.plotly_chart(fig1)

    labels = ["Male Participants", "Female Participants"]
    values = [male, female]
    layout = go.Layout(title="Total Ratio Of Participants")
    fig2 = go.Figure(
        data=[go.Pie(labels=labels, values=values, hole=0.5)], layout=layout
    )
    st.plotly_chart(fig2)

if st.sidebar.checkbox(""):
    df1 = df.groupby(["region", "Event"])["Medal"].agg("count")
    df = pd.DataFrame(df1)
    df = df.pivot_table(index="Event", columns="region", values="Medal", aggfunc=sum)

    op1 = st.selectbox("First County", df.columns)
    op2 = st.selectbox("Second County", df.columns)

if st.sidebar.checkbox("Participants: Yearly Total"):
    df["Games"] = df["Games"].fillna("0")
    df = pd.DataFrame(df)
    games = df["Games"].value_counts()

    trace = go.Bar(
        x=games.index,
        y=games.values,
        marker=dict(color=games.values, colorscale="Plotly3", showscale=True),
    )
    layout = go.Layout(
        title="Athlete Participantion 1896-2016",
        yaxis=dict(title="Total Participants", zeroline=False, range=[1, 15000]),
    )
    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    fig.update_xaxes(categoryorder="category ascending")
    fig.update_layout(
        autosize=False,
        width=1100,
        height=800,
    )
    st.plotly_chart(fig)

if st.sidebar.checkbox("Participants: Country Total"):
    df["region"] = df["region"].fillna("0")
    df = pd.DataFrame(df)
    region = df["region"].value_counts()

    trace = go.Bar(
        x=region.index,
        y=region.values,
        marker=dict(color=region.values, colorscale="Plotly3", showscale=True),
    )
    layout = go.Layout(
        title="Country Participantion 1896-2016",
        yaxis=dict(title="Countries Total", zeroline=False, range=[1, 15000]),
    )
    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    fig.update_xaxes(categoryorder="category ascending")
    fig.update_layout(
        autosize=True,
        width=1100,
        height=800,
    )
    st.plotly_chart(fig)

if st.sidebar.checkbox("Medals Won: Country"):
    df_medal = df.groupby(["region", "Medal"])["ID"].agg("count").dropna()
    df = pd.DataFrame(df_medal).reset_index()
    gold = df[df["Medal"] == "Gold"]
    silver = df[df["Medal"] == "Silver"]
    bronze = df[df["Medal"] == "Bronze"]

    def draw_map(dataset, title, colorscale):
        trace = go.Choropleth(
            locations=dataset["region"],
            locationmode="country names",
            z=dataset["ID"],
            text=dataset["region"],
            autocolorscale=False,
            reversescale=False,
            colorscale=colorscale,
            marker=dict(line=dict(color="rgb(0,0,0)", width=0.7)),
            colorbar=dict(title="Medals", tickprefix=""),
        )
        data = [trace]
        layout = go.Layout(
            title=title,
            geo=dict(
                showframe=True,
                showlakes=False,
                showcoastlines=True,
                projection=dict(type="mercator"),
            ),
        )
        fig = dict(data=data, layout=layout)
        st.plotly_chart(fig)

    draw_map(gold, "Countries that Won Gold Medals", "OrRd")
    draw_map(silver, "Countries that Won Silver Medals", "Greys")
    draw_map(bronze, "Countries that Won Bronze Medals", "turbid")

if st.sidebar.checkbox("Medals Won: Events"):
    df_events = df.groupby(["Sport", "Medal"])["ID"].agg("count").dropna()
    df = pd.DataFrame(df_events).reset_index()
    gold = df[df["Medal"] == "Gold"]
    silver = df[df["Medal"] == "Silver"]
    bronze = df[df["Medal"] == "Bronze"]
    trace_gold = go.Bar(
        x=gold["Sport"],
        y=gold["ID"],
        name="Gold",
        marker=dict(
            color="gold",
            line=dict(color="black", width=1),
            opacity=0.5,
        ),
        text=gold["Sport"],
    )
    trace_silver = go.Bar(
        x=silver["Sport"],
        y=silver["ID"],
        name="Silver",
        marker=dict(
            color="Grey",
            line=dict(color="black", width=1),
            opacity=0.5,
        ),
        text=silver["Sport"],
    )
    trace_bronze = go.Bar(
        x=bronze["Sport"],
        y=bronze["ID"],
        name="Bronze",
        marker=dict(
            color="Brown",
            line=dict(color="black", width=1),
            opacity=0.5,
        ),
        text=bronze["Sport"],
    )

    data = [trace_gold, trace_silver, trace_bronze]
    layout = dict(
        title="Medals per Sporting Event",
        xaxis=dict(
            title="Sport",
            showticklabels=True,
            tickangle=45,
            tickfont=dict(size=8, color="white"),
        ),
        yaxis=dict(title="Total Medals"),
        hovermode="closest",
        barmode="stack",
        showlegend=False,
        width=1100,
        height=600,
    )
    fig = dict(data=data, layout=layout)
    st.plotly_chart(fig)