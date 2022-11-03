#!/bin/sh

PGBINDIR=/home/guest/bsc/postgres-compiled/bin
DBNAME=tpcds1gb
QLOC=/home/guest/bsc/tpcds_queries/acqueries
TXTLOC=/home/guest/bsc/tpcds_queries/actxts

mkdir -p $TXTLOC

count=0

for qfile in $QLOC/*;
do
count=$(($count+1))

echo $QLOC/query${count}.sql

$PGBINDIR/psql $DBNAME < $QLOC/query${count}.sql > $TXTLOC/q${count}a.txt

done

