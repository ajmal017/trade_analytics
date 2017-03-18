

from jinja2 import Template
import json

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader

# env = Environment(
#     loader=PackageLoader('templates'),  #'yourapplication',
#     autoescape=select_autoescape(['html', 'xml'])
# )

template_dir = 'templates/'
env = Environment(loader=FileSystemLoader(template_dir))

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

env.filters['to_pretty_json'] = to_pretty_json


def getd3linechart():
	template = env.get_template('d3_linearchart_1.html')
	template_str=template.render(context={	'use_d3_httplink':True,
											'width':960,'height':500,
											'layout_template':'bases/base_page.html'
										 },
									data={	"usetsv":True,
											"file":'data/data_1.tsv'
										} 
								)

	with open('output/chart.html','w') as outfile:
		outfile.write(template_str)


def getmorrisdonutchart():
	plotdata=[
		    {'label': "Download Sales", 'value': 12},
		    {'label': "In-Store Sales", 'value': 30},
		    {'label': "Mail-Order Sales", 'value': 20}
		  ]

	template = env.get_template('morris_donut_1.html')
	template_str=template.render(context={	'use_morris_httplink':True,
											'width':960,'height':"500px",
											'layout_template':'bases/base_page.html'
										 },
									data={	'embeddata': plotdata } 
								)

	with open('output/donut.html','w') as outfile:
		outfile.write(template_str)


def getmorrisbarchart():
	plotdata=[
			    { 'y': '2006', 'a': 100, 'b': 90 },
			    { 'y': '2007', 'a': 75,  'b': 65 },
			    { 'y': '2008', 'a': 50,  'b': 40 },
			    { 'y': '2009', 'a': 75,  'b': 65 },
			    { 'y': '2010', 'a': 50,  'b': 40 },
			    { 'y': '2011', 'a': 75,  'b': 65 },
			    { 'y': '2012', 'a': 100, 'b': 90 }
		    ];
	template = env.get_template('morris_bar_1.html')
	template_str=template.render(context={	'use_morris_httplink':True,
											'width':960,'height':'500px',
											'layout_template':'bases/base_page.html'
										 },
									data={ 'embeddata': plotdata	} 
								)

	with open('output/bar.html','w') as outfile:
		outfile.write(template_str)

if __name__=='__main__':
	print "ok"
	getmorrisdonutchart()