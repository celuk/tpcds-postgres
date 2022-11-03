#!/bin/sh

PGBINDIR=/home/guest/bsc/postgres-compiled/bin
DBNAME=tpcds1gb
QLOC=/home/guest/denegenyeni/tmpq0/acqueries
TXTLOC=/home/guest/denegenyeni/tmpq0/atxtsindexed

mkdir -p $TXTLOC

count=0

for qfile in $QLOC/*;
do
count=$(($count+1))

echo $QLOC/query${count}.sql

sudo -u guest $PGBINDIR/psql $DBNAME < $QLOC/query${count}.sql > $TXTLOC/q${count}a.txt

done

