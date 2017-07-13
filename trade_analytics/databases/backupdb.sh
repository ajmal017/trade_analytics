currdir=`pwd`;
echo $currdir;

pg_dump trade_analytics > $currdir/backup/trade_analytics.backup
pg_dump featuredata > $currdir/backup/featuredata.backup
pg_dump querydata > $currdir/backup/querydata.backup
pg_dump stockpricedata > $currdir/backup/stockpricedata.backup

