currdir=`pwd`;
echo $currdir;
pg_dump -U nagavenkat -w -h 127.0.0.1 trade_analytics > trade_analytics_09-07-17.backup
pg_dump trade_analytics > $currdir/backup/trade_analytics.backup
pg_dump featuredata > $currdir/backup/featuredata.backup
pg_dump querydata > $currdir/backup/querydata.backup
pg_dump stockpricedata > $currdir/backup/stockpricedata.backup
