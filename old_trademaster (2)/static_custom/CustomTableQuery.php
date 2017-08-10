 <!DOCTYPE HTML>
<html>
<head>
<script src="TableFilter/tablefilter_min.js" language="javascript" type="text/javascript"></script>
<script src="TableFilter/TF_Modules/tf_paging.js" language="javascript" type="text/javascript"></script>
<script src="TableFilter/sortabletable.js" language="javascript" type="text/javascript"></script>
<script src="TableFilter/tfAdapter.sortabletable.js" language="javascript" type="text/javascript"></script> 

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

</head>
<body>


<?php
//echo shell_exec("/home/nagavenkat/anaconda3/bin/python -V 2>&1");

$result=1;
if(!empty($_GET)) {
	echo "<p> <br>The Direct URL for this table is <br>\n";
	echo "<a href=\"http://nadurthi.ddns.net/bigdatatrading.com/CustomTableQuery.php?telnum=".urlencode($_GET["telnum"])."\" target=\"_blank\">" ;
	echo "http://nadurthi.ddns.net/bigdatatrading.com/CustomTableQuery.php?telnum=".urlencode($_GET["telnum"]);
	echo "</a>";
	echo "<br></p>";
	$result = shell_exec("/home/nagavenkat/anaconda3/bin/python python-finance/GetHTMLtables.py ".'"'.str_replace('"',"'",$_GET["telnum"]).'" 2>&1');
}
elseif(!empty($_POST)) {
	echo "IN POST<br>";
	print_r($_POST["telnum"]);
	echo "<br>";
	echo "/home/nagavenkat/anaconda3/bin/python python-finance/GetHTMLtables.py ".'"'.str_replace('"',"'",$_POST["telnum"]).'"';
	echo "\n<br>\n";
	$result = shell_exec("/home/nagavenkat/anaconda3/bin/python python-finance/GetHTMLtables.py ".'"'.str_replace('"',"'",$_POST["telnum"]).'" 2>&1');
}
echo $result;
echo "\n<br>\n";



?>



</body>
</html>
