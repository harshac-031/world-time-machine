import streamlit as st
import pandas as pd
import plotly.express as px

st.title("World Time Machine: Paint the Planet with Data")
st.write("A **choropleth map** colours whole countries by a number. Travel from 1952 to 2022 "
         "and watch the world change. Grey countries have no data.")

# Step 1: load real country data (a file that comes with this app)
df = pd.read_csv("world_data.csv")
# what each number means, in plain words: (short phrase, label for the chart)
plain = {
    "Life expectancy (years)": ("the number of years a newborn baby could expect to live", "Years a newborn baby could expect to live"),
    "Money per person (GDP, US dollars)": ("the yearly money earned by the average person (US dollars)", "Money earned per person in a year (US dollars)"),
    "Population (people)": ("the number of people living", "Number of people living there"),
}
indicators = list(plain)

# Step 2: the student's controls
col = st.selectbox("What should the map show?", indicators)
st.caption(f"This number means: {plain[col][0]}.")
year = st.slider("Which year?", 1952, 2022, 2022)
style = st.radio("Colour style", ["Smooth colours", "5 equal-size groups"], horizontal=True)
data = df[df["Year"] == year].copy()

# Step 3: paint the map
if style == "Smooth colours":
    fig = px.choropleth(data, locations="Code", color=col, hover_name="Country", color_continuous_scale="Viridis")
else:
    labels = ["Lowest 20%", "Low", "Middle", "High", "Highest 20%"]
    data["Group"] = pd.qcut(data[col], 5, labels=labels)
    fig = px.choropleth(data, locations="Code", color="Group", hover_name="Country",
                        category_orders={"Group": labels}, color_discrete_sequence=px.colors.sequential.Viridis)
fig.update_layout(title=f"{plain[col][1]}, in the year {year}", margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(fig)
st.caption("Try Population with smooth colours, then switch to 5 groups. Which map tells the fairer story?")

# Step 4: who is on top and who is at the bottom?
top, bottom = st.columns(2)
top.write(f"**Top 5 countries in {year}**")
top.dataframe(data.nlargest(5, col)[["Country", col]], hide_index=True)
bottom.write(f"**Bottom 5 countries in {year}**")
bottom.dataframe(data.nsmallest(5, col)[["Country", col]], hide_index=True)

# Step 5: YOUR country's story compared with the world
st.subheader("Your country's story")
countries = sorted(df["Country"].unique())
country = st.selectbox("Pick your country (or any country you are curious about)", countries, index=None, placeholder="Choose a country")
if country is None:
    st.stop()                                   # wait until the student chooses
story = pd.DataFrame({country: df[df["Country"] == country].set_index("Year")[col],
                      "World average": df.groupby("Year")[col].mean()}).reset_index()
fig2 = px.line(story, x="Year", y=[country, "World average"],
               labels={"value": plain[col][1], "variable": "", "Year": "Calendar year"},
               title=f"{country} compared with the world average")
fig2.update_xaxes(tickformat="d")
st.plotly_chart(fig2)

mine = story[country].dropna()
if mine.empty:
    st.warning(f"We have no data on {plain[col][0]} for {country}. Try another country!")
else:
    st.write(f"In **{int(story.loc[mine.index[0], 'Year'])}**, {plain[col][0]} in {country} was **{mine.iloc[0]:,.0f}**. "
             f"In **{int(story.loc[mine.index[-1], 'Year'])}** it was **{mine.iloc[-1]:,.0f}**. "
             f"That is a change of **{mine.iloc[-1] - mine.iloc[0]:+,.0f}**.")
