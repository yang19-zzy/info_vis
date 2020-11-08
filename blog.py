import altair as alt
import pandas as pd
import streamlit as st
import requests
from BeautifulSoup4 import BeautifulSoup

def popualtion_GRP(dataset):
    selection = alt.selection_single(on='mouseover',empty='none')

    point_1 = alt.Chart(dataset).mark_point(filled=True,size=90).encode(
        x=alt.X('Population:Q'),
        y=alt.Y('GDP per Capita:Q'),
        tooltip=['Country','Code']
    ).add_selection(selection)

    point_2 = alt.Chart(dataset).mark_point(filled=True,size=90).encode(
        x=alt.X('Population:Q'),
        y=alt.Y('GDP per Capita:Q'),
        color=alt.value('red')
    ).transform_filter(
        alt.datum.Country == 'Norway'
    )

    text = point_2.mark_text(dy=-4,dx=25).encode(
        alt.Text('Country'),
        color=alt.value('black')
    )

    return point_1 + point_2 + text

def NOR_medals(dataset):
    return alt.Chart(dataset).mark_area().encode(
    x=alt.X('Year:O'),
    y=alt.Y('count():Q',axis=alt.Axis(grid=False)),
    color=alt.Color('Medal:N', sort=['Gold','Silver','Bronze'])
    )

def medal_rank(dataset):
    return alt.Chart(dataset).mark_bar().encode(
    y=alt.Y('Country:N',sort='-x'),
    x=alt.X('Total:Q')
    ).transform_joinaggregate(
        total = 'sum(Total)',
        groupby=['Country']
    ).transform_window(
        rank='rank(total)',
        sort=[alt.SortField('total',order='descending')]
    ).transform_filter(
        alt.datum.rank<10
    )

def gender(dataset):
    return alt.Chart(dataset).mark_bar().encode(
    x=alt.X('Year:O'),
    y=alt.Y('count()',title=None,scale=alt.Scale(domain=[0,2000])),
    color='Gender'
    )


def main():
    # Data Processing
    ## dataset_1
    ## https://www.kaggle.com/the-guardian/olympic-games?select=summer.csv
    dictionary = pd.read_csv("archive/dictionary.csv")
    summer = pd.read_csv("archive/summer.csv")
    winter = pd.read_csv("archive/winter.csv")
    countries = dictionary.dropna()
    country_code = countries.Code.to_list()
    ## winter_countries
    winter_countries = winter.loc[winter['Country'].isin(country_code)]
    winter_countries['Season'] = ['winter'] * winter_countries.shape[0]
    ## summer_countries
    summer_countries = summer.loc[summer['Country'].isin(country_code)]
    summer_countries['Season'] = ['summer'] * summer_countries.shape[0]
    ## df
    df = pd.concat([summer_countries,winter_countries],axis=0).reset_index().iloc[:,1:]
    df_50_60 = df[df.Year.isin(range(1950,1970))]
    df_70_80 = df[df.Year.isin(range(1970,1990))]
    df_90 = df[df.Year.isin(range(1990,1999))]
    df_00 = df[df.Year.isin(range(2000,2006))]
    df_06 = df[df.Year>2006]
    df_NOR = df[df.Country=='NOR']
    ## dataset_2
    URL = "https://www.nytimes.com/interactive/2018/sports/olympics/medal-count-results-schedule.html"

    result = requests.get(URL,'html.parser')
    soup = BeautifulSoup(result.content, 'html.parser')
    table_soup = soup.find(class_="int-table oly-table int-table-medal-standings")

    table = table_soup.find('table')
    rows_soup = table.find_all('tr')
    heads = rows_soup[0]
    data = rows_soup[1:]

    columns = []
    heads_item = heads.find_all('td')
    for item in heads_item:
        columns.append(item.text)
    rows = []
    for row in data:
        rows.append([item.text for item in row])

    medal_2018 = pd.DataFrame(rows,columns=columns)
    medal_2018['Country'] = medal_2018.apply(lambda X: X['Medal Count'][:-3],axis=1)
    medal_2018['Code'] = medal_2018.apply(lambda row: row['Medal Count'][-3:], axis=1)






    st.title("SI 649 Individual Project - Communicative Visualization")
    # st.altair_chart()
    selectbox_values = st.sidebar.selectbox(label='Select to show more',
                    options=['Learning Objectives',
                            'Design Process',
                            'Final Design'])
    if selectbox_values == 'Learning Objectives':
        st.header('Learning Objectves')
        st.markdown("""
        1. What is the difference in number of medals between winter and summer competition?
        2. From 1950 to 2014, how number of athletes in different gender has changed?
        3. What is the change in total number of medals in Norway?
        """)

    elif selectbox_values == 'Design Process':
        st.header('Design Process - My exploration with data')
        st.markdown(" ")
        st.markdown('Relationship between popultaion and GDP')
        st.altair_chart(popualtion_GRP(countries), use_container_width=True)

        st.markdown('Number of medals change along years in Norway')
        st.altair_chart(NOR_medals(df_NOR), use_container_width=True)

        st.markdown('Number of athletes with different genders changes overtime')
        st.altair_chart(gender(df_06)|gender(df_00)|gender(df_90)|gender(df_70_80)|gender(df_50_60), use_container_width=True)

        st.markdown('Top 10 total medals in 2018')
        st.altair_chart(medal_rank(medal_2018), use_container_width=True)
    else:
        st.header("Final Design")
        st.markdown("Why I think this is a good design?")
        st.markdown("""
        1. I would combine created graphs together with filters 
        2. xxx
        """)
        
        
        st.markdown("How would I evaluate my design?")
        st.markdown("""
        1. 
        2. 
        """)        




if __name__ == "__main__":
    main()
