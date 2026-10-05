import streamlit as st
import pandas as pd
import plotly.express as px

st.title("World Time Machine: Paint the Planet with Data")
st.write("A **choropleth map** colours whole countries by a number. Travel from 1952 to 2007 "
         "and watch the world change. (Data: Gapminder, 142 countries, years 1952-2007.)")

# Step 1: load real country data (comes built into Plotly - no internet needed)
df = px.data.gapminder()
indicators = {"Life expectancy (years)": "lifeExp",
              "Money per person (GDP, US dollars)": "gdpPercap",
              "Population (people)": "pop"}

# Step 2: the student's controls
what = st.selectbox("What should the map show?", list(indicators))
year = st.slider("Year", 1952, 2007, 2007, step=5)
style = st.radio("Colour style", ["Smooth colours", "5 equal-size groups"], horizontal=True)
col = indicators[what]
data = df[df["year"] == year].copy()

# Step 3: paint the map
if style == "Smooth colours":
    fig = px.choropleth(data, locations="iso_alpha", color=col, hover_name="country",
                        color_continuous_scale="Viridis")
else:
    labels = ["Lowest 20%", "Low", "Middle", "High", "Highest 20%"]
    data["group"] = pd.qcut(data[col], 5, labels=labels)
    fig = px.choropleth(data, locations="iso_alpha", color="group", hover_name="country",
                        category_orders={"group": labels},
                        color_discrete_sequence=px.colors.sequential.Viridis)
st.plotly_chart(fig)
st.caption("Try Population with smooth colours, then switch to 5 groups. Which map tells the fairer story?")

# Step 4: who is on top and who is at the bottom?
top, bottom = st.columns(2)
top.write("**Highest 5**")
top.dataframe(data.nlargest(5, col)[["country", col]], hide_index=True)
bottom.write("**Lowest 5**")
bottom.dataframe(data.nsmallest(5, col)[["country", col]], hide_index=True)

# Step 5: YOUR country's story compared with the world
st.subheader("Your country's story")
country = st.selectbox("Pick your country (or any country you are curious about)", sorted(df["country"].unique()))
story = pd.DataFrame({country: df[df["country"] == country].set_index("year")[col],
                      "World median": df.groupby("year")[col].median()})
st.line_chart(story)
first, last = story[country].iloc[0], story[country].iloc[-1]
st.metric(f"{country}: 1952 to 2007", f"{last:,.0f}", f"{last - first:+,.0f} since 1952")
st.info("A map shows WHERE, a line shows WHEN. But how far apart are these countries? "
        "Next lesson: measure real distances on our round Earth!")
