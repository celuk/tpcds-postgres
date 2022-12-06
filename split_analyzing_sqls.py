## Author: Seyyid Hikmet Celik

import os

filetosave = "/acqueries"

if not os.path.exists(os.getcwd() + filetosave):
    os.mkdir(os.getcwd() + filetosave)

splitted_text = ""
query_count = 0

qdays_list = [5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98]
loch_list = [36, 70, 86]

with open('query_0.sql', 'r') as q0:
    text_split = q0.read().split("\n\n\n")

text_split = text_split[:-1]

for each_text in text_split:
    query_count += 1
    if query_count == 30:
        each_text = each_text.replace('c_last_review_date_sk', 'c_last_review_date')
    elif query_count in qdays_list:
        each_text = each_text.replace('days', '')
    elif query_count in loch_list:
        each_text = each_text.replace('select', 'select * from (select ', 1)
        each_text = ') as sub\n order by'.join(each_text.rsplit('order by', 1))
    
    each_file = open(os.getcwd() + filetosave + "/query" + query_count.__str__() + ".sql", "w")
    each_file.write("explain analyze " + each_text.lstrip() + "\n\n")
            
    each_file.close()

