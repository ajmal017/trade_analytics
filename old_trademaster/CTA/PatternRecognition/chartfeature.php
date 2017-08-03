 <!DOCTYPE HTML>
<html>
<head>


</head>
<body>


<?php
$symb=strtoupper($_POST['stock']);
 if (empty($_POST['stock'])) {
echo "error";
}
echo "<p>";

echo "Stock Symbol received is ".$symb;



echo "</p>";
?>

<?php
// Now getting the yahoo data and getting its features
$stock = $symb;
$date = strtotime(date('Y-m-d') );
$date2 = strtotime(date('Y-m-d') . ' -3 years');

$a = (date('m', $date));
$b = (date('d', $date));
$c =(date('Y', $date));
$d = (date('m', $date2));
$e = (date('d', $date2));
$f =(date('Y', $date2));

$data = file_get_contents("http://ichart.yahoo.com/table.csv?s=$stock&a=$d&b=$e&c=$f&d=$a&e=$b&f=$c&g=d");
//$file = fopen('testdata.csv',"w");
//file_put_contents($file,$data);



$rows = explode("\n",$data);
$s = array();
foreach($rows as $row) {
    $s[] = str_getcsv($row);
}


$o=1;
$c=4;
$h=2;
$l=3;
$v=5;


if(sizeof($s)<504){
    echo "error: yahoo data received is not enough";
}

$sizzes=sizeof($s);

//calculating the smas
//$sma10 = array();
//$sma20 = array();
//$sma50 = array();
//$sma100 = array();

//$Vsma20 = array();

for($i=1;$i<$sizzes;$i++){

	$sma10[$i]=0;
	 for($j=$i;$j<min($i+10,$sizzes-1);$j++){
	 $sma10[$i]=$sma10[$i]+$s[$j][$c];
	}
	$sma10[$i]=$sma10[$i]/(min($i+10,$sizzes-1)-$i+0.0001);

	$sma20[$i]=0;
	 for($j=$i;$j<min($i+20,$sizzes-1);$j++){
	 $sma20[$i]=$sma20[$i]+$s[$j][$c];
	}
	$sma20[$i]=$sma20[$i]/(min($i+20,$sizzes-1)-$i+0.0001);
	
	$sma50[$i]=0;
	 for($j=$i;$j<min($i+50,$sizzes-1);$j++){
	 $sma50[$i]=$sma50[$i]+$s[$j][$c];
	}
	$sma50[$i]=$sma50[$i]/(min($i+50,$sizzes-1)-$i+0.0001);
	
	
	$sma100[$i]=0;
	 for($j=$i;$j<min($i+100,$sizzes-1);$j++){
	 $sma100[$i]=$sma100[$i]+$s[$j][$c];
	}
	$sma100[$i]=$sma100[$i]/(min($i+100,$sizzes-1)-$i+0.0001);
	
	$Vsma20[$i]=0;
	 for($j=$i;$j<min($i+20,$sizzes-1);$j++){
	 $Vsma20[$i]=$Vsma20[$i]+$s[$j][$v];
	}
	$Vsma20[$i]=$Vsma20[$i]/(min($i+20,$sizzes-1)-$i+0.0001);	
				
}
//echo "<br>SMA10 <br>";
//echo json_encode($sma10);
//echo "<br>SMA20 <br>";
//echo json_encode($sma20);
//echo "<br>SMA50 <br>";
//echo json_encode($sma50);
//echo "<br>SMA100 <br>";
//echo json_encode($sma100);
//echo "<br>VSMA20 <br>";
//echo json_encode($Vsma20);


/*  
$file = fopen('testdata10.csv',"w");
foreach ($sma10 as $line)
  {
  fputcsv($file,explode(',',$line));
  }
  
$file = fopen('testdata20.csv',"w");
foreach ($sma20 as $line)
  {
  fputcsv($file,explode(',',$line));
  }
  
$file = fopen('testdata50.csv',"w");
foreach ($sma50 as $line)
  {
  fputcsv($file,explode(',',$line));
  }
  
$file = fopen('testdata100.csv',"w");
foreach ($sma100 as $line)
  {
  fputcsv($file,explode(',',$line));
  }
  
$file = fopen('testdataV20.csv',"w");
foreach ($Vsma20 as $line)
  {
  fputcsv($file,explode(',',$line));
  }
*/  

//$yahoodata = file_get_contents($file);




//3 month  .... 1 nyr is 252 candles/trading days
$gapup=0;
$gapdown=0;

$greencandles=0;
$redcandles=0;

$Vspikegt2=0;
$Vspikegt4=0;
$Vspikegt6=0;
$Vspikegt8=0;



$SMA10gt20=0;
$SMA50gt100=0;
$SMA10gt20gt50=0;
$SMA20gt50gt100=0;
$SMA10gt20gt50gt100=0;


$Candlesgt10=0;
$Candlesgt20=0;


$maxrv=0;


$T=63;
for($i=1;$i<=$T;$i++){
	
    if($Vsma20[$i]>$maxrv){
        $maxrv=$Vsma20[$i];
        
    }
    // SMA over each other
    if($sma10[$i]>$sma20[$i]){
        $SMA10gt20=$SMA10gt20+1;
    }
    
    if($sma50[$i]>$sma100[$i]){
        $SMA50gt100=$SMA50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i]){
        $SMA10gt20gt50=$SMA10gt20gt50+1;
    }
    if($sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i]){
        $SMA20gt50gt100=$SMA20gt50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i] ){
        $SMA10gt20gt50gt100=$SMA10gt20gt50gt100+1;
    }
    // candles over sma
    if(max($s[$i][$o],$s[$i][$c])>$sma10[$i]){
        $Candlesgt10=$Candlesgt10+1;
    }
    if(max($s[$i][$o],$s[$i][$c])>$sma20[$i]){
        $Candlesgt20=$Candlesgt20+1;
    }
    
    
	//number of volume spikes
	if($s[$i][$v]>=2*$Vsma20[$i]){
	$Vspikegt2=$Vspikegt2+1;
	}
	if($s[$i][$v]>=4*$Vsma20[$i]){
	$Vspikegt4=$Vspikegt4+1;
	}
	if($s[$i][$v]>=6*$Vsma20[$i]){
	$Vspikegt6=$Vspikegt6+1;
	}
	if($s[$i][$v]>=8*$Vsma20[$i]){
	$Vspikegt8=$Vspikegt8+1;
	}

	// Number of green and red candles
	if(max($s[$i][$o],$s[$i][$c])<min($s[$i+1][$o],$s[$i+1][$c])){
	  $gapdown=$gapdown+1;
	}
	if(min($s[$i][$o],$s[$i][$c])>max($s[$i+1][$o],$s[$i+1][$c])){
	  $gapup=$gapup+1;
	}
	if($s[$i][$c]>$s[$i][$o]){
	  $greencandles=$greencandles+1;
	}
	if($s[$i][$o]>$s[$i][$c]){
	  $redcandles=$redcandles+1;
	}
}






echo "<p>";

echo '<h3> '.$symb.' : 3 month Current chart   </h3>';
echo "<p align=\"center\">";
echo '<img src="http://chart.finance.yahoo.com/z?s='.$symb.'&t=3m&q=c&l=on&z=l&p=m10,m20,m50,v" alt="HTML5 Icon">';
echo "</p>";
echo "<p><button onclick=\"return toggleme('.tab3m');\">Toggle Feature Table for 3 month chart</button></p>";

echo '<div class="tab3m" id="tab3m">';

echo "<p>";
echo "<table style=\"width:100%\" >";

echo "<tr>";
echo "<td># of Gap Ups =<font color=\"blue\"> ".((string) $gapup)." (".((string) 100*round($gapup/$T, 2))."%)"."</font></td>";  
echo "<td># of Gap Downs =<font color=\"blue\"> ".((string) $gapdown)." (".((string) 100*round($gapdown/$T, 2))."%)"."</font></td>";  
echo "<td># of Red/Down Candles = <font color=\"blue\">".((string) $redcandles)." (".((string) 100*round($redcandles/$T, 2))."%)"."</font></td>"; 
echo "<td># of Green/Up Candles = <font color=\"blue\">".((string) $greencandles)." (".((string) 100*round($greencandles/$T, 2))."%)"."</font></td>"; 
echo "</tr>";

echo "<tr>";
echo "<td># of Rel. Vols > 2  = <font color=\"blue\">".((string) $Vspikegt2)."</font></td>";  
echo "<td># of Rel. Vols > 4  = <font color=\"blue\">".((string) $Vspikegt4)."</font></td>";  
echo "<td># of Rel. Vols > 6  = <font color=\"blue\">".((string) $Vspikegt6)."</font></td>";  
echo "<td># of Rel. Vols > 8  = <font color=\"blue\">".((string) $Vspikegt8)."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td>Max Rel. Vol = <font color=\"blue\">".((string) $maxrv)."</font></td>"; 
echo "<td># of Candles > SMA10  = <font color=\"blue\">".((string) $Candlesgt10)." (".((string) 100*round($Candlesgt10/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles > SMA20  = <font color=\"blue\">".((string) $Candlesgt20)." (".((string) 100*round($Candlesgt20/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA = <font color=\"blue\">".((string) $SMA10gt20)." (".((string) 100*round($SMA10gt20/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td># of Candles 10SMA > 20SMA > 50SMA = <font color=\"blue\">".((string) $SMA10gt20gt50)." (".((string) 100*round($SMA10gt20gt50/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA50gt100)." (".((string) 100*round($SMA50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 20SMA > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA20gt50gt100)." (".((string) 100*round($SMA20gt50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA  > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA10gt20gt50gt100)." (".((string) 100*round($SMA10gt20gt50gt100/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "</table>";
echo "<p>";

echo "</div>";
echo "</p>";





//6 month  .... 1 nyr is 252 candles/trading days
$gapup=0;
$gapdown=0;

$greencandles=0;
$redcandles=0;

$Vspikegt2=0;
$Vspikegt4=0;
$Vspikegt6=0;
$Vspikegt8=0;



$SMA10gt20=0;
$SMA50gt100=0;
$SMA10gt20gt50=0;
$SMA20gt50gt100=0;
$SMA10gt20gt50gt100=0;


$Candlesgt10=0;
$Candlesgt20=0;


$maxrv=0;


$T=126;
for($i=1;$i<=$T;$i++){
	
    if($Vsma20[$i]>$maxrv){
        $maxrv=$Vsma20[$i];
        
    }
    // SMA over each other
    if($sma10[$i]>$sma20[$i]){
        $SMA10gt20=$SMA10gt20+1;
    }
    
    if($sma50[$i]>$sma100[$i]){
        $SMA50gt100=$SMA50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i]){
        $SMA10gt20gt50=$SMA10gt20gt50+1;
    }
    if($sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i]){
        $SMA20gt50gt100=$SMA20gt50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i] ){
        $SMA10gt20gt50gt100=$SMA10gt20gt50gt100+1;
    }
    // candles over sma
    if(max($s[$i][$o],$s[$i][$c])>$sma10[$i]){
        $Candlesgt10=$Candlesgt10+1;
    }
    if(max($s[$i][$o],$s[$i][$c])>$sma20[$i]){
        $Candlesgt20=$Candlesgt20+1;
    }
    
    
	//number of volume spikes
	if($s[$i][$v]>=2*$Vsma20[$i]){
	$Vspikegt2=$Vspikegt2+1;
	}
	if($s[$i][$v]>=4*$Vsma20[$i]){
	$Vspikegt4=$Vspikegt4+1;
	}
	if($s[$i][$v]>=6*$Vsma20[$i]){
	$Vspikegt6=$Vspikegt6+1;
	}
	if($s[$i][$v]>=8*$Vsma20[$i]){
	$Vspikegt8=$Vspikegt8+1;
	}

	// Number of green and red candles
	if(max($s[$i][$o],$s[$i][$c])<min($s[$i+1][$o],$s[$i+1][$c])){
	  $gapdown=$gapdown+1;
	}
	if(min($s[$i][$o],$s[$i][$c])>max($s[$i+1][$o],$s[$i+1][$c])){
	  $gapup=$gapup+1;
	}
	if($s[$i][$c]>$s[$i][$o]){
	  $greencandles=$greencandles+1;
	}
	if($s[$i][$o]>$s[$i][$c]){
	  $redcandles=$redcandles+1;
	}
}






echo "<p>";

echo '<h3> '.$symb.' : 6 month Current chart   </h3>';
echo "<p align=\"center\">";
echo '<img src="http://chart.finance.yahoo.com/z?s='.$symb.'&t=6m&q=c&l=on&z=l&p=m10,m20,m50,v" alt="HTML5 Icon">';
echo "</p>";
echo "<p><button onclick=\"return toggleme('.tab6m');\">Toggle Feature Table for 6 month chart</button></p>";

echo '<div class="tab6m" id="tab6m">';

echo "<p>";
echo "<table style=\"width:100%\" >";

echo "<tr>";
echo "<td># of Gap Ups =<font color=\"blue\"> ".((string) $gapup)." (".((string) 100*round($gapup/$T, 2))."%)"."</font></td>";  
echo "<td># of Gap Downs =<font color=\"blue\"> ".((string) $gapdown)." (".((string) 100*round($gapdown/$T, 2))."%)"."</font></td>";  
echo "<td># of Red/Down Candles = <font color=\"blue\">".((string) $redcandles)." (".((string) 100*round($redcandles/$T, 2))."%)"."</font></td>"; 
echo "<td># of Green/Up Candles = <font color=\"blue\">".((string) $greencandles)." (".((string) 100*round($greencandles/$T, 2))."%)"."</font></td>"; 
echo "</tr>";

echo "<tr>";
echo "<td># of Rel. Vols > 2  = <font color=\"blue\">".((string) $Vspikegt2)."</font></td>";  
echo "<td># of Rel. Vols > 4  = <font color=\"blue\">".((string) $Vspikegt4)."</font></td>";  
echo "<td># of Rel. Vols > 6  = <font color=\"blue\">".((string) $Vspikegt6)."</font></td>";  
echo "<td># of Rel. Vols > 8  = <font color=\"blue\">".((string) $Vspikegt8)."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td>Max Rel. Vol = <font color=\"blue\">".((string) $maxrv)."</font></td>"; 
echo "<td># of Candles > SMA10  = <font color=\"blue\">".((string) $Candlesgt10)." (".((string) 100*round($Candlesgt10/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles > SMA20  = <font color=\"blue\">".((string) $Candlesgt20)." (".((string) 100*round($Candlesgt20/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA = <font color=\"blue\">".((string) $SMA10gt20)." (".((string) 100*round($SMA10gt20/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td># of Candles 10SMA > 20SMA > 50SMA = <font color=\"blue\">".((string) $SMA10gt20gt50)." (".((string) 100*round($SMA10gt20gt50/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA50gt100)." (".((string) 100*round($SMA50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 20SMA > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA20gt50gt100)." (".((string) 100*round($SMA20gt50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA  > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA10gt20gt50gt100)." (".((string) 100*round($SMA10gt20gt50gt100/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "</table>";
echo "<p>";

echo "</div>";
echo "</p>";


//1 year  .... 1 nyr is 252 candles/trading days
$gapup=0;
$gapdown=0;

$greencandles=0;
$redcandles=0;

$Vspikegt2=0;
$Vspikegt4=0;
$Vspikegt6=0;
$Vspikegt8=0;



$SMA10gt20=0;
$SMA50gt100=0;
$SMA10gt20gt50=0;
$SMA20gt50gt100=0;
$SMA10gt20gt50gt100=0;


$Candlesgt10=0;
$Candlesgt20=0;


$maxrv=0;


$T=252;
for($i=1;$i<=$T;$i++){
	
    if($Vsma20[$i]>$maxrv){
        $maxrv=$Vsma20[$i];
        
    }
    // SMA over each other
    if($sma10[$i]>$sma20[$i]){
        $SMA10gt20=$SMA10gt20+1;
    }
    
    if($sma50[$i]>$sma100[$i]){
        $SMA50gt100=$SMA50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i]){
        $SMA10gt20gt50=$SMA10gt20gt50+1;
    }
    if($sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i]){
        $SMA20gt50gt100=$SMA20gt50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i] ){
        $SMA10gt20gt50gt100=$SMA10gt20gt50gt100+1;
    }
    // candles over sma
    if(max($s[$i][$o],$s[$i][$c])>$sma10[$i]){
        $Candlesgt10=$Candlesgt10+1;
    }
    if(max($s[$i][$o],$s[$i][$c])>$sma20[$i]){
        $Candlesgt20=$Candlesgt20+1;
    }
    
    
	//number of volume spikes
	if($s[$i][$v]>=2*$Vsma20[$i]){
	$Vspikegt2=$Vspikegt2+1;
	}
	if($s[$i][$v]>=4*$Vsma20[$i]){
	$Vspikegt4=$Vspikegt4+1;
	}
	if($s[$i][$v]>=6*$Vsma20[$i]){
	$Vspikegt6=$Vspikegt6+1;
	}
	if($s[$i][$v]>=8*$Vsma20[$i]){
	$Vspikegt8=$Vspikegt8+1;
	}

	// Number of green and red candles
	if(max($s[$i][$o],$s[$i][$c])<min($s[$i+1][$o],$s[$i+1][$c])){
	  $gapdown=$gapdown+1;
	}
	if(min($s[$i][$o],$s[$i][$c])>max($s[$i+1][$o],$s[$i+1][$c])){
	  $gapup=$gapup+1;
	}
	if($s[$i][$c]>$s[$i][$o]){
	  $greencandles=$greencandles+1;
	}
	if($s[$i][$o]>$s[$i][$c]){
	  $redcandles=$redcandles+1;
	}
}



echo "<p>";

echo '<h3> '.$symb.' : 1 year Current chart   </h3>';
echo "<p align=\"center\">";
echo '<img src="http://chart.finance.yahoo.com/z?s='.$symb.'&t=1y&q=c&l=on&z=l&p=m10,m20,m50,v" alt="HTML5 Icon">';
echo "</p>";
echo "<p><button onclick=\"return toggleme('.tab1y');\">Toggle Feature Table for 1 year chart</button></p>";

echo '<div class="tab1y" id="tab1y">';

echo "<p>";
echo "<table style=\"width:100%\" >";

echo "<tr>";
echo "<td># of Gap Ups =<font color=\"blue\"> ".((string) $gapup)." (".((string) 100*round($gapup/$T, 2))."%)"."</font></td>";  
echo "<td># of Gap Downs =<font color=\"blue\"> ".((string) $gapdown)." (".((string) 100*round($gapdown/$T, 2))."%)"."</font></td>";  
echo "<td># of Red/Down Candles = <font color=\"blue\">".((string) $redcandles)." (".((string) 100*round($redcandles/$T, 2))."%)"."</font></td>"; 
echo "<td># of Green/Up Candles = <font color=\"blue\">".((string) $greencandles)." (".((string) 100*round($greencandles/$T, 2))."%)"."</font></td>"; 
echo "</tr>";

echo "<tr>";
echo "<td># of Rel. Vols > 2  = <font color=\"blue\">".((string) $Vspikegt2)."</font></td>";  
echo "<td># of Rel. Vols > 4  = <font color=\"blue\">".((string) $Vspikegt4)."</font></td>";  
echo "<td># of Rel. Vols > 6  = <font color=\"blue\">".((string) $Vspikegt6)."</font></td>";  
echo "<td># of Rel. Vols > 8  = <font color=\"blue\">".((string) $Vspikegt8)."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td>Max Rel. Vol = <font color=\"blue\">".((string) $maxrv)."</font></td>"; 
echo "<td># of Candles > SMA10  = <font color=\"blue\">".((string) $Candlesgt10)." (".((string) 100*round($Candlesgt10/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles > SMA20  = <font color=\"blue\">".((string) $Candlesgt20)." (".((string) 100*round($Candlesgt20/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA = <font color=\"blue\">".((string) $SMA10gt20)." (".((string) 100*round($SMA10gt20/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td># of Candles 10SMA > 20SMA > 50SMA = <font color=\"blue\">".((string) $SMA10gt20gt50)." (".((string) 100*round($SMA10gt20gt50/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA50gt100)." (".((string) 100*round($SMA50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 20SMA > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA20gt50gt100)." (".((string) 100*round($SMA20gt50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA  > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA10gt20gt50gt100)." (".((string) 100*round($SMA10gt20gt50gt100/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "</table>";
echo "<p>";

echo "</div>";
echo "</p>";




//2 year  .... 1 nyr is 252 candles/trading days
$gapup=0;
$gapdown=0;

$greencandles=0;
$redcandles=0;

$Vspikegt2=0;
$Vspikegt4=0;
$Vspikegt6=0;
$Vspikegt8=0;



$SMA10gt20=0;
$SMA50gt100=0;
$SMA10gt20gt50=0;
$SMA20gt50gt100=0;
$SMA10gt20gt50gt100=0;


$Candlesgt10=0;
$Candlesgt20=0;


$maxrv=0;


$T=504;
for($i=1;$i<=$T;$i++){
	
    if($Vsma20[$i]>$maxrv){
        $maxrv=$Vsma20[$i];
        
    }
    // SMA over each other
    if($sma10[$i]>$sma20[$i]){
        $SMA10gt20=$SMA10gt20+1;
    }
    
    if($sma50[$i]>$sma100[$i]){
        $SMA50gt100=$SMA50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i]){
        $SMA10gt20gt50=$SMA10gt20gt50+1;
    }
    if($sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i]){
        $SMA20gt50gt100=$SMA20gt50gt100+1;
    }
    if($sma10[$i]>$sma20[$i] and $sma20[$i]>$sma50[$i] and $sma50[$i]>$sma100[$i] ){
        $SMA10gt20gt50gt100=$SMA10gt20gt50gt100+1;
    }
    // candles over sma
    if(max($s[$i][$o],$s[$i][$c])>$sma10[$i]){
        $Candlesgt10=$Candlesgt10+1;
    }
    if(max($s[$i][$o],$s[$i][$c])>$sma20[$i]){
        $Candlesgt20=$Candlesgt20+1;
    }
    
    
	//number of volume spikes
	if($s[$i][$v]>=2*$Vsma20[$i]){
	$Vspikegt2=$Vspikegt2+1;
	}
	if($s[$i][$v]>=4*$Vsma20[$i]){
	$Vspikegt4=$Vspikegt4+1;
	}
	if($s[$i][$v]>=6*$Vsma20[$i]){
	$Vspikegt6=$Vspikegt6+1;
	}
	if($s[$i][$v]>=8*$Vsma20[$i]){
	$Vspikegt8=$Vspikegt8+1;
	}

	// Number of green and red candles
	if(max($s[$i][$o],$s[$i][$c])<min($s[$i+1][$o],$s[$i+1][$c])){
	  $gapdown=$gapdown+1;
	}
	if(min($s[$i][$o],$s[$i][$c])>max($s[$i+1][$o],$s[$i+1][$c])){
	  $gapup=$gapup+1;
	}
	if($s[$i][$c]>$s[$i][$o]){
	  $greencandles=$greencandles+1;
	}
	if($s[$i][$o]>$s[$i][$c]){
	  $redcandles=$redcandles+1;
	}
}
echo "<p>";

echo '<h3> '.$symb.' : 2 year Current chart </h3>';
echo "<p align=\"center\">";
echo '<img src="http://chart.finance.yahoo.com/z?s='.$symb.'&t=2y&q=c&l=on&z=l&p=m10,m20,m50,v,vm" alt="HTML5 Icon">';
echo "</p>";
echo "<p><button onclick=\"return toggleme('.tab2y');\">Toggle Feature Table for 2 year chart</button></p>";

echo '<div class="tab2y" id="tab2y">';

echo "<p>";
echo "<table style=\"width:100%\" >";

echo "<tr>";
echo "<td># of Gap Ups =<font color=\"blue\"> ".((string) $gapup)." (".((string) 100*round($gapup/$T, 2))."%)"."</font></td>";  
echo "<td># of Gap Downs =<font color=\"blue\"> ".((string) $gapdown)." (".((string) 100*round($gapdown/$T, 2))."%)"."</font></td>";  
echo "<td># of Red/Down Candles = <font color=\"blue\">".((string) $redcandles)." (".((string) 100*round($redcandles/$T, 2))."%)"."</font></td>"; 
echo "<td># of Green/Up Candles = <font color=\"blue\">".((string) $greencandles)." (".((string) 100*round($greencandles/$T, 2))."%)"."</font></td>"; 
echo "</tr>";

echo "<tr>";
echo "<td># of Rel. Vols > 2  = <font color=\"blue\">".((string) $Vspikegt2)."</font></td>";  
echo "<td># of Rel. Vols > 4  = <font color=\"blue\">".((string) $Vspikegt4)."</font></td>";  
echo "<td># of Rel. Vols > 6  = <font color=\"blue\">".((string) $Vspikegt6)."</font></td>";  
echo "<td># of Rel. Vols > 8  = <font color=\"blue\">".((string) $Vspikegt8)."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td>Max Rel. Vol = <font color=\"blue\">".((string) $maxrv)."</font></td>"; 
echo "<td># of Candles > SMA10  = <font color=\"blue\">".((string) $Candlesgt10)." (".((string) 100*round($Candlesgt10/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles > SMA20  = <font color=\"blue\">".((string) $Candlesgt20)." (".((string) 100*round($Candlesgt20/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA = <font color=\"blue\">".((string) $SMA10gt20)." (".((string) 100*round($SMA10gt20/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "<tr>";
echo "<td># of Candles 10SMA > 20SMA > 50SMA = <font color=\"blue\">".((string) $SMA10gt20gt50)." (".((string) 100*round($SMA10gt20gt50/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA50gt100)." (".((string) 100*round($SMA50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 20SMA > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA20gt50gt100)." (".((string) 100*round($SMA20gt50gt100/$T, 2))."%)"."</font></td>";  
echo "<td># of Candles 10SMA > 20SMA  > 50SMA > 100SMA = <font color=\"blue\">".((string) $SMA10gt20gt50gt100)." (".((string) 100*round($SMA10gt20gt50gt100/$T, 2))."%)"."</font></td>";
echo "</tr>";

echo "</table>";
echo "<p>";

echo "</div>";
echo "</p>";







// all the javascript functions


?>



</body>
</html>
