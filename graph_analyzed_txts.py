## This script traverse on the analyzed texts of queries and makes stacked bar chart from them.

## Below commands are executing on the texts and then it extracts info from them

# cat /home/guest/bsc/tpcds_queries/analyzing_txts/q23.txt | plan-exporter --target=depesz --auto-confirm
# echo $(wget https://explain.depesz.com/s/iPQ9#stats -q -O -)

######### REQUIRED INSTALLATIONS #########

## Before running you need to install plan-exporter tool like this:

# wget https://github.com/agneum/plan-exporter/releases/download/v0.0.5/plan-exporter-0.0.5-linux-amd64.tar.gz
# tar -zxvf plan-exporter-0.0.5-linux-amd64.tar.gz
# sudo mv plan-exporter-*/plan-exporter /usr/local/bin/
# rm -rf ./plan-exporter-*

## If cannot find the python modules:

# pip3 install matplotlib
# pip3 install BeautifulSoup4
# pip3 install numpy
# pip3 install pprint

##### END OF REQUIRED INSTALLATIONS #####

######### REQUIRED CHANGES #########

## Analyzed txts path
## Change this path
atxts_path = '/home/guest/bsc/tpcds_queries/analyzing_txts/' #'/home/guest/bsc/tpcds_10gb/atxts10gb/' #'/home/guest/bsc/tpcds_queries/analyzing_txts/'

## Also change these, if you need
txt_pfx = 'q' ## e.g. q23.txt, prefix of text before the query number
txt_sfx = 'a.txt' ## suffix after the query number

## If there is less query, then change this too
numofqueries = 99

plot_title_name = 'The Most Consumer Functions in TPC-DS Queries - 1GB'
pdf_name = 'tpcds1gb'

##### END OF REQUIRED CHANGES #####

import subprocess
import re
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import argparse
import pprint

## You can use this command line argument e.g.:
# python3 allinonce.py --hlfunc="Sort"
## to highlight desired function in the bar chart
parser = argparse.ArgumentParser(description='Create Configuration')
parser.add_argument('-hf', '--hlfunc', type=str, help='Specify function to highlight it', default='')
args = parser.parse_args()

## If you want to add a function adding to functions list is sufficient, it will generate extra colors automatically
## If you want to remove a function removing from function list is sufficient, it will remove extra colors
## However, if you want to match colors and functions one-to-one, you need to add colors to colors list as you added functions to functions list
## Always, just leave 'Other' as last element
functions = ['Parallel Hash Join', 'Sort', 'Index Scan', 'Index Only Scan', 'Parallel Seq Scan', 'Gather', 'Gather Merge', 'Bitmap Heap Scan', 'CTE Scan', 'Partial HashAggregate', 'Seq Scan', 'HashAggregate', 'Finalize GroupAggregate', 'MixedAggregate', 'Hash Join', 'Other']

colors=['blue', 'green', 'red', '#F5DEB3', 'cyan', 'magenta', 'yellow', '#800000', '#FF8C00', '#00FF7F', '#4682B4', '#800080', '#8B4513', '#696969', '#808000', 'black']

## These colors for highlighting desired function
h1color = 'blue' ## desired function color
h2color = '#808080' ## other functions color

## This is for if you add extra functions to functions list and don't specify the color for them, it generates random colors for them.
import random
get_rand_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))

## Either functions removed or added to functions list it arranges the colors list accordingly, and for example, after adding extra functions, it adds extra colors randomly
if len(functions) > len(colors):
    extra_colors = get_rand_colors(len(functions) - len(colors))
    for each_color in extra_colors:
        colors.insert(colors.index(colors[-2]), each_color)
elif len(functions) < len(colors):
    for i in range(0, len(colors) - len(functions)):
        colors.pop(colors.index(colors[-2]))

## 1 to 99 (numofqueries) numbers for x axis of bar plot
xlist = []

## Number of functions list each with numofqueries items filled with 0 (default 16x99 matrix)
## This list is using to save percentages of each desired function for each query
ylist = [[0 for x in range(numofqueries)] for y in range(len(functions))]

## A list to save percentages of the most consumer functions for each query
maxylist = []
## A list to save names of the most consumer functions for each query
maxnamelist = []

## All the uploading analyzed texts to explain.depesz.com, getting the source of each stats page and parsing operations running here
## In summary, depesz' stats table is extracting from here
for count in range(1, numofqueries+1):
    try:
        ## Saves query numbers for x axis of the plot
        xlist.append(count.__str__())
        
        ## Uploads each analyzed text to explain.depesz.com
        upload_to_depesz = subprocess.getoutput("cat " + atxts_path + txt_pfx + count.__str__() + txt_sfx + " | plan-exporter --target=depesz --auto-confirm")
    
        ## Saves given url after uploading
        url = re.search('URL: (.*)', upload_to_depesz).group(1)
        url = url + '#stats'
    
        ## Getting the xml source of the page from given url
        get_depesz_source = subprocess.getoutput("echo $(wget " + url + " -q -O -)")
    
        ## Regexing the xml to find desired table in the page
        xml = re.sub(r"\b(Per node type stats.*?)\b\btable", r"\1table2", get_depesz_source)
        xml = re.sub(r"\b(Per node type stats.*?)\b\btable\>", r"\1table2>", xml)
    
        ## Parsing xml and getting the rows of the table
        parse_xml = bs(xml, 'lxml')
        find_table = parse_xml.find('table2')
        table_rows = find_table.find_all('tr')
    
        max_prcnt = 0
        name_of_max = ''
    
        ## Traversing on the table's rows and columns and save them to the lists
        for i in table_rows[1:]:
            table_data = i.find_all('td')
            data = [j.text for j in table_data]
            each_prcnt = float(data[3].replace('%', '').strip())
            
            if data[0] in functions:
                ylist[functions.index(data[0])][count-1] = float(data[3].replace('%', '').strip())
            else: ## For other functions
                ylist[functions.index(functions[-1])][count-1] += float(data[3].replace('%', '').strip())

            if each_prcnt > max_prcnt:
                max_prcnt = each_prcnt
                name_of_max = data[0]
    
        ## Prints depesz url, the most consumer functions and the percentages for each query
        ## Keep in mind that max percentages are not normalized while printing, they are normalizing in the bar chart
        print(txt_pfx + count.__str__() + txt_sfx + ' --> ' + name_of_max + ' ' + max_prcnt.__str__()  + ' --> ' + url)
        
        maxnamelist.append(name_of_max)
        maxylist.append(max_prcnt)

    ## If there is an exception above, probably the analyzed text is empty or not found because of the syntax errors in the queries
    except Exception as e:
        print()
        print(txt_pfx + count.__str__() + txt_sfx + ' --> empty')
        
        maxnamelist.append('empty')
        maxylist.append(0)
        print()

print()      

## This prints number of the most consumer functions out of 99 (numofqueries) query in descending order
maxnamedict = {i:maxnamelist.count(i) for i in maxnamelist}
sorted_maxnamedict = sorted(maxnamedict.items(), key=lambda x:x[1], reverse=True)
pprint.pprint(sorted_maxnamedict)

print()

## This is normalizing data to 100 percent for bar plot, otherwise overlapping occurs and percentages are exceeding 100 percent
## Remove this if you dont want to normalize
for i in range(0, numofqueries):
    eachq_prcnt_sum = 0
    for j in range(0, len(functions)):
        eachq_prcnt_sum += ylist[j][i]
    if eachq_prcnt_sum > 100:
        rate = eachq_prcnt_sum / 100.0
        for j in range(0, len(functions)):
            ylist[j][i] = ylist[j][i] / rate

## If e.g. --hlfunc="Sort" option is given from the command line, then this makes the colors two seperate color as "Sort" and the others
highlight = False
if args.hlfunc in functions:
    highlight = True
    skip_index = functions.index(args.hlfunc)
    for i in range(0, len(functions)):
        if i is not skip_index:
            colors[i] = h2color #'#808080' #'black'
        else:
            colors[i] = h1color #'blue'

plt.rcParams["font.size"] = "18"

## Plotting stacked bar chart according to list of functions
bars1 = plt.bar(xlist, ylist[0], color=colors[0])
cumulative_list = np.array(ylist[0])
count = 0
for eachylist in ylist[1:]:
    count += 1
    plt.bar(xlist, eachylist, color=colors[count], bottom=cumulative_list)
    cumulative_list = cumulative_list + np.array(eachylist)

## At the top of the chart, this is writing max percentage for each bar, for the most consumer function in each query

count = 0
for each_bar in bars1:
    plt.text(each_bar.get_x() + each_bar.get_width() / 2.0, 110, '% ' + maxylist[count].__str__(), color='black', ha='center', va='center', rotation='vertical', fontsize=18)
    count = count + 1

## Plot title and preferences
if highlight:
    plt.title(plot_title_name + ' - ' + args.hlfunc.strip(), fontsize=30)
else:
    plt.title(plot_title_name, fontsize=30)
plt.xlabel('Queries', fontsize=30)
plt.ylabel('Percentage', fontsize=30)
plt.xticks(rotation=75)
plt.grid()

## Add legends automatically to the plot
patch_list = []
i = 0
if highlight:
    patch_list.append(mpatches.Patch(label=args.hlfunc, color=h1color))
    patch_list.append(mpatches.Patch(label='Other', color=h2color))
else:
    for each_func in functions:
        patch_list.append(mpatches.Patch(label=each_func.replace(' ', '\n'), color=colors[i]))
        i += 1
plt.legend(handles=patch_list, fontsize=26, loc=(0.96, 0))

#plt.rc('font', size=20)          # controls default text sizes
#plt.rc('axes', titlesize=20)     # fontsize of the axes title
#plt.rc('axes', labelsize=20)    # fontsize of the x and y labels
#plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
#plt.rc('ytick', labelsize=20)    # fontsize of the tick labels
#plt.rc('legend', fontsize=20)    # legend fontsize
#plt.rc('figure', titlesize=20)  # fontsize of the figure title

#plt.rcParams.update({'font.size': 22})

## Maximize the plot window
figure = plt.gcf()
figure.set_size_inches(32,18)

## Save the plot to pdf
if highlight:
    plt.savefig(pdf_name + '_' + ''.join(args.hlfunc.split()) + '.pdf', dpi=300)
else:
    plt.savefig(pdf_name + '.pdf', dpi=300)
    
## Show the plot
plt.show()

