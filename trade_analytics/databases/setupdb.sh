#!/bin/zsh
source ~/.zshrc

#sudo su - postgres
#psql
# dumps are in /var/lib/postgresql/

sudo -i -u postgres psql -c "CREATE DATABASE trade_analytics;"
sudo -i -u postgres psql -c "CREATE DATABASE stockpricedata;"
sudo -i -u postgres psql -c "CREATE DATABASE featuredata;"

sudo -i -u postgres psql -c "CREATE USER $DBUSER WITH PASSWORD '$DBPASS';"

sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET client_encoding TO 'utf8';"
sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET default_transaction_isolation TO 'read committed';"
sudo -i -u postgres psql -c "ALTER ROLE $DBUSER SET timezone TO 'EST';"

echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE trade_analytics TO $DBUSER;"
echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stockpricedata TO $DBUSER;"
echo|sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE featuredata TO $DBUSER;"



#\q
#exit







