#!/bin/bash

## TCP-DS Database Generation Script for Postgres

## Before running this script you should do;
## sudo apt-get install gcc make flex bison byacc git
## then go to DSGen-software-code-3.2.0rc1/tools directory
## and then make the tools: make OS=LINUX

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)
. "$BASEDIR/pgtpcds_defaults"

t=$(timer)

sudo mkdir -p "$Q0DIR"

if ! [ -d "$PGDATADIR" ]; then
  sudo mkdir -p "$PGDATADIR"
  sudo chmod 777 "$PGDATADIR"
  sudo chown $PGUSER "$PGDATADIR"
  sudo -u $PGUSER $PGBINDIR/initdb -D "$PGDATADIR" --encoding=UTF-8 --locale=C
  CREATE_NEW_DB=true
else
  CREATE_NEW_DB=false
fi

sudo -u $PGUSER $PGBINDIR/postgres -D "$PGDATADIR" -p $PGPORT &
PGPID=$!
while ! sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $PGDATADIR | grep "server is running" -q; do
  echo "Waiting for the Postgres server to start"
  sleep 2
done

if $CREATE_NEW_DB; then
  sudo -u $PGUSER $PGBINDIR/createdb -h /tmp -p $PGPORT $PGUSER --encoding=UTF-8 --locale=C
fi

WAL_LEVEL_MINIMAL=`sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -c 'show wal_level' -t | grep minimal | wc -l`
DEBUG_ASSERTIONS=`sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -c 'show debug_assertions' -t | grep on | wc -l`

shopt -s nullglob

sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -c "select name, current_setting(name) from pg_settings where name
in('debug_assertions', 'wal_level', 'checkpoint_segments', 'shared_buffers', 'wal_buffers',
'fsync', 'maintenance_work_mem', 'checkpoint_completion_target',
'max_connections');"

if [ $WAL_LEVEL_MINIMAL != 1 ] ;
then
    echo "Warning: Postgres wal_level is not set to minimal; 'Elide WAL traffic' optimization cannot be used">&2
fi

if [ $DEBUG_ASSERTIONS = 1 ] ;
then
    echo "Error: debug_assertions are enabled">&2
    exit -1
fi

sudo mkdir -p "$TPCDSTMP" || die "Failed to create temporary directory: '$TPCDSTMP'"

for p in $(jobs -p);
do
  if [ $p != $PGPID ];
  then
      wait $p
  fi
done

if $POPULATE_DB
then
  echo "DROP DATABASE IF EXISTS $DB_NAME" | sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT

  sudo -u $PGUSER $PGBINDIR/createdb -h /tmp -p $PGPORT $DB_NAME --encoding=UTF-8 --locale=C
  if [ $? != 0 ]; then
    echo "Error: Can't proceed without database"
    exit -1
  fi

  TIME=`date`
  sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "comment on database $DB_NAME is 'TPC-DS data, created at $TIME'"
  cd $TPCDSDIR/tools
  sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -f ./tpcds.sql
  sudo ./dsdgen -FORCE -VERBOSE -SCALE $SCALE
  for i in `ls *.dat`; do
  table=${i/.dat/}
  echo "Loading $table..."
  sudo sed 's/|$//' $i > $Q0DIR/$i
  
  ## It may not be needed
  sudo chmod 777 $Q0DIR/$i
  
  if [[ "$i" == "customer.dat" ]]; then
  sudo python3 $BASEDIR/fix_encoding.py --filename="$Q0DIR/$i"
  fi
  
  sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -q -c "TRUNCATE $table"
  sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "\\copy $table FROM '${Q0DIR}/$i' CSV DELIMITER '|'"
  done

  # Configuration parameters for efficient data loading
  echo "$data_loading_configuration" | sudo -u $PGUSER tee -a $PGDATADIR/postgresql.conf

  if $LOGGING
  then
      echo "$logging_configuration" | sudo -u $PGUSER tee -a $PGDATADIR/postgresql.conf
  fi

  sudo -u $PGUSER $PGBINDIR/pg_ctl reload -D $PGDATADIR

  cd "$TPCDSTMP"
  for f in *.tbl; do
    bf="$(basename $f .tbl)"
    echo "truncate $bf; COPY $bf FROM '$(pwd)/$f' WITH DELIMITER AS '|'" | sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME &
  done

  for p in $(jobs -p); do
    if [ $p == $PGPID ]; then continue; fi
    wait $p;
  done
fi

cd "$BASEDIR"
sudo rm -rf "$TPCDSTMP"

echo "$query_configuration" | sudo -u $PGUSER tee -a $PGDATADIR/postgresql.conf
sudo -u $PGUSER $PGBINDIR/pg_ctl reload -D $PGDATADIR

echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

echo "Running vacuum freeze analyze..."
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "vacuum freeze"
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "analyze"

echo "Checkpointing..."
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "checkpoint"

pushd $TPCDSDIR/tools
sudo ./dsqgen -DIRECTORY ../query_templates -INPUT ../query_templates/templates.lst -VERBOSE Y -QUALIFY Y -DIALECT netezza -SCALE $SCALE -OUTPUT_DIR $Q0DIR
popd

printf 'Elapsed time: %s\n' $(timer $t)

