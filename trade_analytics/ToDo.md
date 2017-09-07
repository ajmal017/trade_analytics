# ToDo


- Make charting better:
	- May be I do not need tornado websocket, just create the charts and save with UUIDS, Jquery will keep reloading them till they receive the chart.
	- I want to plot features for a given stock and multiple ones. Live computed features that I dont want to save, just want to see
	- Should be able to do that for multiple number of stocks
	- Use tasks to compute the charts
- Charts I want:
	- Send 1 df with all stocks concatenated
	- Send dict of dfs of all stocks
	- send dict of columns names for all stocks, data is taken from db
	- Server to accept all inputs
	- Send makechart classname and above inputs, t pick the function to make charts
	- Very basic entry to get charts quickly
	- Entry function to start 
	- ChartServer also responsible for: 
		- given dfinstants with UUIDS, generate the charts and save them
		- ChartServer has to be in same machine as django webserver
		- Create the charts and save into folder
		- chartserver responisble for deleting old charts 

- Make features compute better
	- register features before it self
	- recompute features or just fill in the missing
	- compute model predictions and save them to db

