#imports
import streamlit as st
import pandas as pd
from pandas import DataFrame
import altair as alt
import numpy as np
import pprint
import urllib.request
import time, json
import json
import networkx as nx
from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from networkx.drawing.nx_agraph import graphviz_layout

# enable wide layout
st.set_page_config(layout="wide")

#Title
st.title('Post Game Analysis')
st.write('Ningdan Zhang, Zihao Zhu, Xinyi Wang, Zhengyang Zhao, Xin Hu')
#Setup Columns
left, right= st.beta_columns((1,1.7))
# t1, t2= st.beta_columns((2, 1))
# c1, c2, c3= st.beta_columns((4, 1, 1))


#Import Data
df1 = pd.read_csv("https://raw.githubusercontent.com/eytanadar/si649robogames/main/server/example1/examplematch1.robotdata.csv")
robotdata = pd.read_csv("https://raw.githubusercontent.com/eytanadar/si649robogames/main/server/example1/examplematch1.robotdata.csv")
with urllib.request.urlopen("https://raw.githubusercontent.com/eytanadar/si649robogames/main/server/example1/bobvalice.json") as url:
    gamedata = json.loads(url.read().decode())
G = nx.read_gexf("./server/example1/examplematch1.tree.gexf",relabel=True)
G1 = nx.read_gexf("./server/example1/examplematch1.socialnet.gexf",relabel=True)

####################################Viz1####################################
#####################################1.1####################################
expire_value_list = []
for row in df1.itertuples():
  expires = getattr(row, 'expires')
  if np.isnan(expires):
    expire_time = 100
  else:
    expire_time = int(expires)
  expire_value = row[expire_time+3]
  expire_value_list.append(expire_value)

data = {'id':df1['id'].values,'expire_time':df1['expires'].values,'expire_value':expire_value_list}
df = DataFrame(data)

#Line chart
line_chart = alt.Chart(df).mark_line().encode(
    x = alt.X('id:N',axis=alt.Axis(title='Robot ID')),
    y = alt.Y('expire_value:Q',axis=alt.Axis(title='Expire value')),
).properties(
    width = 1300,
    height = 300
).encode(    
    tooltip = [alt.Tooltip('expire_value:Q', title="Expire Value", format='.2f'),alt.Tooltip('expires:Q', title="Expire Time", format='.2f'),"id:N"]
    )

#vertical line
line_selection = alt.selection_single(on='mouseover',empty='none')

colorCondition = alt.condition(line_selection,alt.value('lightgray'),alt.value('transparent'))

vline = alt.Chart(df).mark_rule(size = 4).encode(
    x = alt.X('id:N'),
    color = colorCondition
).add_selection(
    line_selection
)

#interaction dots
dot_selection = alt.selection_single(on='mouseover',nearest=True,empty='none',encodings=['x'])

sizeCondition = alt.condition(dot_selection,alt.SizeValue(70),alt.SizeValue(0))

dot = alt.Chart(df).mark_circle(color='black').encode(
    x = alt.X('id:N'),
    y = alt.Y('expire_value:Q'),
    size = sizeCondition,
    tooltip = ['id:N','expire_time:Q','expire_value:Q']
).add_selection(
    dot_selection
)

viz1_1 = alt.layer(line_chart, dot, vline)

#####################################1.2####################################

####################################Viz2####################################
#####################################2.1####################################

for i in np.arange(0,100):
    reason = gamedata['winreasons'][i]
    reason['prod'] = robotdata.at[i,'Productivity']   

reasonframe = pd.read_json(json.dumps(gamedata['winreasons']))   

sum_prod = alt.Chart(reasonframe).mark_bar().encode(
    y = alt.Y('winner:O'),
    x = alt.X('sum_prod:Q', scale=alt.Scale(domain=[0, 2800])),
    color = alt.Color('reason:N')
).transform_aggregate(
    sum_prod='sum(prod)',
    groupby=["winner","reason"]
)

selection0 = alt.selection_multi(fields=['reason'], bind='legend')

sum_prod_inter = sum_prod.add_selection(
  selection0,
).transform_filter(
  selection0
).encode(
  tooltip = [alt.Tooltip('sum_prod:Q', format='.2f'),"winner:N","reason:N"],
)

sum_prod_inter = sum_prod_inter.properties(
    title = "Sum of productivities",
    height = 250,
    width = 1000,
)

sum_prod_inter.configure_axis(
    labelFontSize=17,
    titleFontSize=17
).configure_title(
    fontSize=20,
).configure_legend(
    titleFontSize=17,
    labelFontSize=17,
)

viz2_1 = sum_prod_inter

#####################################2.2####################################
prod_distri = alt.Chart(reasonframe).mark_circle(size=80).encode(
    color = 'winner:N',
    x = alt.X('prod:Q', title = "Productivity"),
    y = alt.Y('reason:N'),
)
selection = alt.selection_multi(fields=['winner'], bind='legend')
selection1 = alt.selection_single(on="mouseover", empty="none", nearest=True, clear = "click")

selection2 = alt.selection_single(on="mouseover", nearest=True, clear = "click")
sizeCondition = alt.condition(selection1, alt.SizeValue(250), alt.SizeValue(100))
colorCondition = alt.condition(selection2, 'winner:N', alt.value('grey'))

prod_distri_inter = prod_distri.add_selection(
    selection,
    selection2,
    selection1
).encode(    
    tooltip = [alt.Tooltip('prod:Q', title="productivity", format='.2f'),"winner:N","reason:N"],
    opacity=alt.condition(selection, alt.value(1), alt.value(0)),
    color = colorCondition,
    size = sizeCondition
)

prod_distri_inter = prod_distri_inter.properties(
    title = "Distribution of productivities",
    height = 250,
    width = 1000,
)


prod_distri_inter.configure_axis(
    labelFontSize=17,
    titleFontSize=17
).configure_title(
    fontSize=20,
).configure_legend(
    titleFontSize=17,
    labelFontSize=17,

)

viz2_2 = prod_distri_inter


####################################Viz3####################################
pos = graphviz_layout(G, prog="twopi", args="")
degrees = dict(nx.degree(G))
nx.set_node_attributes(G, name='degree', values=degrees)
number_to_adjust_by = 10
adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(G)])
nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)
node_highlight_color = 'white'
edge_highlight_color = 'black'

size_by_this_attribute = 'adjusted_node_size'
color_by_this_attribute = 'adjusted_node_size'

color_palette = Blues8

title = 'Family Tree'

HOVER_TOOLTIPS = [("ID", "@index")]

plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
            x_range=Range1d(-100, 1300), y_range=Range1d(-300, 1100), title=title,plot_height=600, plot_width=600)

network_graph = from_networkx(G, pos, k=0.15, iterations=70, center=(500,600), with_labels=True)

minimum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
maximum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

plot.renderers.append(network_graph)

x, y = zip(*network_graph.layout_provider.graph_layout.values())
node_labels = list(G.nodes())
source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)
plot.renderers.append(labels)
plot.axis.visible = False
#output_notebook()
viz3 = plot


####################################Viz4####################################
gamedata = {}
with open('./server/example1/bobvalice.json') as json_file:
    gamedata = json.load(json_file)
robotdata = pd.read_csv("./server/example1/examplematch1.robotdata.csv")
for i in np.arange(0,100):
    reason = gamedata['winreasons'][i]
    reason['prod'] = robotdata.at[i,'Productivity']   
reasonframe = pd.read_json(json.dumps(gamedata['winreasons']))
winner = reasonframe['winner'].to_list()
reason = reasonframe['reason'].to_list()
prod = reasonframe['prod'].to_list()
for i in G1.nodes():
    G1.nodes[i]['winner'] = winner[int(i)]
    G1.nodes[i]['reason'] = reason[int(i)]
    G1.nodes[i]['prod'] = prod[int(i)]
node_highlight_color = 'black'
edge_highlight_color = 'black'

color_by_this_attribute = 'prod'

color_palette = Blues8

#nx.set_node_attributes(G, attrs)
title = 'Social Network'

HOVER_TOOLTIPS = [("Id", "@index"),("Winner","@winner"),("Reason","@reason"),("Productivity","@prod")]
plot4 = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title,plot_height=600, plot_width=600)

network_graph = from_networkx(G1, nx.spring_layout, scale=10, center=(0,0))

network_graph.node_renderer.hover_glyph = Circle(size=15, fill_color=node_highlight_color,line_width=2)
network_graph.node_renderer.selection_glyph = Circle(size=15, fill_color=node_highlight_color,line_width=2)

minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
network_graph.node_renderer.glyph = Circle(size=15, fill_color=linear_cmap(color_by_this_attribute,color_palette,high=minimum_value_color,low=maximum_value_color))

network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color,line_width=2)
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color,line_width=2)

network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

plot4.renderers.append(network_graph)
plot4.axis.visible = False
viz4 = plot4

#####################################Put all together####################################
#line_chart + vline + dot
# with t1:
# 	st.header('Robot lifecycle Value')
# 	st.write('Choose a robot ID from the dropdown menu to view its lifecycle value')

with left:
	st.header('Family Tree')
	st.write('The family tree used spring layout to present the relationship between each robots. Each robot’s id is presented beside the robot’s node. The darker the node is, the more important role the node plays in the family, which means that the robot has more linked neighbors (here would be more children robots) than other robots.')
	st.write(viz3)
	st.header('Social Network')
	st.write('The network used spring layout to present the social relationship between each robot. Each node in this graph has 4 attributes: id, winner, winner reason and productivity. The darker the node is, the higher productivity it has. When user hovers on a node, its neighbor will be highlighted, and a tooltip will pop up which shows its attributes.')
	st.write(viz4)

with right:
	st.header('Productivity')
	st.write('The first graph is the sum of total productivity of two teams and also use color to encode the reason of winning. The second graph is the distribution of productivity and each point represent a robot and user can hover to see detailed information. Reason 1: win by the social network strategy. Reason 1.5: win by fliping a coin with same network values. Reason 2: win by closer guess. Hover on graph to view detail. Click on legend to filter out data.')
	st.write(viz2_1)
	st.write(viz2_2)

	st.header('Robot lifecycle Value')
	st.write('The first graph is about each robot’s value at expiration time. It also displays a vertical line that moves with the mouse, as well as the intersection dot of the vertical line and the line chart. When hovering over these intersection dots, the tooltip will display the robot id, expiration time and expiration value.')
	st.write(viz1_1)

	st.write('The second graph shows the time series of robot’s value. The users can select the robot that they are interested in in the drop box, and then check the time XTU and value of that robot by tooltip.')
	df2 = df1.iloc[:,3:103]
	df2['id'] = df1['id']

	df2 = df2.melt(id_vars='id',var_name='time',value_name='value')
	df3 = df2.copy()
	df3['time'] = df2['time'].str.replace('t_','')

	id = list(df3['id'].unique())
	x_axis_select = st.selectbox(label="Robot ID", 
								  options = id)

	
	filtered_df3 = df3[df3['id'] == x_axis_select]


	viz1_2 = alt.Chart(filtered_df3).mark_point(filled=True).encode(
	    x = alt.X('time:N',sort=None),
	    y = alt.Y('value:Q')
	).properties(
	    width = 1100,
	    height = 300
	)

	alt.data_transformers.disable_max_rows()
	st.write(viz1_2)

	# st.markdown('Reason 1: win by the social network strategy,\nReason 1.5: win by fliping a coin with same network values,\nReason 2: win by closer guess')
	# st.write('Reason 1: win by the social network strategy,\nReason 1.5: win by fliping a coin with same network values,\nReason 2: win by closer guess')


