<!DOCTYPE HTML>
<html>
<head>


</head>
<body>

<?php


$data = file_get_contents("AllStocksList.csv");
$symb = explode(PHP_EOL, $data);

//$symb=array("AAPL","TSLA","GOOG");
//sizeof($symb)
$kk=sizeof($symb);

if(strcmp($_POST["limitto"],"10")==0){
$kk=10;	
}
if(strcmp($_POST["limitto"],"100")==0){
$kk=100;	
}
if(strcmp($_POST["limitto"],"1000")==0){
$kk=1000;	
}

$j=0;
echo "<font size=\"4\">Grade the charts. The results are stored at</font> <a href=\"https://docs.google.com/spreadsheets/d/1CP1I7sOymwuLgpjO3rDmRug8YLLY6hBiQdopAtiFqdU/edit#gid=198051896\" target=\"_blank\"><font size=\"6\">Google Spreadsheet</font></a>";
echo "<br><hr><br>";
echo '<table>';

for ($x = 0; $x <$kk; $x++){
if(strlen($symb[$x])<=4){
	if($j==0){
		echo '<tr>';
	}
echo "<td>";
echo '<img src="http://chart.finance.yahoo.com/z?s='.trim($symb[$x]).'&t='.$_POST["chartlen"].'&q=c&l=on&z=l&p=m10,m20,m50,v" style="width:350px;height:250px;">';
echo '<p align="center">';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',\'Flat\',0,0,0)">Flat</button> '; 
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,0,0,\'RndUp\')">Rnd Up</button> ';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,0,0,\'RndBtm\')">Rnd Btm</button> ';
echo "</p>";
echo '<p align="center">';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,\'ChnlUp\',0,0)">Chnl Up</button> ';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,\'ChnlDn\',0,0)">Chnl Dn</button> ';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,0,\'Buy\',0)">Buy</button> ';
echo ' <button onclick="postToGoogle_general(\''.trim($symb[$x]).'-'.$_POST["chartlen"].'\',0,0,\'Sell\',0)">Sell</button> ';
echo "</p>";
echo "</td>";

$j=$j+1;
if($j==4){
	echo '</tr>';
	$j=0;
}
}
}
echo '</table>';


?>








</body>
</html>
