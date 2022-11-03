#cat /home/guest/bsc/tpcds_queries/analyzing_txts/q23a.txt | plan-exporter --target=depesz --auto-confirm

#echo $(wget https://explain.depesz.com/s/iPQ9#stats -q -O -)

import subprocess
import re
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt

functions = ['Parallel Hash Join', 'Sort', 'Index Scan', 'Parallel Seq Scan', 'Gather', 'Gather Merge', 'Bitmap Heap Scan', 'CTE Scan', 'Partial HashAggregate', 'Seq Scan', 'HashAggregate', 'Finalize GroupAggregate', 'MixedAggregate', 'Hash Join', 'Other']

atxts_path = '/home/guest/bsc/tpcds_queries/analyzing_txts/'

xlist = []
ylist = []

namelist = []

for count in range(1, 100):
    try:
        xlist.append(count.__str__())
        
        upload_to_depesz = subprocess.getoutput("cat " + atxts_path + "q" + count.__str__() + "a.txt | plan-exporter --target=depesz --auto-confirm")
    
        url = re.search('URL: (.*)', upload_to_depesz).group(1)
        url = url + '#stats'
    
        get_depesz_source = subprocess.getoutput("echo $(wget " + url + " -q -O -)")
    
        xml = re.sub(r"\b(Per node type stats.*?)\b\btable", r"\1table2", get_depesz_source)
        xml = re.sub(r"\b(Per node type stats.*?)\b\btable\>", r"\1table2>", xml)
    
        parse_xml = bs(xml, 'lxml')
        find_table = parse_xml.find('table2')
        rows = find_table.find_all('tr')
    
        max_prcnt = 0
        name_of_max = ''
    
        for i in rows[1:]:
            table_data = i.find_all('td')
            data = [j.text for j in table_data]
            each_prcnt = float(data[3].replace('%', '').strip())
            if each_prcnt > max_prcnt:
                max_prcnt = each_prcnt
                name_of_max = data[0]
    
        print('q' + count.__str__() + 'a.txt --> ' + name_of_max + ' ' + max_prcnt.__str__()  + ' --> ' + url)
        
        namelist.append(name_of_max)
        ylist.append(max_prcnt)

    except Exception as e:
        print()
        print('q' + count.__str__() + 'a.txt --> empty' + ' --> ' + url)
        
        namelist.append('empty')
        ylist.append(0)
        
        print()
        #print(e)
        #print()
  
print()      

namedict = {i:namelist.count(i) for i in namelist}

#print(sorted(namedict.items(), key=lambda x:x[1], reverse=True))

sorted_namedict = sorted(namedict.items(), key=lambda x:x[1], reverse=True)
#sorted_namedict = {i:sorted_namedict.count(i) for i in sorted_namedict}

import pprint

pprint.pprint(sorted_namedict)

## This does not work for integers
#for x in sorted_namedict:
#    print(x)
#    for y in sorted_namedict[x]:
#        print(y, ':', sorted_namedict[x][y])

print()

bars = plt.bar(xlist, ylist)
plt.title('Most Consumer Functions in Queries')
plt.xlabel('Queries')
plt.ylabel('Percentage')

plt.xticks(rotation=75)

count = 0

for each_bar in bars:
    plt.text(each_bar.get_x() + each_bar.get_width() / 2.0, 20, namelist[count] + '   %' + ylist[count].__str__(), color='red', ha='center', va='center', rotation='vertical')
    count = count + 1

#colors=['#A71930', '#DF4601', '#AB0003', '#003278', '#FF5910', '#0E3386', '#BA0021', '#E81828', '#473729', '#D31145', '#0C2340', '#005A9C', '#BD3039', '#EB6E1F', '#C41E3A', '#33006F', '#C6011F', '#004687', '#CE1141', '#134A8E', '#27251F', '#FDB827', '#0C2340', '#FD5A1E', '#00A3E0', '#ffc52f', '#003831', '#005C5C', '#E31937', '#8FBCE6']

#colors=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', '#C6011F', '#004687', '#CE1141', '#134A8E', '#27251F', '#FDB827', '#0C2340', '#AB0003', 'black']

colors=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', '#800000', '#FF8C00', '#00FF7F', '#4682B4', '#800080', '#8B4513', '#696969', '#808000', 'black']

i = 0
for patch in bars.patches:
    count = 0
    for each_func in functions:
        if namelist[i] == each_func:
            patch.set_facecolor(colors[count])
        
        count += 1
    i += 1

import matplotlib.patches as mpatches

patch_list = []
i = 0
for each_func in functions:
    patch_list.append(mpatches.Patch(label=each_func, color=colors[i]))
    i += 1
   
plt.legend(handles=patch_list, fontsize=8) #, bbox_to_anchor=(1.04, 0.5), loc='center left', borderaxespad=0, frameon=False)
    
#leg = plt.legend(functions, fontsize=8)

#leg.legendHandles[0].set_color(colors[0])
#leg.legendHandles[1].set_color(colors[1])

#for i, j in enumerate(leg.legendHandles):
#    j.set_color(colors[i])


#for patch,color in zip(bars.patches,colors):
#    patch.set_facecolor(color)

plt.show()

