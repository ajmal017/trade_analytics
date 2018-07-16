#!/bin/bash
# copy all dumps to /var/lib/postgresql/
# run setupdb to create the databases
# then do : sudo -i -u postgres
# then do : psql stockpricedata < stockpricedata.backup

currdir=`pwd`;
echo "Delete existing databases and restore ** PLEASE BACKUP **, [yes/(no)]  "
read goahead
echo $goahead;

if [ $goahead = "yes" ]; then
   
	echo "going ahead with delete and backup"

	db_name=trade_analytics;
	db_backup=$db_name.backup;
	sudo -i -u postgres psql -c "DROP DATABASE  IF EXISTS $db_name;"
	sudo -i -u postgres psql -c "CREATE DATABASE $db_name;"
	# sudo -i -u postgres psql -c "CREATE DATABASE $db_name -T template0 ;"
	sudo -i -u postgres psql -d $db_name -f $db_backup;
	sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $DBUSER;"
	
	# psql $db_name < $db_backup

	db_name=stockpricedata;
	db_backup=$db_name.backup;
	sudo -i -u postgres psql -c "DROP DATABASE  IF EXISTS $db_name;"
	sudo -i -u postgres psql -c "CREATE DATABASE $db_name;"
	sudo -i -u postgres psql -d $db_name -f $db_backup;
	sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $DBUSER;"

	db_name=featuredata;
	db_backup=$db_name.backup;
	sudo -i -u postgres psql -c "DROP DATABASE  IF EXISTS $db_name;"
	sudo -i -u postgres psql -c "CREATE DATABASE $db_name;"
	sudo -i -u postgres psql -d $db_name -f $db_backup;
	sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $DBUSER;"

	db_name=querydata;
	db_backup=$db_name.backup;
	sudo -i -u postgres psql -c "DROP DATABASE  IF EXISTS $db_name;"
	sudo -i -u postgres psql -c "CREATE DATABASE $db_name;"
	sudo -i -u postgres psql -d $db_name -f $db_backup;
	sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $DBUSER;"

fi