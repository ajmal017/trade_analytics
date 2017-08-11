     <!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

<script src="TableFilter/tablefilter_min.js" language="javascript" type="text/javascript"></script>
<!-- Additional imported module needed for this demo  -->
<script src="TableFilter/TF_Modules/tf_paging.js" language="javascript" type="text/javascript"></script>

<script src="TableFilter/sortabletable.js" language="javascript" type="text/javascript"></script>
<script src="TableFilter/tfAdapter.sortabletable.js" language="javascript" type="text/javascript"></script> 


<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script src="https://code.jquery.com/jquery-1.10.2.js"></script>
<script src="CommDataFuncs.js" type="text/javascript"></script>

<script language="JavaScript">
<!--
function autoResize(id){
    var newheight;
    var newwidth;

    if(document.getElementById){
        newheight = document.getElementById(id).contentWindow.document .body.scrollHeight;
        newwidth = document.getElementById(id).contentWindow.document .body.scrollWidth;
    }

    document.getElementById(id).height = (newheight) + "px";
    document.getElementById(id).width = (newwidth) + "px";
}
//-->
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


<script type="text/javascript" >
function SendForm() {

var ddformserial=$("#queryform").serialize();

var xmlhttp;
        if (window.XMLHttpRequest) {
            // code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp = new XMLHttpRequest();
        } else {
            // code for IE6, IE5
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        //document.getElementById("tableout").innerHTML = xmlhttp.responseText;
        $( "#tableout" ).empty().append( xmlhttp.responseText);

            }
        }
        xmlhttp.open("POST","CustomTableQuery.php",true);
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send(ddformserial);
        $("#tableout").load(location.href + " #tableout");

}   
function ResetForm(){
document.getElementById("queryform").reset();
GlobalQuerystr = [];
GlobalQueryids = [];
document.getElementById("telnum").value= "";
document.getElementById("tableout").innerHTML ="";
}




</script>


<script>
	var GlobalQuerystr = [];
	var GlobalQueryids = [];
</script>	

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
    

	
<style TYPE="text/css">

body
{
scrollbar-base-color: orange;
scrollbar-arrow-color: green;
scrollbar-DarkShadow-Color: blue;
}
</style>


</head>
<body>


<h1>  Data Analysis for Trading  -  Filter/Search stocks by Charts, Patterns, Features or Correlation </h1>





target="my_iframe"
<div id="queryformdiv">
 <form method="get" id="queryform" action="CustomTableQuery.php" target="my_iframe">
<!--	<form method="post" id="queryform" action="javascript:SendForm();"> -->
<!-- <form method="get" id="queryform" target="_blank" action="CustomTableQuery.php"> -->
	<h2>  Load Standard Tables</h2>
	<table align="center">
	<tr>
		<td align="center"><button style="width:250px;height:60px;font-size: 100%" id="sendStdCorrTab" form="queryform" type="submit">Latest Correlation Table and Charts</button>  </td>
		<td align="center"><button style="width:250px;height:60px;font-size: 100%" id="sendStdLinFeatChartTab" form="queryform" type="submit">Table of Latest Linear Trend Features  and Charts</button> </td> 
		<td align="center"><button style="width:250px;height:60px;font-size: 100%" id="sendChartGradeTab" form="queryform" type="submit">Latest Charts and Grading</button> </td>  
		<td align="center"><button style="width:250px;height:60px;font-size: 100%" id="sendPattCorrtubeChartTab" form="queryform" type="submit">Latest Pattern and Tube Charts</button> </td>  
	</tr>
	</table>
<h2>  or Create New Custom Tables  </h2> 
	<table border="1" align="center">


	<tr>
		<td align="center"> 
			<table>
				<tr><td align="center"> Reference Date (Y-M-D) Range -</td></tr>
				<tr><td align="center"> From : <select name="T0" id="T0">
		
		
				<?php
				
					echo nl2br("<option value=\"None\" selected> Select</option> \n ");
				
				
				 $file = file_get_contents("GeneralRefDates.csv","r");

                                 $k=0;
                                 $dt= explode(PHP_EOL, $file);

				
				for($x = count($dt)-2; $x >=0; $x--)
				{
					echo "<option value=".$dt[$x].">".$dt[$x]."</option> \n";
				}
				echo '</select>
				To : <select name="Tf"  id="Tf">';
				echo nl2br("<option value=\"None\" selected> Select</option> \n ");
				
				for($x = 0; $x <count($dt)-1; $x++)
				{
                                        echo "<option value=".$dt[$x].">".$dt[$x]."</option>  \n";
				}
				
				?>
				
				</select> </td></tr>
				<tr><td align="center"><input type="button" onclick="adddaterange()" value="Add Date Range"/> </td></tr>
			</table>
		
		</td>
	
		<td align="center">
			<table>
			 <tr><td align="center">Limit Number of rows to : </td></tr> 
			 <tr><td align="center"> <select id="limitto">
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
			
		<td rowspan="3"> Pre-view Query Request <p> <font color="blue"> <textarea rows="15" class="Qview" form="queryform" id="telnum" name="telnum">Query in order ... </textarea></font> </p>	<p align="center">  <input type="button"  onclick="DeleteLastEntry()" value="Delete last entry"/>    </p>  </td>	
</tr>



	
	
	<tr>
		<td align="center">
			<table>
				
				<tr><td align="center">Select the columns for Display: </td></tr>
				 <tr><td align="center"><div class="simpselect">
					 <select  multiple name="colms" id="colms" size="10">
					 <option value="None"  selected> Select</option>
					 

					 
					 <?php
                                         $coldict=json_decode(file_get_contents('ColmCodes.txt'), true);
					 foreach($coldict as $key=>$value ){
					 	if(strcmp($value["Disp"],"Yes")==0){
						echo nl2br("<option value=\"(". $value["webcode"].")\">". $value["webcode"].":".$value["short"]. "</option>\n");
						}
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
					<select name="filtercol" id="filtercol" ondblclick="filtercoladd()" size="10" >
				 <option value="None"  selected> Select</option>

					 
				 <?php
                                         $coldict=json_decode(file_get_contents('ColmCodes.txt'), true);
					 foreach($coldict as $key=>$value ){
					 	if(strcmp($value["FilterDisp"],"Yes")==0){
						echo nl2br("<option value=\"(". $value["webcode"].")\">". $value["webcode"].":".$value["short"]. "</option>\n");
						}
						} 
				 ?>

				</select>
				</div>
				</td></tr>
				<tr><td align="center"><input type="text" name="colfilter" id="colfilter" onfocus="inputFocus(this)" onblur="inputBlur(this)" style="color:#888;" value=""></td></tr>
				 <tr>   <td align="center"> <input type="button" id="addfilcolbtn" onclick="resetcolumnfilter()" value="Reset column filter"/> </td></tr>
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
                                         $coldict=json_decode(file_get_contents('ColmCodes.txt'), true);
					 foreach($coldict as $key=>$value ){
					 	if(strcmp($value["SortDisp"],"Yes")==0){
						echo nl2br("<option value=\"(". $value["webcode"].")\">". $value["webcode"].":".$value["short"]. "</option>\n");
						}
						} 
				 ?>

				</select>
				</div>
				</td></tr>
				<tr><td align="center">
					<table>
					<tr>
						<td align="center"> <input id="sortcolmord" type="radio" value="des" name="sortcolmord" checked > Descending </td> 
						<td align="center"> <input id="sortcolmord" type="radio"  value="asc" name="sortcolmord"> Ascending </td>
					</tr>
					<tr>
						<td align="center"> <input type="button" id="addsortcolbtn" onclick="addsortcolumn()" value="Add sort by column"/> </td>
					</tr>
					</table>
				</td></tr>
		 
			</table>
		 </td>	
	
	</tr>
	
	<tr>
		<td align="center">	
		<table>
			<tr> 
				<td align="left">Preferred Stock Tickers </td> 
				<td align="center"> <input type="text" id="stk" value=""></td>
				<td align="center"><input type="button" id="addstockbtn" onclick="addstock()" value="Add"/> </td> 
				
			</tr>
			<tr> 
				<td align="right">limit correlated stocks to</td> 
				<td align="center"> <input type="text" id="stkcorr" value=""></td> 
				<td align="center"><input type="button" id="addstockcorrbtn" onclick="addstockcorr()" value="Add"/> </td>
			</tr>
		
		</table>	
		</td>
		
		<td align="center">   
			<table style="table-layout: fixed">
				<tr>
					<td><input  type="checkbox" id="normwind" name="normwind" value="normwind">  Normalize Data to window length </td>
				</tr>
				<tr>	
					<td><input  type="checkbox" id="gradeoption" name="gradeoption" value="gradeoption">  Add Grade option </td>
				</tr>

			</table>
		</td>
		<td align="center">   
			<table style="table-layout: fixed">
				<tr>
					
				</tr>
			</table>
		</td>
	</tr>
	
	</table>
	
	
	 <div id='scrolly' >
		 Add Pattern correlation columns and filters 
		<table border="1" class="scrltab" style="width:100%">
			<tr>
      <td align="center"> <img class="imgscroll" src="customdir/P1.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P2.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P3.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P4.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P5.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P6.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P7.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P8.png"> </td>
      <td align="center"> <img class="imgscroll" src="customdir/P9.png"> </td>
			</tr>
			<tr>
      <td align="center"> P1 </td>
      <td align="center"> P2 </td>
      <td align="center"> P3 </td>
      <td align="center"> P4 </td>
      <td align="center"> P5 </td>
      <td align="center"> P6 </td>
      <td align="center"> P7 </td>
      <td align="center"> P8 </td>
      <td align="center"> P9 </td>
			</tr>

		
       </table>
    </div>

    
    
</form>


    
	
<p align="center">
	<button style="width:200px;height:50px;font-size: 180%" id="sendQ" form="queryform" type="submit">Send Query</button>  
	<button style="width:100px;height:40px;font-size: 100%" onclick="ResetForm()"> Reset </button>
</p>
</div>
<hr>

    <h2>  Table Query </h2>    




<div id="tableout"> Table.... </div>    
    
<iframe name="my_iframe" width="100%" height="200px" id="my_iframe" marginheight="0" frameborder="0" onLoad="autoResize('my_iframe');"></iframe>   
    
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
			InsertGlobalQueries("normwind","False");
		}
		
		LoadStrs2textareas();
		
	})
	.change(); 

// construct the column filter and then add them
function filtercoladd(){
    
    var e = document.getElementById("filtercol");
    var strlimitto = e.options[e.selectedIndex].value;
    e.selectedIndex=0;
    if (strlimitto=="None"){
	return;
     }

     document.getElementById("colfilter").value = document.getElementById("colfilter").value.concat(strlimitto);
     var val=document.getElementById("colfilter").value
     document.getElementById("colfilter").focus().val("").val(v);	
    //colfilter
}
	
	
		
	  $( "#gradeoption")
	.change(
	function () {
		var lfckv = document.getElementById("gradeoption").checked;
		var strlimitto;
		if(lfckv==true)
		{
			InsertGlobalQueries("gradeoption","True");
		}
		else{
			InsertGlobalQueries("gradeoption","False");
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
	
/* 	// sort by col
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
	.change();	 */
	
	//style="display:none;"

function DeleteLastEntry(){
if(GlobalQueryids.length>0){ 
GlobalQueryids.pop();
GlobalQuerystr.pop();
LoadStrs2textareas();
}

}

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
			if(GlobalQueryids[i]=="Stockscorr"){
			str=str+"Limit to Correlated Tickers : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="filtercol"){
			str=str+"Filter by column : "+GlobalQuerystr[i][0]+" using '"+GlobalQuerystr[i][1]+"',\r\n";
			}
			if(GlobalQueryids[i]=="normwind"){
			str=str+"Normalize data to window length : "+GlobalQuerystr[i]+",\r\n";
			}
			if(GlobalQueryids[i]=="gradeoption"){
			str=str+"Add option to Grade entry : "+GlobalQuerystr[i]+",\r\n";
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
  function addstockcorr(){
	  var str1=document.getElementById("stkcorr").value.toUpperCase();
	  var str=str1.split(/[ ,]+/).filter(function(v){return v!==''}).join(',');
	  var strarray = str.split(",");
	  //var stk=document.getElementById("stocks").value;
	  var stkarray;
	  if(GlobalQueryids.indexOf("Stockscorr")<0){
		stkarray=[];
	  } 
	  else{
		stkarray = GlobalQuerystr[GlobalQueryids.indexOf("Stockscorr")].split(/[ ,]+/).filter(function(v){return v!==''});
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
	  document.getElementById("stkcorr").value="";
	  
		InsertGlobalQueries("Stockscorr",stk);
		
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
		//if (strlimitto=="None"){
		//	return;
		//}	
		var colfilter=document.getElementById("colfilter").value;
		if(colfilter.indexOf("fil")>=0 || colfilter.indexOf("exp")>=0 || colfilter.length==0 ){
			return;
		}
		
		if((colfilter.match(/>/g) || []).length==0 && (colfilter.match(/</g) || []).length==0 && (colfilter.match(/==/g) || []).length==0 ){
			alert(" filter needs a comparison >, <, |");
			return;
		}
	

		if( colfilter.match(/\(/g).length != colfilter.match(/\)/g).length  ){
			return;
		}
		
		var cc=colfilter.replace(/ /g,"");

		if( colfilter.match(/\)/g).length >=1  ){
			var n=0;

			while(n< colfilter.length){
				n=cc.indexOf(")",n);
				if(n<0){ break;}
				

				if ( cc.charAt(n+1)==">" || cc.charAt(n+1)=="<" || ( cc.charAt(n+1)=="=" && cc.charAt(n+2)=="=") ){
			
				}
				else{

					alert(" Column code should proceed with a >, <, ==");
					return;
				}
			 	n=n+1;

			}

		}
		
		if( colfilter.match(/\(/g).length >=2  ){
			var n=0;
			
			while(n< colfilter.length){
				n=cc.indexOf("(",n);
				if(n<0){ break;}
				if(n>0){  // after the first code
					if ( cc.charAt(n-1)=="&" || cc.charAt(n-1)=="|"  ){
			
					}
					else{
						alert(" need a &(and) or |(or) to combine multiple columns in the filter");
						return;
					}
				 	
				}
				n=n+1;
			}

		}
	
		
		GlobalQueryids.push("filtercol");
		GlobalQuerystr.push([strlimitto,colfilter]);

		LoadStrs2textareas();
		document.getElementById("colfilter").value="";
}

function resetcolumnfilter(){
	
		
			
		document.getElementById("colfilter").value="";
		
}

function addsortcolumn(){
	
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
		
		/* var e = document.getElementById("sortcol");
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

		LoadStrs2textareas(); */
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
			pattcollarray.push([("("+"P"+String(id)+")"),colfilter]);
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

