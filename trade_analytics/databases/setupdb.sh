#!/bin/zsh
source ~/.zshrc



#sudo su - postgres
#psql
# dumps are in /var/lib/postgresql/

#edit 
# /etc/postgresql/9.1/main/pg_hba.conf
# to have 
# local   all             postgres                                md5
# host all nagavenkat 0.0.0.0/0 md5
# host all nagavenkat ::0/0 md5
# then restart:
# sudo service postgresql restart

# edit:
# /etc/postgresql/9.5/main/postgresql.conf
# to have 
# listen_addresses='*'
# sudo service postgresql restart

# Place the username and pass of DB is source bashrc or zshrc
export DBUSER="..."
export DBPASS="..."

sudo -i -u postgres psql -c "CREATE DATABASE trade_analytics;"
sudo -i -u postgres psql -c "CREATE DATABASE stockpricedata;"
sudo -i -u postgres psql -c "CREATE DATABASE featuredata;"
sudo -i -u postgres psql -c "CREATE DATABASE querydata;"

sudo -i -u postgres psql -c "CREATE USER $DBUSER WITH PASSWORD '$DBPASS';"

sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET client_encoding TO 'utf8';"
sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET default_transaction_isolation TO 'read committed';"
sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET timezone TO 'UTC';"

echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE trade_analytics TO $DBUSER;"
echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stockpricedata TO $DBUSER;"
echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE featuredata TO $DBUSER;"
echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE querydata TO $DBUSER;"


#\q
#exit






