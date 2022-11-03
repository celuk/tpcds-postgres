import subprocess

queries_path = '/home/guest/denegenyeni/tmpq0/cqueries'

for count in range(1, numofqueries+1):
    try:
        subprocess.getoutput("cat " + atxts_path + txt_pfx + count.__str__() + txt_sfx + " | plan-exporter --target=depesz --auto-confirm")
        "for i in `seq 1 10`; do   dexter -d tpcds1gb -h /tmp -p 5432 query_0.sql --input-format sql --create; done"
    
    except Exception as e:
        print()
        print(e)
        print()

