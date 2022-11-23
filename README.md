# tpcds-postgres
TPC-DS Generation, Execution and Analyzer for Postgres

## TL;DR

Making TPC-DS Tools:
```bash
git clone https://github.com/celuk/tpcds-postgres
cd tpcds-postgres/DSGen-software-code-3.2.0rc1/tools
make
```

Database Generation:
```bash
cd ../..
nano pgtpcds_defaults ## change required variables
sudo ./tpcds_generator.sh
```

Splitting and Fixing Sqls:

```bash
cd your_query0_generated_directory ## either go to this directory or place query_0.sql and the scripts in the same directory.
python3 split_sqls.py
python3 split_analyzing_sqls.py
```

Getting Analyzed Texts:

```bash
nano get_analyzed_txts.sh ## change required variables
sudo ./get_analyzed_txts.sh
```

Installing python dependencies for `graph_analyzed_txts.py`:

```bash
pip3 install matplotlib
pip3 install BeautifulSoup4
pip3 install lxml
pip3 install numpy
pip3 install pprint
```

Plotting Stacked Bar Chart Graphs from Analyzed Texts:

```bash
nano graph_analyzed_txts.py ## change required variables
python3 graph_analyzed_txts.py --depesz ## after that you will get .png and .pdfs of stacked bar chart
```

## Error Corrections for Generation and Execution of TPC-DS

**1-)** TPC-DS v3.2.0 benchmarks (DSGen-software-code-3.2.0rc1) are downloaded from [TPC site](https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp) and because it was giving error in the generation, I [added one line](https://github.com/celuk/tpcds-postgres/commit/13aa8d50cc6b6c22b882c3b1aae7dd638ed16d79) in [netezza.tpl](DSGen-software-code-3.2.0rc1/query_templates/netezza.tpl) file (according to this: https://dba.stackexchange.com/questions/36938/how-to-generate-tpc-ds-query-for-sql-server-from-templates/97926#97926):

```diff
--- a/DSGen-software-code-3.2.0rc1/query_templates/netezza.tpl
+++ b/DSGen-software-code-3.2.0rc1/query_templates/netezza.tpl
@@ -32,6 +32,9 @@
 -- 
 -- Contributors:
 -- 
+
+define _END = "";
+
 define __LIMITA = "";
 define __LIMITB = "";
 define __LIMITC = "limit %d";
```

&nbsp;

**2-)** There was an error in the generator while reading `customer.dat` because of `UTF-8` formatting. So, for fixing this, I added encoding fixer python script [fix_encoding.py](fix_encoding.py) and it is automatically running while generating the database via [tpcds_generator.sh](tpcds_generator.sh) bash script and fixes `customer.dat` encoding.

&nbsp;

**3-)** Other errors was because syntax of 19 (out of 99) queries when running queries in the generated postgres database. This is because of query templates written in [`ANSI SQL`](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v3.2.0.pdf#page=15) format and is not compatible totaly with [`PostgreSQL`](https://www.postgresql.org)format. Syntax errors were in `5, 12, 16, 20, 21, 30, 32, 36, 37, 40, 70, 77, 80, 82, 86, 92, 94, 95, 98` queries.

&nbsp;

I could use automatic converters like [jOOQ](https://www.jooq.org/translate) but this does not resolve the column name errors.

I could do modifications in `.tpl` files but I didn't want to change original source. I am doing modifications after generation of sql queries while splitting via [split_analyzing_sqls.py](split_analyzing_sqls.py) or [split_sqls.py](split_sqls.py) scripts.

_**Note:**_ Note that SQL queries should be fixed for every database generation because in `TPC-DS` while a database is generating, it is also generating the queries according to the `SCALE` factor (size of database in gigabytes).  

&nbsp;

Errors and fixes can be seen below:

&nbsp;

**Syntax Error in query30.sql**

Column name error:

```
c_last_review_date_sk
```

_**Fix of query30.sql Syntax Error**_

_`c_last_review_date_sk` should be changed with `c_last_review_date`._

In python scripts I did:

```python
each_text = each_text.replace('c_last_review_date_sk', 'c_last_review_date')
```

&nbsp;

**Syntax Errors in 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 queries**

`days` syntax is not valid for `PostgreSQL`.

_**Fix of 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 queries Syntax Errors**_

_Either all `days` keywords should be removed or changed like this `'30 days'::interval`._

In python scripts I did:

```python
each_text = each_text.replace('days', '')
```

&nbsp;

**Syntax Errors in 36, 70, 86 queries**

Column name alias error.

A quote from https://github.com/RunningJon/TPC-DS that explains the problem:

```
Query templates were modified to exclude columns not found in the query.  In these cases, the 
common table expression used aliased columns but the dynamic filters included both the alias 
name as well as the original name. Referencing the original column name instead of the alias 
causes the query parser to not find the column. 
```

_**Fix of 36, 70, 86 queries Syntax Errors**_

_Using [subquery](https://stackoverflow.com/questions/69805738/why-do-i-get-an-error-querying-from-column-alias/69805832#69805832) fixes the problem. So, `select * from (` should be added the head of the queries and `) as sub` should be added before `order by` section. And it makes the piece of code to subquery like this:_

```sql
select * from ( -- this is added to head of the query before select

-- ...

-- encapsulated code

-- ...

) as sub -- this is added before the last order by

order by

-- ...
```

In python scripts I did:

```python
each_text = each_text.replace('select', 'select * from (select ', 1)
each_text = ') as sub\n order by'.join(each_text.rsplit('order by', 1))
```

## Generation of TPC-DS Database

Generation phase is imitated from https://github.com/AXLEproject/pg-tpch and https://ankane.org/tpc-ds, and then the process is automated.

For generation, firstly clone this repository, go to directory `tpcds-postgres/DSGen-software-code-3.2.0rc1/tools` and type `make` in the terminal to compile generation tools of [TPC](https://www.tpc.org):

```bash
git clone https://github.com/celuk/tpcds-postgres
cd tpcds-postgres/DSGen-software-code-3.2.0rc1/tools
make
```

Secondly, change the required variables in `pgtpcds_defaults` file.

Thirdly, run [tpcds_generator.sh](tpcds_generator.sh) with `sudo`:

```bash
sudo ./tpcds_generator.sh
```

_**Note:**_ There are a lot of unnecessary `sudo`s in `tpcds_generator.sh` because some servers may need it but you can try to remove them to see if it works in your case. 

## Generation of Seperate TPC-DS Queries
After generation of the database, all 99 queries will be generated in just one file which is `query_0.sql`. For seperating the queries we have two python scripts:
```bash
* split_sqls.py --> Splits `query_0.sql` to `query1.sql`, `query2.sql`, ..., `query99.sql`
* split_analyzing_sqls.py --> Splits `query_0.sql` to `query1.sql`, `query2.sql`, ..., `query99.sql` 
with at the beginning `explain analyze` keyword that gives analyzed output after running.
```

Firstly place `query_0.sql` and the python scripts in the same place or run python scripts in directory of `query_0.sql`.

For getting normal SQLs run:

```bash
python3 split_sqls.py
```

For getting analyzing SQLs run:

```bash
python3 split_analyzing_sqls.py
```

## Running Queries
You need to start the database firstly as:

```bash
sudo -u <username> pg_ctl -D <database-name> start
```

An example to start database:

```bash
sudo -u guest /home/guest/postgres/postgres-compiled/bin/pg_ctl -D /home/guest/bsc/databases/pgdata1GB start
```

If you cannot start because of an old process, please look at this answer to solve the problem and try to start database again: https://stackoverflow.com/questions/52963079/i-cant-start-server-postgresql-11-pg-ctl-could-not-start-server/73868082#73868082

For running a query, you can use this command:

```bash
sudo -u <username> psql -d <database-name> -f <query-name>
```

or this command:

```bash
sudo -u <username> psql <database-name> < <query-name>
```

An example to run a query:

```bash
sudo -u guest /home/guest/postgres/postgres-compiled/bin/psql tpcds1gb < query1.sql
```

For running all queries you can use [get_analyzed_txts.sh](get_analyzed_txts.sh). Firstly edit the required variables in the file, then you can run as:

```bash
sudo ./get_analyzed_txts.sh
```

After that if you run:
* normal sqls --> you will get outputs of sql commands in a folder as seperate `.txt` files.
* analyzing sqls --> you will get analyzed outputs of sql commands in a folder as seperate `.txt` files. As `q1a.txt`, `q2a.txt`, ..., `q99a.txt`

An example output of analyzing sql is like this:

```bash
                                                  QUERY PLAN                    
                              
--------------------------------------------------------------------------------------------------------------
 HashAggregate  (cost=1.25..1.45 rows=20 width=12) (actual time=0.134..0.263 row
s=20 loops=1)
   Group Key: ib_income_band_sk
   Batches: 1  Memory Usage: 24kB
   ->  Seq Scan on income_band  (cost=0.00..1.20 rows=20 width=12) (actual time=
0.027..0.032 rows=20 loops=1)
 Planning Time: 1.741 ms
 Execution Time: 0.518 ms
(6 rows)
```

&nbsp;

After running the desired queries don't forget to stop the database:

```bash
sudo -u <username> pg_ctl -D <database-name> stop
```

## Getting Graphs from Analyzed Texts
To get stacked bar chart graphs from analyzed txts, you can use [graph_analyzed_txts.py](graph_analyzed_txts.py). It uploads analyzed txts to https://explain.depesz.com from given path, gets the source of uploaded url, parses it and extracts table from there, -if `--depesz` flag given before, they already stored in a folder, so, by not giving depesz option we can bypass all of these operations to not wait- creates customizable graphs according to given flags.

Firstly install python dependencies:

```bash
pip3 install matplotlib
pip3 install BeautifulSoup4
pip3 install lxml
pip3 install numpy
pip3 install pprint
```

Change required variables in the script, then run the script:

```bash
python3 graph_analyzed_txts.py --depesz
```
This will give an output graph like this:
![tpcds1gb.png](tpcds1gb.png)


There are several flags here to use while running [graph_analyzed_txts.py](graph_analyzed_txts.py):
|     flag    | short version of the flag | description                                                                                                                                                          | example usage           |
|:-----------:|:-------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| --depesz    |      -dz      | Uploads given analyzed texts to https://explain.depesz.com, if it is the first time for your analyzed texts you need to give this flag, otherwise you don't need it. | `-dz`                   |
| --hlfunc    |      -hf      | Takes one argument as string to highlight desired function in the graph.                                                                                             | `-hf "Sort"`            |
| --querylist |      -ql      | Takes desired query list as numbers with commas as string to plot special graphs.                                                                                    | `-ql "1, 32,3,76 , 55"` |
| --part      |       -p      | Like `querylist` option but it makes parted graphs ten by ten like first ten part, fourth ten part.                                                                  | `-p 5`                  |
| --bottomed  |      -bt      | If you are highlighting desired function and if it is floating in the graph, it makes the bars bottomed.                                                             | `-bt`                   |
### Example Use Cases for graph_analyzed_txts.py

This highlights `Index Scan` function in the graph:
```bash
python3 graph_analyzed_txts.py -hf "Index Scan"
```
![tpcds1gb_IndexScan.png](tpcds1gb_IndexScan.png)
&nbsp;

This makes it bottomed:
```bash
python3 graph_analyzed_txts.py -dz -hf "Index Scan" -bt
```
![tpcds1gb_IndexScan_bottomed.png](tpcds1gb_IndexScan_bottomed.png)
&nbsp;

This is giving a special graph according to given query list and highlights `Index Scan` function at the same time:
```bash
python3 graph_analyzed_txts.py -hf "Index Scan" --querylist "1, 32,3,76 , 55"
```
![tpcds1gb_IndexScan_querylist.png](tpcds1gb_IndexScan_querylist.png)
&nbsp;

This is giving the seventh part of the main graph:
```bash
python3 graph_analyzed_txts.py -p 7
```
![tpcds1gb_part7.png](tpcds1gb_part7.png)
&nbsp;

## Extra: Creating Indexes
Firstly install [hypopg](https://github.com/HypoPG/hypopg):
```bash
export PATH=/home/guest/bsc/postgres-compiled/bin:$PATH
git clone https://github.com/HypoPG/hypopg
USE_PGXS=1 make install
```

Then install [dexter](https://github.com/ankane/dexter):

```bash
wget -qO- https://dl.packager.io/srv/pghero/dexter/key | sudo apt-key add -
sudo wget -O /etc/apt/sources.list.d/dexter.list \
  https://dl.packager.io/srv/pghero/dexter/master/installer/ubuntu/$(. /etc/os-release && echo $VERSION_ID).repo
sudo apt-get update
sudo apt-get -y install dexter
```

Change required variables in [create_indexes.py](create_indexes.py) and then run the script to create indexes in desired database:
```bash
python3 create_indexes.py
```
