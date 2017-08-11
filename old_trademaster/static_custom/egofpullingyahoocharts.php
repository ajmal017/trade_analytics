<!DOCTYPE html>
<html>
<head>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
</head>
<body>

<h2>Spectacular Mountains</h2>
<img src="pic_mountain.jpg" alt="Mountain View" style="width:304px;height:228px">

<form method="post" action="disp_form.php">
<p>First Value:<br/>
<input type="text" id="first" name="first"></p>
<p>Second Value:<br/>
<input type="text" id="second" name="second"></p>
<input type="radio" name="group1" id="subtract" value="subtract">-<br/>
<p></p>
<button type="submit" name="answer" id="answer" value="answer" >Calculate</button>

</form>
<br>
<button type="button" name="button1" id="button1" onclick="document.write('<?php dispme() ?>');">Click the shit out of me</button>

<?php
function dispme(){
echo "button pressing baby hj ";

}


?>
<br>
<?php 

$mystring = system('python test.py', $retval);
echo $retval;

?>


<p>
<h1> yahoo Current charts 3 months  </h1>
<img src="http://chart.finance.yahoo.com/z?s=SIRO&t=3m&q=c&l=on&z=l&p=m10,m20,m50,m100,m200," alt="HTML5 Icon">

<h1> yahoo Current charts 6 months  </h1>
<img src="http://chart.finance.yahoo.com/z?s=SIRO&t=6m&q=c&l=on&z=l&p=m10,m20,m50,m100,m200," alt="HTML5 Icon">

<h1> yahoo Current charts 1 year  </h1>
<img src="http://chart.finance.yahoo.com/z?s=SIRO&t=1y&q=c&l=on&z=l&p=m10,m20,m50,m100,m200," alt="HTML5 Icon">

<h1> yahoo Current charts 2 year  </h1>
<img src="http://chart.finance.yahoo.com/z?s=SIRO&t=2y&q=c&l=on&z=l&p=m10,m20,m50,m100,m200," alt="HTML5 Icon">


</p>



<div id="chart_div" style="width: 1500px; height: 700px;"></div>

<script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart", 'line']});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable(
[
         ['Mon', 25, 28, 38, 38,10,10,10,10],
         ['Tue', 35, 38, 55, 55,20,10,10,10],
         ['Wed', 50, 55, 77, 77,40,10,10,10],
         ['Thu', 72, 77, 66, 66,60,10,10,10],
	 ['Thu', 72, 77, 66, 66,80,10,10,10],
         ['Fri', 62, 66, 22, 22,100,10,10,10]
        ], true);

        var options = {
          legend: 'none',
          bar: { groupWidth: '60%' }, // Remove space between bars.
          candlestick: {
	    hollowIsRising: true,	
            fallingColor: { strokeWidth: 0, fill: '#a52714' }, // red
            risingColor: { strokeWidth: 0, fill: '#0f9d58' }   // green
          },
	  series: {5:{type: "line",color: 'black'}},
	  hAxis: {title: 'Hellooooo',  titleTextStyle: {color: '#FF0000'}}
	  
        };

        var chart = new google.visualization.CandlestickChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>

<div id="chart_div2" style="width: 1500px; height: 700px;"></div>

<script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart", 'line',"bars"]});
      google.setOnLoadCallback(drawChart2);
      function drawChart2() {
        var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Dummy');
  data.addColumn('number', 'Range');
  data.addColumn({type: 'number', role: 'interval'});
  data.addColumn({type: 'number', role: 'interval'});
  data.addColumn('number', 'Trend');
  data.addRows([
    ['Mon', 28, 10, -8, 17, 42.8],
    ['Tue', 38, 17, -7, 28, 47.5],
    ['Wed', 55, 22, -5, 25, 52.2],
    ['Thu', 66, 11, -16, 11, 56.9],
    ['Fri', 22, 44, -7, 44, 61.6],
  ]);

  // Create and draw the visualization.
  var ac = new google.visualization.ComboChart(document.getElementById('chart_div2'));
  ac.draw(data, {
    title : 'Monthly Coffee Production by Country',
    isStacked: true,
    seriesType: "bars",
    series: {0: {color: 'transparent'}, 2: {type: "line"}}
  });
    </script>
</body>
</html>

