#!/bin/bash

# TCP-DS Database Generation Script for Postgres

## Before running this script you should do;
## sudo apt-get install gcc make flex bison byacc git
## then go to DSGen-software-code-3.2.0rc1/tools directory
## and then make the tools: make OS=LINUX

## configuration variables
SCALE=1 #GB
PGDATADIR=/home/guest/bsc/databases/pgdata1GB
PGUSER="guest"
PGBINDIR=/home/guest/bsc/postgres-compiled/bin

TPCDSDIR=/home/guest/bsc/DSGen-software-code-3.2.0rc1
TOOLSDIR=$TPCDSDIR/tools
Q0DIR=/home/guest/bsc #/DSGen-software-code-3.2.0rc1/tools

NEWDB=tpcds1gb
## end of configuration variables

pushd $TOOLSDIR

#sudo /etc/init.d/postgresql stop

# starting the old server
sudo -u $PGUSER $PGBINDIR/pg_ctl -D $PGDATADIR start

# creating new database
$PGBINDIR/createdb -U $PGUSER $NEWDB
$PGBINDIR/psql -U $PGUSER $NEWDB -f tpcds.sql
./dsdgen -FORCE -VERBOSE -DISTRIBUTIONS tpcds.idx

for i in `ls *.dat`; do
  table=${i/.dat/}
  echo "Loading $table..."
  sed 's/|$//' $i > $TOOLSDIR/$i
  $PGBINDIR/psql -U $PGUSER $NEWDB -q -c "TRUNCATE $table"
  $PGBINDIR/psql -U $PGUSER $NEWDB -c "\\copy $table FROM '${TOOLSDIR}/$i' CSV DELIMITER '|'"
done
./dsqgen -DIRECTORY $TPCDSDIR/query_templates -INPUT $TPCDSDIR/query_templates/templates.lst -VERBOSE Y -QUALIFY Y -DIALECT netezza -SCALE $SCALE -OUTPUT_DIR $Q0DIR

# stopping the old server
sudo -u $PGUSER $PGBINDIR/pg_ctl -D $PGDATADIR stop

popd

