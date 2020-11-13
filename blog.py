import altair as alt
import pandas as pd
import numpy as np
# import seaborn as sns
import streamlit as st
# from matplotlib import pyplot as plt
# from preprocessing import *
# import requests
# from bs4 import BeautifulSoup

##################
## build graphs ##
##################

def popualtion_GDP_stat(dataset):
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

def popualtion_GDP_inter(dataset,filter):
    selection = alt.selection_single(on='mouseover',empty='none')

    point_1 = alt.Chart(dataset,title='Population - GDP per Capita').mark_point(filled=True,size=90).encode(
        x=alt.X('Population:Q'),
        y=alt.Y('GDP per Capita:Q'),
        size='Population',
        tooltip=['Country','Code']
    ).add_selection(selection).transform_filter(
        alt.FieldOneOfPredicate(field='Country', oneOf=filter)
    )

    point_2 = alt.Chart(dataset).mark_point(filled=True,size=90).encode(
        x=alt.X('Population:Q'),
        y=alt.Y('GDP per Capita:Q'),
        size='Population',
        color=alt.value('red')
    ).transform_filter(
        alt.datum.Country == 'Norway'
    )

    text = alt.Chart(dataset).encode(
        x=alt.X('Population:Q'),
        y=alt.Y('GDP per Capita:Q'),
        text=alt.Text('Country'),
        color=alt.value('black')
    ).mark_text(dy=-4,dx=25).transform_filter(
        alt.FieldOneOfPredicate(field='Country', oneOf=filter)
    )

    return (point_1 + point_2 + text).interactive()

def NOR_medals_stat(dataset):
    return alt.Chart(dataset,title="Chnages of Number of Medals in Norway 1900-2014").mark_area().encode(
    x=alt.X('Year:O'),
    y=alt.Y('count():Q',axis=alt.Axis(grid=False)),
    color=alt.Color('Medal:N'))

def NOR_medals_inter(dataset, filter_year):
    return alt.Chart(dataset,title="Chnages of Number of Medals in Norway").mark_area().encode(
    x=alt.X('Year:O'),
    y=alt.Y('count():Q',axis=alt.Axis(grid=False),scale=alt.Scale(domain=(0,160))),
    color=alt.Color('Medal:N', 
                    sort=['Gold','Silver','Bronze'],
                    scale=alt.Scale(domain=['Gold','Silver','Bronze'],
                                    range=['gold', 'silver','darkorange']))
    ).transform_filter(
        alt.datum.Year >= filter_year
    )

def medal_rank(dataset, medal_type='Total'):
    base = alt.Chart(dataset,title='2018 Medal Summary').mark_bar().encode(
            y=alt.Y('Country:N',sort='-x'),
            x=alt.X('total:Q',scale=alt.Scale(domain=(0,40)))
            ).transform_joinaggregate(
                total = f'sum({medal_type})',
                groupby=['Country']
            ).transform_window(
                rank='rank(total)',
                sort=[alt.SortField('total',order='descending')]
            ).transform_filter(
                alt.datum.rank<10
            )
    if medal_type == 'Gold':
        return base.mark_bar(color='gold')
    elif medal_type == 'Silver':
        return base.mark_bar(color='silver')
    elif medal_type == 'Bronze':
        return base.mark_bar(color='darkorange')
    else:
        return base
    

def gender(dataset):
    return alt.Chart(dataset).mark_bar().encode(
    x=alt.X('Year:O'),
    y=alt.Y('count()',title=None,scale=alt.Scale(domain=[0,2000])),
    color='Gender'
    )

def gender_inter(dataset, filter_year):
    char_m = alt.Chart(dataset).mark_bar(color="lightblue").encode(
    x=alt.X('count:Q',
            title='Men',
            sort='descending',
           scale=alt.Scale(domain=(0,160)),
           axis=alt.Axis(grid=False)),
    y=alt.Y('Year:N'),
    tooltip=['count:Q']
    ).transform_joinaggregate(
        groupby=['Year','Gender'],
        count = 'count(Medal)'
    ).transform_filter(
        (alt.datum.Gender=='Men') & (alt.datum.Year >= filter_year)
    )

    chart_f = alt.Chart(dataset).mark_bar(color="lightpink").encode(
        x=alt.X('count:Q',
                title='Women',
                sort='ascending',
            scale=alt.Scale(domain=(0,160)),
           axis=alt.Axis(grid=False)),
        y=alt.Y('Year:N',title=None,axis=None),
        tooltip=['count:Q']
    ).transform_joinaggregate(
        groupby=['Year','Gender'],
        count = 'count(Medal)'
    ).transform_filter(
        (alt.datum.Gender=='Women') & (alt.datum.Year >= filter_year)
    )

    return (char_m | chart_f).properties(title='Number of Winners in Gender')

def season_inter(dataset, filter_year):
    selection = alt.selection_single(on='mouseover',empty='none')
    opacityCondition = alt.condition(selection, alt.value(1.0), alt.value(0.8))
    bar = alt.Chart(dataset,title='Number of Medals in Summer and Winter Olympics overtime').mark_bar().encode(
            x='Year:N',
            y='Medal:Q',
            color='Season',
            tooltip=['Medal:Q'],
            opacity=opacityCondition
        ).add_selection(selection).transform_filter(alt.datum.Year >= filter_year)
    return bar

def main():
    # load data
    ## dataset_1
    countries = pd.read_csv('data/countries.csv')
    df = pd.read_csv('data/summer_winter.csv')
    ## dataframe used in stat
    df_50_60 = df[df.Year.isin(range(1950,1970))]
    df_70_80 = df[df.Year.isin(range(1970,1990))]
    df_90 = df[df.Year.isin(range(1990,1999))]
    df_00 = df[df.Year.isin(range(2000,2006))]
    df_06 = df[df.Year>2006]
    df_NOR = df[df.Country=='NOR']
    # country_code = list(countries.Code)
    ## dataset_2
    medal_2018 = pd.read_csv('data/medal_2018.csv')
    ## dataset_3
    winner_medals = pd.read_excel('data/winner_medals.csv')

    ##########################
    ####### main page ########
    ##########################

    st.title("""Olympics' Facts in Norway""")

    st.sidebar.markdown("""Select to show more contents""")
    st.sidebar.text("(Diselect to show less)")
    checkbox_1 = st.sidebar.checkbox('Domain Questions',value=True)
    checkbox_2 = st.sidebar.checkbox('Select to learn more',value=False)
    checkbox_3 = st.sidebar.checkbox('Earlier Version',value=False)


    html = """
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#ffe6e6);
        padding: 80px 50px;

    }
    .sidebar .sidebar-collapse-control,
    .sidebar.--collapsed .sidebar-collapse-control {
        left: 2px;
        right: auto;
    }

    </style>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    if checkbox_1:
        st.header('Domain Questions')
        st.markdown("""
        1. In 2018, what are the top 10 countries with the highest number of medals? 
        2. How population and GDP per capita relate between countries?
        3. What is the difference in the number of medals between winter and summer competition?
        4. How the number of winners with different genders has changed?
        5. What is the change in the total number of medals in Norway?

        """)

    
    if checkbox_2:
        st.markdown('----------------------')
        # st.balloons()
        st.header("Learn Something About Olympics' Facts in Norway")
        # - Default view at the beginning of the page
        st.markdown('<h3>Top 10 Countries with Different Medals in 2018</h3>',unsafe_allow_html=True)
        medal_type = st.radio(label='Select medal type for 2018',options=['Total','Gold','Silver','Bronze'])
        st.altair_chart(medal_rank(medal_2018,medal_type), use_container_width=True)
        
        st.sidebar.markdown('----------------------')
        country_list = list(countries.Country) 
        button = st.sidebar.multiselect('Select to show more countries', country_list, default=['Norway'])
        st.sidebar.markdown('----------------------')
        year = st.sidebar.slider('Year', 1896, 2014, 1988)  
        
        st.markdown('----------------------')
        st.markdown('<h3>Relations between Population and GDP per Capita Overtime</h3>',unsafe_allow_html=True)
        st.markdown('Select countries you would like to know more in the sidebar at the left ^^')
        st.altair_chart(popualtion_GDP_inter(countries,button), use_container_width=True)
        # st.text(str(year))

        st.markdown('----------------------')
        st.markdown('<h3>Number of Medals in Summer and Winter Olympics Overtime 1896-2012</h3>',unsafe_allow_html=True)
        year_season_medal = df.groupby(['Year','Season']).count().Medal.reset_index()
        # plt.subplots(figsize=(7,3))
        st.altair_chart(season_inter(year_season_medal, year), use_container_width=True)
        # g.set(title='Number of Medals in Summer and Winter Olympics overtime')
        # st.set_option('deprecation.showPyplotGlobalUse', False)
        # st.pyplot()

        st.markdown('----------------------')
        st.markdown('<h3>Number of Winners in Different Gender Changes Overtime 1924-2014</h3>',unsafe_allow_html=True)
        st.altair_chart(gender_inter(winner_medals,year), use_container_width=True)
        # gender_fig.configure_view(title='test')

        st.markdown('----------------------')
        st.markdown('<h3>Number of medals change along years in Norway</h3>',unsafe_allow_html=True)
        st.altair_chart(NOR_medals_inter(df_NOR,year), use_container_width=True)

    if checkbox_3:
        st.markdown('----------------------')
        st.header('Earlier Version')
        st.markdown('<h3>Building Statistics Vis</h3>',unsafe_allow_html=True)
        st.markdown(" ")
        st.markdown('Relationship between popultaion and GDP')
        st.altair_chart(popualtion_GDP_stat(countries), use_container_width=True)

        st.markdown('Number of medals change along years in Norway')
        st.altair_chart(NOR_medals_stat(df_NOR), use_container_width=True)

        st.markdown('Number of athletes with different genders changes overtime')
        st.altair_chart(gender(df_06)|gender(df_00)|gender(df_90)|gender(df_70_80)|gender(df_50_60), use_container_width=True)

        st.markdown('Top 10 total medals in 2018')
        st.altair_chart(medal_rank(medal_2018), use_container_width=True)

        




if __name__ == "__main__":
    main()