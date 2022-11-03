import os
if not os.path.exists(os.getcwd() + "/queries"):
    os.mkdir(os.getcwd() + "/queries")

splitted_text = ""
query_count = 0

with open('query_0.sql', 'r') as q0:
    text_split = q0.read().split("\n\n\n")

text_split = text_split[:-1]

for each_text in text_split:
    query_count += 1
    each_file = open(os.getcwd() + "/queries/query" + query_count.__str__() + ".sql", "w")
    each_file.write(each_text.lstrip() + "\n\n")
            
    each_file.close()

