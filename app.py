import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from pycaret.regression import *

st.cache()

# import the dateset and format it for
# use through this app
def load_data():
    df_data = pd.read_csv("Data/athlete_events.csv")
    df_regions = pd.read_csv("Data/noc_regions.csv")
    df = pd.merge(df_data, df_regions, on="NOC", how="left")
    return df

def predict_cache(test_data):
    rf_saved = load_model('rf_model2')
    predictions = predict_model(rf_saved, data = test_data)
    return predictions['Label']


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

# Create a title for the sidebar
st.sidebar.title("Menu")

# Area to display key information about the dataset
if st.sidebar.checkbox("Data Information"):
    st.header("Description")
    st.subheader("Context")
    st.write(
        "This dataset is a historical look at the Olympic Games from 1896 to 2016. "
        "This dataset was scraped from www.sports-reference.com by Kaggle user rgriffin. "
        "They made this dataset publicly available to everyone under a Public Domain license."
    )
    st.subheader("Content")
    st.write("This dataset has the following features: ")
    features_table = [
        "ID",
        "Name",
        "Sex",
        "Age",
        "height",
        "Weight",
        "Team",
        "NOC",
        "Games",
        "Year",
        "Season",
        "City",
        "Sport",
        "Event",
        "Medal",
        "Region",
        "Notes",
    ]
    st.write(features_table)
    st.subheader("Raw Data")
    raw = df.head(5)
    st.write(raw)

# Create the option to display charts that show the stats
# for gender representation for the last 120 years
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

# Create the option to display information about the
# yearly total of participants
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
        yaxis=dict(title="Total Participants", zeroline=False, range=[1, 14000]),
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

# Create the option to display information about the
# contry of orgion of participants
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

# Create the option to display information about the
# total of medals won by country
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

# Create the option to display information about the
# total of medals won by event
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
        showlegend=True,
        width=1100,
        height=600,
    )
    fig = dict(data=data, layout=layout)
    st.plotly_chart(fig)
    
if st.sidebar.checkbox("Predict medal type"):
    #st.write("1 = Gold, 2 = Silver,  3 = Bronze")
    st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">1 = Gold, 2 = Silver,  3 = Bronze</p>', unsafe_allow_html=True)
    col1, col2 = st.beta_columns(2)
    
    col1.header("Individual 1")
    inp_sex = col1.radio('Sex 1', ('female', 'male'), index=0)
    inp_age = col1.slider('Age 1', 13, 66, 35, step=1)
    inp_height = col1.slider('Height 1', 136, 223, step=1)
    inp_weight = col1.slider('Weight 1', 28, 182, step=1)
    inp_sport = col1.radio('Sport 1', ('Ice Hockey', 'Gymnastics', 'Alpine Skiing', 'Rowing', 'Football',
       'Fencing', 'Taekwondo', 'Athletics', 'Canoeing', 'Handball',
       'Water Polo', 'Wrestling', 'Sailing', 'Cycling', 'Hockey',
       'Figure Skating', 'Softball', 'Swimming', 'Boxing', 'Basketball',
       'Nordic Combined', 'Diving', 'Baseball', 'Volleyball',
       'Speed Skating', 'Cross Country Skiing', 'Bobsleigh',
       'Modern Pentathlon', 'Curling', 'Judo', 'Rugby Sevens', 'Tennis',
       'Rhythmic Gymnastics', 'Weightlifting', 'Equestrianism',
       'Badminton', 'Beach Volleyball', 'Ski Jumping', 'Shooting',
       'Short Track Speed Skating', 'Biathlon', 'Synchronized Swimming',
       'Freestyle Skiing', 'Triathlon', 'Luge', 'Table Tennis',
       'Snowboarding', 'Skeleton', 'Rugby', 'Archery', 'Tug-Of-War',
       'Trampolining', 'Lacrosse', 'Golf', 'Art Competitions'), index=0)
    inp_region = col1.radio('Region 1', ('Finland', 'Norway', 'Netherlands', 'Italy', 'Spain', 'Azerbaijan',
       'Russia', 'Belarus', 'France', 'Cameroon', 'USA', 'Hungary',
       'Australia', 'Iran', 'Canada', 'Pakistan', 'Uzbekistan',
       'Tajikistan', 'Japan', 'Ethiopia', 'Germany', 'Sweden', 'Turkey',
       'Bulgaria', 'Egypt', 'UK', 'Jordan', 'Romania', 'Switzerland',
       'Puerto Rico', 'Mexico', 'Ghana', 'Morocco', 'New Zealand',
       'Argentina', 'Cuba', 'Poland', 'Czech Republic', 'Nigeria',
       'Brazil', 'Lithuania', 'South Africa', 'Indonesia', 'Chile',
       'Ukraine', 'Greece', 'Uganda', 'Syria', 'Qatar', 'Kuwait',
       'Individual Olympic Athletes', 'Saudi Arabia',
       'United Arab Emirates', 'Croatia', 'Armenia', 'Serbia', 'Niger',
       'India', 'Algeria', 'Austria', 'Trinidad', 'Colombia', 'Botswana',
       'Tunisia', 'South Korea', 'North Korea', 'China', 'Denmark',
       'Uruguay', 'Guyana', 'Kazakhstan', 'Georgia', 'Kenya', 'Iceland',
       'Jamaica', 'Malaysia', 'Slovakia', 'Bahamas', 'Paraguay',
       'Montenegro', 'Ireland', 'Portugal', 'Guatemala', 'Luxembourg',
       'Belgium', 'Tanzania', 'Lebanon', 'Kyrgyzstan', 'Venezuela',
       'Thailand', 'Togo', 'Peru', 'Estonia', 'Slovenia', 'Haiti',
       'Taiwan', 'Zimbabwe', 'Mongolia', 'Moldova', 'Ivory Coast', 'Fiji',
       'Senegal', 'Dominican Republic', 'Philippines', 'Latvia',
       'Namibia', 'Israel', 'Liechtenstein', 'Bermuda', 'Vietnam',
       'Virgin Islands, US', 'Macedonia', 'Sudan', 'Bahrain', 'Grenada',
       'Sri Lanka', 'Mauritius', 'Kosovo', 'Cyprus', 'Panama', 'Zambia',
       'Mozambique', 'Suriname', 'Afghanistan', 'Burundi', 'Gabon',
       'Ecuador', 'Costa Rica', 'Djibouti', 'Eritrea', 'Barbados',
       'Tonga'), index=0)
    
    col2.header("Individual 2")
    inp_sex2 = col2.radio('Sex 2', ('female', 'male'), index=0)
    inp_age2 = col2.slider('Age 2', 13, 66, 35, step=1)
    inp_height2 = col2.slider('Height 2', 136, 223, step=1)
    inp_weight2 = col2.slider('Weight 2', 28, 182, step=1)
    inp_sport2 = col2.radio('Sport 2', ('Ice Hockey', 'Gymnastics', 'Alpine Skiing', 'Rowing', 'Football',
       'Fencing', 'Taekwondo', 'Athletics', 'Canoeing', 'Handball',
       'Water Polo', 'Wrestling', 'Sailing', 'Cycling', 'Hockey',
       'Figure Skating', 'Softball', 'Swimming', 'Boxing', 'Basketball',
       'Nordic Combined', 'Diving', 'Baseball', 'Volleyball',
       'Speed Skating', 'Cross Country Skiing', 'Bobsleigh',
       'Modern Pentathlon', 'Curling', 'Judo', 'Rugby Sevens', 'Tennis',
       'Rhythmic Gymnastics', 'Weightlifting', 'Equestrianism',
       'Badminton', 'Beach Volleyball', 'Ski Jumping', 'Shooting',
       'Short Track Speed Skating', 'Biathlon', 'Synchronized Swimming',
       'Freestyle Skiing', 'Triathlon', 'Luge', 'Table Tennis',
       'Snowboarding', 'Skeleton', 'Rugby', 'Archery', 'Tug-Of-War',
       'Trampolining', 'Lacrosse', 'Golf', 'Art Competitions'), index=0)
    inp_region2 = col2.radio('Region 2', ('Finland', 'Norway', 'Netherlands', 'Italy', 'Spain', 'Azerbaijan',
       'Russia', 'Belarus', 'France', 'Cameroon', 'USA', 'Hungary',
       'Australia', 'Iran', 'Canada', 'Pakistan', 'Uzbekistan',
       'Tajikistan', 'Japan', 'Ethiopia', 'Germany', 'Sweden', 'Turkey',
       'Bulgaria', 'Egypt', 'UK', 'Jordan', 'Romania', 'Switzerland',
       'Puerto Rico', 'Mexico', 'Ghana', 'Morocco', 'New Zealand',
       'Argentina', 'Cuba', 'Poland', 'Czech Republic', 'Nigeria',
       'Brazil', 'Lithuania', 'South Africa', 'Indonesia', 'Chile',
       'Ukraine', 'Greece', 'Uganda', 'Syria', 'Qatar', 'Kuwait',
       'Individual Olympic Athletes', 'Saudi Arabia',
       'United Arab Emirates', 'Croatia', 'Armenia', 'Serbia', 'Niger',
       'India', 'Algeria', 'Austria', 'Trinidad', 'Colombia', 'Botswana',
       'Tunisia', 'South Korea', 'North Korea', 'China', 'Denmark',
       'Uruguay', 'Guyana', 'Kazakhstan', 'Georgia', 'Kenya', 'Iceland',
       'Jamaica', 'Malaysia', 'Slovakia', 'Bahamas', 'Paraguay',
       'Montenegro', 'Ireland', 'Portugal', 'Guatemala', 'Luxembourg',
       'Belgium', 'Tanzania', 'Lebanon', 'Kyrgyzstan', 'Venezuela',
       'Thailand', 'Togo', 'Peru', 'Estonia', 'Slovenia', 'Haiti',
       'Taiwan', 'Zimbabwe', 'Mongolia', 'Moldova', 'Ivory Coast', 'Fiji',
       'Senegal', 'Dominican Republic', 'Philippines', 'Latvia',
       'Namibia', 'Israel', 'Liechtenstein', 'Bermuda', 'Vietnam',
       'Virgin Islands, US', 'Macedonia', 'Sudan', 'Bahrain', 'Grenada',
       'Sri Lanka', 'Mauritius', 'Kosovo', 'Cyprus', 'Panama', 'Zambia',
       'Mozambique', 'Suriname', 'Afghanistan', 'Burundi', 'Gabon',
       'Ecuador', 'Costa Rica', 'Djibouti', 'Eritrea', 'Barbados',
       'Tonga'), index=0)
    
    test_data = pd.DataFrame({'Sex': [inp_sex], 
                          'Age': [inp_age], 
                          'Height': [inp_height], 
                          'Weight' : [inp_weight], 
                          'Sport': [inp_sport], 
                          'region': [inp_region]})
    
    test_data2 = pd.DataFrame({'Sex': [inp_sex2], 
                          'Age': [inp_age2], 
                          'Height': [inp_height2], 
                          'Weight' : [inp_weight2], 
                          'Sport': [inp_sport2], 
                          'region': [inp_region2]})
    # Show prediction
    col1.write('Medal = %0.2f'%predict_cache(test_data)[0])
    col2.write('Medal = %0.2f'%predict_cache(test_data2)[0])
              
    

        
