     <!DOCTYPE HTML>
<html>
<head>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script src="https://code.jquery.com/jquery-1.10.2.js"></script>
<script src="CommDataFuncs.js" type="text/javascript"></script>
<style type="text/css" media="screen">

	/*====================================================
		- html elements
	=====================================================*/
	body{ 
		margin:15px; padding:15px; border:1px solid #666;
		font-family:Arial, Helvetica, sans-serif; font-size:88%; 
	}
	h2{ margin-top: 50px; }
	pre{ margin:5px; padding:5px; background-color:#f4f4f4; border:1px solid #ccc; }
	/* for elements added by sortable.js in th tags*/
	th img{ border:0; } 
	th a{ color:#fff; font-size:13px; text-transform: uppercase; text-decoration:none; }
	
</style>

<script src="TableFilter/tablefilter_min.js" language="javascript" type="text/javascript"></script>
<!-- Additional imported module needed for this demo  -->
<script src="TableFilter/TF_Modules/tf_paging.js" language="javascript" type="text/javascript"></script>

<script src="TableFilter/sortabletable.js" language="javascript" type="text/javascript"></script>
<script src="TableFilter/tfAdapter.sortabletable.js" language="javascript" type="text/javascript"></script> 

<script type="text/javascript" language="javascript">
    function moveWindow (){window.location.hash="tableanchor";}
</script>

<script language="javascript" type="text/javascript"> 
//<![CDATA[
	tf_AddEvent(window,'load',initHighlighter);
	function initHighlighter()
	{
		dp.SyntaxHighlighter.ClipboardSwf = "includes/SyntaxHighlighter/Scripts/clipboard.swf";  
		dp.SyntaxHighlighter.HighlightAll("code"); 
	}
	
	/*** IE only: show/hide selects during filtering operations ***/
	function hideIESelects()
	{
		if(tf_isIE)
		{
			var slc = tf.tbl.getElementsByTagName('select');
			for(var i=0; i<slc.length; i++)
				slc[i].style.visibility = 'hidden';
		}
	}
	
	function showIESelects()
	{
		if(tf_isIE)
		{
			var slc = tf.tbl.getElementsByTagName('select');
			for(var i=0; i<slc.length; i++)
				slc[i].style.visibility = 'visible';
		}
	}
//]]>
</script>

<style type="text/css">
        #scrolly{
			border-radius: 2px;
            width: 1200px;
            height: 300px;
            overflow: auto;
            overflow-y: hidden;
            margin: 0 auto;
            white-space: nowrap
        }

        .imgscroll{
            width: 250px;
            height: 150px;
            margin: 20px 10px;
            display: inline;
        }
    </style>
    
    <style>
		.simpselect{
			width:300;
			width:300px;
			overflow-x:auto;
			overflow-y:auto;
		}
		
	   .scrltab{
            width: 1000px;
            height: 250px;
            overflow: auto;
            overflow-y: hidden;
            margin: 0 auto;
            white-space: nowrap;
        }	
        .Qview{
			overflow:auto; 
			width: 400px;
			margin: 1 auto;
		}
	</style>
</head>
<body>
<script>
	var GlobalQuerystr = [];
	var GlobalQueryids = [];
</script>	




<?php

$QYResetstr='';
$QYDetailstr="";
$result="";
if (isset($_POST['resetbtn']))
{
  $QYDetailstr="";
}
else{  

	if ($_SERVER["REQUEST_METHOD"] == "POST") {
		
		if (empty($_POST["telnum"])) {
		 
	   } else {
		 $QYDetailstr = test_input($_POST["telnum"]);
		 $output = array();
			$start = microtime(true);
			$result = shell_exec("/home/nagnanamus/miniconda3/bin/python3.4 GetHTMLtables.py "."\"".$QYDetailstr."\"");	
			$end = microtime(true);



	   }
	  
	}
}


function test_input($data) {
   $data = trim($data);
   $data = stripslashes($data);
   $data = htmlspecialchars($data);
   return $data;
}

echo "<br>";

$coldict=json_decode(file_get_contents('ColmCodes.txt'), true);



?>

<h1>  Data Analysis for Trading  -  Filter/Search stocks by Charts, Patterns, Features or Correlation </h1>


<div id="queryformdiv">
	<h2>  Load Standard Tables<h2>
	<table align="center">
	<tr>
		<td><button style="width:200px;height:60px;font-size: 90%" id="sendStdCorrTab" form="queryform" type="submit">Correlation and Charts</button>  </td>
		<td><button style="width:300px;height:60px;font-size: 90%" id="sendStdLinFeatChartTab" form="queryform" type="submit">Linear Trend Features and Charts</button> </td> 
		<td><button style="width:200px;height:60px;font-size: 90%" id="sendStdFeatChartTab" form="queryform" type="submit">Features and Charts</button> </td>  
	</tr>
	</table>
	<h2> Refine or Create New Custom Tables  </h2> 
	
<form method="post" id="queryform" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">

	<table border="1" align="center">


	<tr>
		<td align="center"> 
			<table>
				<tr><td align="center"> Reference Date (Y-M-D) Range -</td></tr>
				<tr><td align="center"> From : <select name="T0" id="T0">
		
		
				<?php
				
					echo nl2br("<option value=\"None\" selected> Select</option> \n ");
				
				
				$file = fopen("GeneralRefDates.csv","r");
				$k=0;
				while(! feof($file))
				{
					$dt[$k]=fgetcsv($file);
					echo nl2br("<option value=".$dt[$k][0].">".$dt[$k][0]."</option> \n ");
					
					$k=$k+1;
				}
				echo '</select>
				To : <select name="Tf"  id="Tf">';
				echo nl2br("<option value=\"None\" selected> Select</option> \n ");
				
				$s=0;
				while($s<$k)
				{
					echo nl2br("<option value=".$dt[$s][0].">".$dt[$s][0]."</option> \n ");
					$s=$s+1;
				}
				fclose($file);
				?>
				
				</select> </td></tr>
				<tr><td align="center"><input type="button" onclick="adddaterange()" value="Add Date Range"/> </td></tr>
			</table>
		
		</td>
	
		<td align="center">
			<table>
			 <tr><td align="center">Limit Number of rows to : </td></tr> 
			 <tr><td align="center"> <select name="limitto" id="limitto">
				 <option  value="None" selected> Select</option>
				 <option  value="50"> 50</option>
				 <option  value="100"> 100</option>
				 <option  value="200"> 200</option>
				 <option  value="300"> 300</option>
				 <option  value="400"> 400</option>
				 <option  value="500"> 500</option>
				 <option  value="1000"> 1000</option>
				 <option  value="All rows"> All rows</option>
			 </select></td></tr>
			 
			 <tr><td align="center"><input type="button" onclick="addlimitrows()" value="Add # of rows"/></td></tr> 
			 </table>
		</td>	
		

		<td align="center">
			<table>
				 <tr><td align="center">Limit to window length : </td></tr>
				 <tr><td align="center"><select name="windlen" id="windlen">
					 <option  value="None" selected> Select</option>
					 <option value="4mon">4 months</option>
					 <option value="6mon">6 months</option>
					 <option value="1y">1 year</option>
					 <option value="2y">2 years</option>
				 </select></td></tr>
			</table>
		</td>	
			
		<td rowspan="3"> Pre-view Query Request<p> <font color="blue"> <textarea rows="15" class="Qview" form="queryform" id="telnum" name="telnum"><?php echo $QYDetailstr; ?></textarea></font> </p>	</td>	
	</tr>
	
	
	<tr>
		<td align="center">
			<table>
				
				<tr><td align="center">Select the columns for Display: </td></tr>
				 <tr><td align="center"><div class="simpselect">
					 <select  multiple name="colms" id="colms" size="10">
					 <option value="None"  selected> Select</option>
					 
					 <option value="Sector" > Sector</option>
					 <option value="Industry" > Industry </option>
					 <option value="Stock/ETF" > Stock/ETF </option>
					 
					 
					 <option value="Chart3m" > 3mon chart for Window End date</option>
					 <option value="Chart6m" > 6mon chart for Window End date</option>
					 <option value="Chart1y" > 1y chart for Window End date</option>
					 <option value="Chart2y" > 2y chart for Window End date</option>
					 
					 <option value="Chart3m+6m" > 3mon chart for Window (End date+6mon)</option>
					 <option value="Chart3m+1y" > 3mon chart for Window (End date+1y)</option>
					 
					 <option value="Chart6m+6m" > 6mon chart for Window (End date+6mon)</option>
					 <option value="Chart6m+1y" > 6mon chart for Window (End date+1y)</option>
					 
					 <option value="Chart1y+6m" > 1y chart for Window (End date+6mon)</option>
					 <option value="Chart1y+1y" > 1y chart for Window (End date+1y)</option>
					 
					 <option value="Chart2y+6m" > 2y chart for Window (End date+6mon)</option>
					 <option value="Chart2y+1y" > 2y chart for Window (End date+1y)</option>
					 
					 <?php
					 foreach($coldict as $key=>$value ){
						echo nl2br("<option value=\"". $value["webcode"]."\">". $value["webcode"].":".$value["short"]. "</option>\n");
						} 
					?>
				 </select>
				 </div>
				 </td></tr>
				 <tr><td align="center"><input type="button" onclick="addcolumns()" value="Add columns"/> </td></tr>
			</table>
		 </td>	

		<td align="center">
			<table>
				<tr><td align="center">Filter by column: </td></tr>
				<tr><td align="center"><div class="simpselect">
					<select name="filtercol" id="filtercol" size="10" >
				 <option value="None"  selected> Select</option>
				 <option value="Sector" > Sector</option>
				 <option value="Industry" > Industry </option>
				 <option value="Stock/ETF" > Stock/ETF </option>
					 
				 <?php
					 foreach($coldict as $key=>$value ){
						echo nl2br("<option value=\"". $value["webcode"]."\">". $value["webcode"].":".$value["short"]. "</option>\n");
						} 
					?>
				</select>
				</div>
				</td></tr>
				<tr><td align="center"><input type="text" name="colfilter" id="colfilter" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td></tr>
				<tr><td align="center"> <input type="button" id="addfilcolbtn" onclick="addcolumnfilter()" value="Add column filter"/> </td></tr>
			</table>
		 </td>	
 
		<td align="center">
			<table>
				<tr><td align="center">Sort by column : </td></tr>
				<tr><td align="center"><div class="simpselect">
					<select name="sortcol" id="sortcol" size="10">
				 <option value="None"  selected> Select</option>
				 <?php
					 foreach($coldict as $key=>$value ){
						echo nl2br("<option value=\"". $value["webcode"]."\">". $value["webcode"].":".$value["short"]. "</option>\n");
						} 
					?>
				</select>
				</div>
				</td></tr>
				<tr><td align="center">
					<table>
					<tr><td align="center"> <input id="sortcolmord" type="radio" value="des" name="sortcolmord" checked > Descending </td></tr>
					<tr><td align="center"> <input id="sortcolmord" type="radio"  value="asc" name="sortcolmord"> Ascending </td></tr>
					</table>
				</td></tr>
		 
			</table>
		 </td>	
	
	</tr>
	
	<tr>
		<td align="center">	
		<table>
			<tr> <td align="center">Preferred Stock Tickers :</td></tr>
			<tr> <td align="center"> <input type="text" id="stk" ></td></tr>
			<tr> <td align="center"><input type="button" id="addstockbtn" onclick="addstock()" value="Add"/> </td></tr>
		</table>	
		</td>
		
		<td align="center">   
			<table style="table-layout: fixed">
		<tr><td><input  type="checkbox" id="normwind" name="normwind" value="normwind">  Normalize Data to <br>
		window length </td></tr>
			</table>
		
		</td>
		<td align="center"> </td>
	</tr>
	
	</table>
	 <div id='scrolly'>
		 Add Pattern correlation columns and filters 
		<table border="1" class="scrltab" >
			<tr>
      <td align="center"> <img class="imgscroll" src="LinearTrendFit_A_120_20_2006-05-14.png"> </td>
      <td align="center"> <img class="imgscroll" src="LinearTrendFit_A_120_20_2006-05-14.png"></td>
      <td align="center"> <img class="imgscroll" src="LinearTrendFit_A_120_20_2006-05-14.png"></td>
      <td align="center"> <img class="imgscroll"  src="LinearTrendFit_A_120_20_2006-05-14.png"></td>
      <td align="center"> <img class="imgscroll"  src="LinearTrendFit_A_120_20_2006-05-14.png"></td>
      <td align="center"> <img class="imgscroll"  src="LinearTrendFit_A_120_20_2006-05-14.png"></td>
			</tr>
       <tr>
		   <td align="center">P1<input  onclick="addpattcolfil(1)" type="checkbox" id="pattcorr1" name="pattcorr1" value="P1"> <input type="text" name="pattcorrfilter1" id="pattcorrfilter1" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		   <td align="center">P2<input  onclick="addpattcolfil(2)" type="checkbox" id="pattcorr2" name="pattcorr2" value="P2"> <input type="text" name="pattcorrfilter2" id="pattcorrfilter2" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		   <td align="center">P3<input  onclick="addpattcolfil(3)" type="checkbox" id="pattcorr3" name="pattcorr3" value="P3"> <input type="text" name="pattcorrfilter3" id="pattcorrfilter3" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		   <td align="center">P4<input  onclick="addpattcolfil(4)" type="checkbox" id="pattcorr4" name="pattcorr4" value="P4"> <input type="text" name="pattcorrfilter4" id="pattcorrfilter4" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		   <td align="center">P5<input  onclick="addpattcolfil(5)" type="checkbox" id="pattcorr5" name="pattcorr5" value="P5"> <input type="text" name="pattcorrfilter5" id="pattcorrfilter5" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		   <td align="center">P6<input  onclick="addpattcolfil(6)" type="checkbox" id="pattcorr6" name="pattcorr6" value="P6"> <input type="text" name="pattcorrfilter6" id="pattcorrfilter6" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value="filter expression"></td>
		</tr>
       </table>
    </div>
    
</form>


    
	
<p align="center">
	<button style="width:200px;height:50px;color: green;font-size: 180%" id="sendQ" form="queryform" type="submit">Send Query</button>  
	<input  style="width:100px;height:40px;color: red;font-size: 150%" name="resetbtn" form="queryform" type="submit" value="Reset" />
</p>
</div>
<hr>
    
    
    
    
    
<h2>Query Table </h2>
<a id='tableanchor' href='#'></a> 
<?php
if (empty($result)==false) {

echo "Requested query of  .... ";
echo $QYDetailstr;
echo " ... took ";
$finish = $end - $start;
echo $finish;
echo "<br>";
echo $result;
}
?>








<script>
	$(document).ready(function() {
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
});

$("#stk").keyup(function(event){
    if(event.keyCode == 13){
        $("#addstockbtn").click();
    }
});

	$("#colfilter").keyup(function(event){
    if(event.keyCode == 13){
        $("#addfilcolbtn").click();
    }
});


	function inputFocus(i){
    if(i.value==i.defaultValue){ i.value=""; i.style.color="#000"; }
    
	}
function inputBlur(i){
    if(i.value==""){ i.value=i.defaultValue; i.style.color="#888"; }
    
	}

	  $( "#normwind")
	.change(
	function () {
		var lfckv = document.getElementById("normwind").checked;
		var strlimitto;
		if(lfckv==true)
		{
			InsertGlobalQueries("normwind","True");
		}
		else{
			//InsertGlobalQueries("normwind","False");
		}
		
		LoadStrs2textareas();
		
	})
	.change();  
	
	  $( "#windlen")
	.change(
	function () {

		var e = document.getElementById("windlen");
		var strlimitto = e.options[e.selectedIndex].value;
		if (strlimitto=="None"){
			return;
		}
		
		InsertGlobalQueries("windlen",strlimitto);
		LoadStrs2textareas();
		
	})
	.change();  
	// sort by col
	$( "#sortcol")
	.change(
	function () {
		
		var sortcolord=$('input[name=sortcolmord]:checked').val();
		//document.getElementById("colmstr").value= sortcolord;
		
		var e = document.getElementById("sortcol");
		var strlimitto = e.options[e.selectedIndex].value;
		if (strlimitto=="None"){
			return;
		}	
		
		
			if(sortcolord=="des"){
				GlobalQueryids.push("sortcol");
				GlobalQuerystr.push(["des",strlimitto]);
			}
			else{
				GlobalQueryids.push("sortcol");
				GlobalQuerystr.push(["asc",strlimitto]);
			}			

		LoadStrs2textareas();
		
	})
	.change();	
	
	//style="display:none;"

	// Just combine as per requersst
	function LoadStrs2textareas(){
		var str="";
		var sstt="";
		for(i=0;i<GlobalQuerystr.length;i++){
			
			if(GlobalQueryids[i]=="limitto"){
			str=str+"limit to #rows : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="Dtrng"){
			str=str+"Limit to Date Range : "+GlobalQuerystr[i][0]+" to "+GlobalQuerystr[i][1]+",\r\n";
			}
			if(GlobalQueryids[i]=="windlen"){
			str=str+"limit to Window length : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="colms"){
			str=str+"Columns to display : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="Stocks"){
			str=str+"Limit to Tickers : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="filtercol"){
			str=str+"Filter by column : "+GlobalQuerystr[i][0]+" using '"+GlobalQuerystr[i][1]+"',\r\n";
			}
			if(GlobalQueryids[i]=="normwind"){
			str=str+"Normalize data to window length : "+GlobalQuerystr[i]+",\r\n";
			}
			
			if(GlobalQueryids[i]=="sortcol"){
				if(GlobalQuerystr[i][0]=="asc"){
					str=str+"Sort(ascending) Table by column : "+GlobalQuerystr[i][1]+",\r\n";
				}
				else{
					str=str+"Sort(descending) Table by column : "+GlobalQuerystr[i][1]+",\r\n";
				}
			}
			//pattcollarray =[  [P1,filter1],  [P2,filter2] , .....]
			if(GlobalQueryids[i]=="patcolfil"){
				var pattcollarray =GlobalQuerystr[i];
				var a="Patt. Corr. Filter: ";
				
				for(j=0;j<pattcollarray.length;j++){
					a=a+pattcollarray[j][0]+" using '"+pattcollarray[j][1]+"'; ";
				}
				str=str+a+",\r\n";
			}
			
			sstt=sstt+GlobalQueryids[i]+",";
		}
		document.getElementById("telnum").value= str;
		//document.getElementById("Qorder").value= sstt;
	}

	function InsertGlobalQueries(id,Qstr){
		
		var flg=0;
        for(i=0;i<GlobalQueryids.length;i++){
			if(GlobalQueryids[i]==id){
				flg=1;
				break;
			}
		}
		if(flg==1){
			GlobalQueryids[i]=id;
			GlobalQuerystr[i]=Qstr;
		
		}
		else{			

			GlobalQueryids.push(id);
			GlobalQuerystr.push(Qstr);
		}
	}
	

	
	// Limit to rows change function
	function addlimitrows() {
		var e = document.getElementById("limitto");
		var strlimitto = e.options[e.selectedIndex].value;
		e.selectedIndex=0;
		if (strlimitto=="None"){
			return;
		}	
				
		GlobalQueryids.push("limitto");
		GlobalQuerystr.push(strlimitto);

		LoadStrs2textareas();
		
	}
		
	// Daterange function
	function adddaterange() {
		var e = document.getElementById("T0");
		var strlimitT0 = e.options[e.selectedIndex].value;
		e.selectedIndex=0;
		var e = document.getElementById("Tf");
		var strlimitTf = e.options[e.selectedIndex].value;
		e.selectedIndex=0;
		
		GlobalQueryids.push("Dtrng");
		GlobalQuerystr.push([strlimitT0,strlimitTf]);
		
		LoadStrs2textareas();
		
	}


	
    function addstock(){
	  var str1=document.getElementById("stk").value.toUpperCase();
	  var str=str1.split(/[ ,]+/).filter(function(v){return v!==''}).join(',');
	  var strarray = str.split(",");
	  //var stk=document.getElementById("stocks").value;
	  var stkarray;
	  if(GlobalQueryids.indexOf("Stocks")<0){
		stkarray=[];
	  } 
	  else{
		stkarray = GlobalQuerystr[GlobalQueryids.indexOf("Stocks")].split(/[ ,]+/).filter(function(v){return v!==''});
	   }
	   
	  var flg=0;
	  for(i=0;i<strarray.length;i++){
		  flg=0;
		  for(j=0;j<stkarray.length;j++){
			if (stkarray[j]==strarray[i]){
				flg=-1;
				break;
			}
		  }
		  if(flg==0){
			stkarray.push(strarray[i]);
		  }
	  } 
	  var stk=stkarray.join(" ").toUpperCase();
	  document.getElementById("stk").value="";
	  
		InsertGlobalQueries("Stocks",stk);
		
		LoadStrs2textareas();
			
  }
  
  function addcolumns(){

	  var strarray = $('#colms').val();
	  var stkarray=[];
	  if(GlobalQueryids.indexOf("colms")<0){
		stkarray=[];
	  } 
	  else{
		stkarray = GlobalQuerystr[GlobalQueryids.indexOf("colms")].split(/[ ,]+/).filter(function(v){return v!==''});
		
	   }


	  var flg=0;
	  for(i=0;i<strarray.length;i++){
		  flg=0;
		  for(j=0;j<stkarray.length;j++){
			if (stkarray[j]==strarray[i]){
				flg=-1;
				break;
			}
		  }
		  if(flg==0){
			stkarray.push(strarray[i]);
		  }
	  } 
	  var stk=stkarray.join(" ");
		

	  
		InsertGlobalQueries("colms",stk);
		
		LoadStrs2textareas();
		
  }

function addcolumnfilter(){
	
	
		var e = document.getElementById("filtercol");
		var strlimitto = e.options[e.selectedIndex].value;

		e.selectedIndex=0;
		if (strlimitto=="None"){
			return;
		}	
		var colfilter=document.getElementById("colfilter").value;
		if(colfilter.indexOf("fil")>=0 || colfilter.indexOf("exp")>=0 ){
			return;
		}
		GlobalQueryids.push("filtercol");
		GlobalQuerystr.push([strlimitto,colfilter]);

		LoadStrs2textareas();
}

 
function addpattcolfil(id){
	
		
		
		
		
		
		var lfckv = document.getElementById("pattcorr"+String(id)).checked;
	
		
		
		
		
		var colfilter=document.getElementById("pattcorrfilter"+String(id)).value;

		if(colfilter.indexOf("fil")>=0 || colfilter.indexOf("exp")>=0 ){
			colfilter="None";
		}
		
		var pattcollarray;
		if(GlobalQueryids.indexOf("patcolfil")<0){
		pattcollarray=[];
		}
		else{
		pattcollarray = GlobalQuerystr[GlobalQueryids.indexOf("patcolfil")];
		}

		//pattcollarray =[  [P1,filter1],  [P2,filter2] , .....]
		var flg=0;
		for(i=0;i<pattcollarray.length;i++){
			if(pattcollarray[i][0]==("P"+String(id))){
				
				flg=1;
				if(lfckv==false)
				{
					pattcollarray.splice(i, 1);
				}
				else{
					pattcollarray[i][1]=colfilter;
				}
				
			}
		}
		if(flg==0){
			pattcollarray.push([("P"+String(id)),colfilter]);
		}
		//GlobalQueryids.push("patcolfil");
		//GlobalQuerystr.push(pattcollarray);
		if(pattcollarray.length>0){
		InsertGlobalQueries("patcolfil",pattcollarray);
		LoadStrs2textareas();
		}
}


</script>

</body>
</html>
