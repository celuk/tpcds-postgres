# tpcds-postgres
TPC-DS Generation, Execution and Analyzer for Postgres

## Error Corrections for Generation and Execution of TPC-DS

**1-)** TPC-DS v3.2.0 benchmarks (DSGen-software-code-3.2.0rc1) are downloaded from [tpc site](https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp) and because it was giving error in the generation, I [added one line](https://github.com/celuk/tpcds-postgres/commit/13aa8d50cc6b6c22b882c3b1aae7dd638ed16d79) in [netezza.tpl](https://github.com/celuk/tpcds-postgres/blob/main/DSGen-software-code-3.2.0rc1/query_templates/netezza.tpl) file (according to this: https://dba.stackexchange.com/questions/36938/how-to-generate-tpc-ds-query-for-sql-server-from-templates/97926#97926):

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

**2-)** There was an error in the generator while reading `customer.dat` because of `UTF-8` formatting. So, for fixing this, I added encoding fixer python script [fix_encoding.py](https://github.com/celuk/tpcds-postgres/blob/main/fix_encoding.py) and it is automatically running while generating the database via [tpcds_generator.sh](https://github.com/celuk/tpcds-postgres/blob/main/tpcds_generator.sh) bash script and fixes `customer.dat` encoding.

&nbsp;

**3-)** Other errors was because syntax of 19 (out of 99) queries when running queries in the generated postgres database. This is because of query templates written in [`ANSI SQL`](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v3.2.0.pdf) format and is not compatible totaly with [`PostgreSQL`](https://www.postgresql.org)format. Syntax errors were in `5, 12, 16, 20, 21, 30, 32, 36, 37, 40, 70, 77, 80, 82, 86, 92, 94, 95, 98` queries. Errors and fixes can be seen below:

&nbsp;

**Syntax Error in query30.sql**

Column name error:

```
c_last_review_date_sk
```

_**Fix of query30.sql Syntax Error**_

_`c_last_review_date_sk` should be changed with `c_last_review_date`._

&nbsp;

**Syntax Errors in 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 queries**

`days` syntax is not valid for `PostgreSQL`.

_**Fix of 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 queries Syntax Errors**_

_Either all `days` keywords should be removed or changed like this `'30 days'::interval`._

&nbsp;

**Syntax Errors in 36, 70, 86 queries**

Column name alias error.

A quote from https://github.com/RunningJon/TPC-DS that explains the problem:

```
Query templates were modified to exclude columns not found in the query.  In these cases, the common 
table expression used aliased columns but the dynamic filters included both the alias name as well as the
original name.  Referencing the original column name instead of the alias causes the query parser to not
find the column. 
```

_**Fix of 36, 70, 86 queries Syntax Errors**_

_Using [subquery](https://stackoverflow.com/questions/69805738/why-do-i-get-an-error-querying-from-column-alias/69805832#69805832) fixes the problem._

&nbsp;

I could use automatic converters like [jOOQ](https://www.jooq.org/translate) but this does not resolve the column name errors.

I could do modifications in `.tpl` files but I didn't want to change original source and I am doing modifications after generation of sql queries while splitting via [split_analyzing_sqls.py](https://github.com/celuk/tpcds-postgres/blob/main/split_analyzing_sqls.py) or [split_sqls.py](https://github.com/celuk/tpcds-postgres/blob/main/split_sqls.py).

## Generation of TPC-DS Database

Generation phase is imitated from https://github.com/AXLEproject/pg-tpch and https://ankane.org/tpc-ds, and then the process is automated.

## Generation of Seperate TPC-DS Queries
After generation of the database, all 99 queries will be generated in just one file which is `query_0.sql`. For seperating the queries we have two python scripts:
* split_sqls.py --> Splits `query_0.sql` to `query1.sql`, `query2.sql`, ..., `query99.sql`
* split_analyzing_sqls.py --> Splits `query_0.sql` to `query1.sql`, `query2.sql`, ..., `query99.sql` with at the beginning `explain analyze` keyword.




