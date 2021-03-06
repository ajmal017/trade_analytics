

#----------------------------  OTHER IMPORTS -------------------------------------------

import uuid
import copy
import tempfile
import webbrowser
import time
import json

# ------------------  --------  JINJA ENVIRONMENT  ----------------------------------

# env = Environment(
#     loader=PackageLoader('templates'),  #'yourapplication',
#     autoescape=select_autoescape(['html', 'xml'])
# )


from jinja2 import Template
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader

template_dir = 'templates/'
env = Environment(loader=FileSystemLoader(template_dir))
def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))
env.filters['to_pretty_json'] = to_pretty_json


# -------------------   JS, CSS AND CDNS FOR STANDALONE ---------------------------------

INCLUDES={
	  'morris': {
	  				'css': ['<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/morris.js/0.5.1/morris.css">'],
      				'js' : ['<script src="http://cdnjs.cloudflare.com/ajax/libs/raphael/2.1.0/raphael-min.js"></script>',
        					'<script src="http://code.jquery.com/jquery-1.8.2.min.js"></script>',
        					'<script src="http://cdn.oesmith.co.uk/morris-0.4.1.min.js"></script>',
							],

	  			},
      'jquery': {
      				'js' : ['<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>'],
      			},
      'raphael' : {
      				'js':  ['<script src="http://cdnjs.cloudflare.com/ajax/libs/raphael/2.1.0/raphael-min.js"></script>']
      			},

      'd3'  : { 'js': ['<script src="http://d3js.org/d3.v4.min.js"></script>'] },
}

ChartTemplates={
	'd3-linearchart-0001' 	: { 
								'description' : 'D3 linear chart ',
								'template'    : 'd3_linearchart_0001.html', 	
								'str_template': None,
							},
	'morris-bar-0001' 		: { 
								'description' : 'Morris bar chart ',
								'template'    : 'morris_bar_0001.html', 	
								'str_template': None,
							},
	'morris-donut-0001' 	: { 
								'description' : 'Morris donut chart ',
								'template'    : 'morris_donut_0001.html', 	
								'str_template': None,
							},
}



class Charthandler(object):
	"""
	this class handles if it has to use jinja templates or just simple string templates
	other ways to render 
	- has to handle the problem of switching back and forth from 
	- keeps all the templates in order, pick nd choose the template
	- pick and choose the string template
	"""
	def __init__(self,engine='jinja',template_id=None,context=None,data=None):
		print "--------------------"
		print template_id
		print "--------------------"

		self.engine=engine
		self.template = env.get_template( ChartTemplates[template_id]['template'] )
		self.template_id=template_id
		self.context=context
		self.data=data

	def html_str(self):
		return self.template.render(context=self.context,
									data=self.data,	)
	



class Chart(object):
	"""
	this is the abstract base class that lists all the methods to be implemented
	"""
	def __init__(self):
		"""
		- options is a dictionary that stores all the information to construct the chart
		- options can be saved as json, and then can be used to reproduce the chart again
		"""

		self.Charthandler=None

		# ideally read __dict__ into options 
		# may be later

		self.options={'data':{},'context':{}, 'type': None, 'name': None, 'description': None,
						'charthandler': None, 'template_dir': None, 'template': None, 'plotdata': None , 'urldata': None}
		

	def chart_json(self,filename=None):
		"""
		get a json object that can be saved to database as a string
		"""
		if filename:
			with open(filename,'w') as fname:
				json.dump(fname, self.options, indent=4,separation=',')
		else:
			return json.dumps(self.options)

	@classmethod
	def make_chart(cls,jsonstr):
		"""
		given a chart_json or chart_json string, construct an object and return the object
		"""
		options=json.loads(jsonstr)
		obj=cls()
		obj.options=copy.deepcopy(options)
		return obj

	def set_template_engine(self,engine='JINJA'):
		"""
		check to see if jinja is there or else just use string based 
		"""
		pass

	def __setitem__(self,attr,val):
		self.options[attr]=val

	def __getitem__(self,attr):
		if hasattr(self,attr):
			return self.options[attr]
		else:
			raise "No option available"

	def set_data(self):
		"""
		set sample data for testing
		"""
		pass
	def set_context(self):
		pass

	def update(self):
		"""
		set the charthandler before you call view or to_html
		"""
		self.Charthandler=Charthandler(engine='jinja',template_id=self.options['template_id'],context=self.options['context'],data=self.options['data'])

	def view(self):
		"""
		write to temp file and then open browser to view it
		"""
		fname = tempfile.NamedTemporaryFile(suffix='.html',delete=False)
		fname.write(self.Charthandler.html_str())
		fname.close()

		webbrowser.open(fname.name)


	def to_html(self,filename=None):
		"""
		Render as html to a file or return a string 
		"""
		if filename:
			with open(filename,'w') as fname:
				fname.write(self.Charthandler.html_str())
		else:
			return self.Charthandler.html_str()

class D3plot(Chart):

	def __init__(self,template_id,chart_id):
		super(D3plot,self).__init__()
		self.options['template_id']=template_id
		self.options['chart_id']=chart_id

	def set_context(self):
		self.options['context']={	
						'chart_id' : self.options['chart_id'], 
						'includes':INCLUDES['d3'],
						'width':self.options['width'],
						'height':self.options['height'],
					 }


	def set_data(self,data_format=None,data_file=None,data_plot=None,data_url=None,data_refresh=None):
		self.options['data'] =	{	
						"data_format":data_format,
						"data_file":data_file,
						'data_url':data_url,
						'data_refresh':data_refresh,
						"data_plot": data_plot ,
					}

		
class Morris(Chart):

	def __init__(self,template_id,chart_id):
		super(Morris,self).__init__()
		self.options['template_id']=template_id
		self.options['chart_id']=chart_id

	def set_context(self):
		self.options['context']={	
						'chart_id' : self.options['chart_id'], 
						'includes':INCLUDES['morris'],
						'width':self.options['width'],
						'height':self.options['height'],
					 }

	def set_data(self,data_format='embed',data_file=None,data_plot=None,data_url=None,data_refresh=None):

		self.options['data'] =	{	
						"data_format":data_format,
						"data_file":data_file,
						'data_url':data_url,
						'data_refresh':data_refresh,
						"data_plot": data_plot ,
					}






if __name__=='__main__':
	print "ok"
	chart=D3plot('d3-linearchart-0001','myd3lin')
	chart.options['width']=900
	chart.options['height']=500
	chart.set_context()
	chart.set_data(data_file='/home/venkat/Documents/trade_analytics/trade_analytics/charts/jschart_builder/output/data/data_1.tsv',
					data_format='tsv' )
	chart.update()
	chart.to_html(filename='output/D3linearclass.html')

	print "donut"

	chart=Morris('morris-donut-0001','myDonut')
	chart.options['width']=500
	chart.options['height']=300
	chart.set_context()
	data_plot=[
			    {'label': "Download Sales", 'value': 12},
			    {'label': "In-Store Sales", 'value': 30},
			    {'label': "Mail-Order Sales", 'value': 20}
			  ]
	chart.set_data(data_plot={'data_plot':data_plot})

	chart.update()
	chart.to_html(filename='output/donutclass.html')

	print "bar"


	chart=Morris('morris-bar-0001','myDonut')
	chart.options['width']=500
	chart.options['height']=300
	chart.set_context()
	data_plot=[
			    { 'y': '2006', 'a': 100, 'b': 90 },
			    { 'y': '2007', 'a': 75,  'b': 65 },
			    { 'y': '2008', 'a': 50,  'b': 40 },
			    { 'y': '2009', 'a': 75,  'b': 65 },
			    { 'y': '2010', 'a': 50,  'b': 40 },
			    { 'y': '2011', 'a': 75,  'b': 65 },
			    { 'y': '2012', 'a': 100, 'b': 90 }
		    ]
	chart.set_data(data_plot={'data_plot':data_plot,'xkey':'y','ykeys': ['a', 'b'],'labels': ['Series A', 'Series B']})
	chart.update()
	chart.to_html(filename='output/barclass.html')

	