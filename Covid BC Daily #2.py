import gif
import numpy as np
import pandas as pd
import plotly.graph_objects as go

data = pd.read_csv('./data/Canada COVID Data/Provincial_Daily_Totals.csv')
data = data[data['Abbreviation']=='BC']		# select data relevant to BC alone
data = data.reset_index(drop=True)
data = data.fillna(0)
# drop unneccessary columns
del data['Province']
del data['Abbreviation']
del data['OBJECTID']
del data['DailyTested']
del data['TotalTested']

# fix the date column
data['SummaryDate'] = data['SummaryDate'].apply(lambda x: x.split()[0]).astype(np.datetime64)
# set proper types for other columns
cols = list(data.columns)
cols.remove('SummaryDate')
for item in cols:
	data[cols] = data[cols].astype(np.int64)

fig = go.Figure()
fig.add_trace(
	go.Scatter(
		x=data['SummaryDate'], y=data['TotalCases'], mode='lines', name='New cases'))
fig.update_layout(title='Cumulative cases', yaxis_title='No. of people', xaxis_title='Time')
fig.write_image('./img/Pyplot_BC_covid_total_cases.png', width=1520, height=744)

fig = go.Figure()
fig.add_trace(
	go.Scatter(
		x=data['SummaryDate'], y=data['DailyTotals'], mode='lines', name='New cases'))
fig.update_layout(title='Daily cases', yaxis_title='No. of people', xaxis_title='Time')
fig.write_image('./img/Pyplot_BC_covid_daily_cases.png', width=1520, height=744)

def correct_for_weekends(series, start):
	for i in range(start, len(series), 7):
		n = 3
		if series[i] == 0:				# if the numbers were given out on Tuesday
			n += 1
			i += 1
		x = series[i] % n
		y = series[i] - x				# so we don't have 1/3rd cases on some days
		series.loc[i-n+1:i] = [y//n]*n
		series[i] += x

for item in cols:
	if 'Daily' in item:
		print(item)
		correct_for_weekends(data[item], 2)			# Correct for weekends

index = data[data['SummaryDate']==np.datetime64('2020-11-11')].index[0]	# Lest we forget
for item in cols:
	if 'Daily' in item:
		data.loc[index:index+1, item] = [data.loc[index+1, item]//2] * 2

fig = go.Figure()
fig.add_trace(
	go.Scatter(
		x=data['SummaryDate'], y=data['DailyTotals'], mode='lines', name='New cases'))
fig.update_layout(title='Daily cases', yaxis_title='No. of people', xaxis_title='Time')
fig.write_image('./img/Pyplot_BC_covid_daily_cases_corrected.png', width=1520, height=744)

data['TotalCases'] = data['DailyTotals'].cumsum()
data['TotalRecovered'] = data['DailyRecovered'].cumsum()
data['TotalDeaths'] = data['DailyDeaths'].cumsum()
data['TotalActive'] = data['DailyActive'].cumsum()
data['TotalHospitalized'] = data['DailyHospitalized'].cumsum()
data['TotalICU'] = data['DailyICU'].cumsum()


fig = go.Figure()

traces = {}
traces['tCases'] = go.Scatter(x=data['SummaryDate'], y=data['TotalCases'], mode='lines',  name='Total cases',  line_shape='spline')
traces['tActive'] = go.Scatter(x=data['SummaryDate'], y=data['TotalActive'], mode='lines',  name='Total active',  line_shape='spline')
traces['tRecovered'] = go.Scatter(x=data['SummaryDate'], y=data['TotalRecovered'], mode='lines',  name='Total recovered',  line_shape='spline')
traces['tDeaths'] = go.Scatter(x=data['SummaryDate'], y=data['TotalDeaths'], mode='lines',  name='Total deaths',  line_shape='spline')
traces['dCases'] = go.Scatter(x=data['SummaryDate'], y=data['DailyTotals'], mode='lines',  name='Daily cases',  line_shape='spline')
traces['dActive'] = go.Scatter(x=data['SummaryDate'], y=data['DailyActive'], mode='lines',  name='Daily active',  line_shape='spline')
traces['dRecovered'] = go.Scatter(x=data['SummaryDate'], y=data['DailyRecovered'], mode='lines',  name='Daily recovered',  line_shape='spline')
traces['dDeaths'] = go.Scatter(x=data['SummaryDate'], y=data['DailyDeaths'], mode='lines',  name='Daily deaths',  line_shape='spline')
traces['dHospitalized'] = go.Scatter(x=data['SummaryDate'], y=data['DailyHospitalized'], mode='lines',  name='Daily hospitalized',  line_shape='spline')
traces['dICU'] = go.Scatter(x=data['SummaryDate'], y=data['DailyICU'], mode='lines',  name='Daily ICU',  line_shape='spline')

@gif.frame
def plot(date):
	d = data[data['SummaryDate']<=date]
	# print(d.iloc[len(d)-1])
	fig = go.Figure()
	fig.add_trace(
		go.Scatter(
			x = d['SummaryDate'], 
			y = d['TotalCases'],
			mode = 'lines',
			name = 'Total cases',
			line_shape = 'spline'))
	fig.add_trace(
		go.Scatter(
			x = d['SummaryDate'], 
			y = d['TotalActive'],
			mode = 'lines',
			name = 'Total active',
			line_shape = 'spline'))
	fig.add_trace(
		go.Scatter(
			x = d['SummaryDate'], 
			y = d['TotalRecovered'],
			mode = 'lines',
			name = 'Total recovered',
			line_shape = 'spline'))
	fig.add_trace(
		go.Scatter(
			x = d['SummaryDate'], 
			y = d['TotalDeaths'],
			mode = 'lines',
			name = 'Total deaths',
			line_shape = 'spline'))
	fig.update_layout(title='COVID-19 cases in BC',
				   yaxis_title='No. of people',
				   yaxis_range=(0, int(max(data.TotalCases)*1.05)),
				   xaxis_title='Time',
				   xaxis_range=(data.iloc[0].SummaryDate, data.iloc[-1].SummaryDate),
				   hovermode='x unified'
				   )
	return fig

f = []
for date in data['SummaryDate']:
	f.append(plot(date))

for i in range(30):
	f.append(plot(date))

gif.save(f, './img/PyPlot_BC_covid_total_cases.gif', duration=25)

fig = go.Figure()
for trace in traces.values():
	fig.add_trace(trace)

fig.update_layout(
	title='Cumulative cases', 
	yaxis_title='No. of people', 
	xaxis_title='Time',
	hovermode='x unified'
)
fig.write_html('./img/html/Pyplot_BC_covid_cumulative_all.html', include_plotlyjs=False, full_html=False)

fig = go.Figure()
fig.add_trace(
	go.Scatter(
		x=data['SummaryDate'], y=data['TotalCases'], mode='lines', name='New cases'))
fig.update_layout(title='Cumulative cases', yaxis_title='No. of people', xaxis_title='Time')