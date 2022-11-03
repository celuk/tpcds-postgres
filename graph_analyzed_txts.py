## Saved tables path
tabletxts_path = '/home/guest/tables1gb/'

tabletxt_pfx = 'qatable'
tabletxt_sfx = '.txt'

## If there is less query, then change this too
maxnumofqueries = 99
numofqueries = maxnumofqueries

plot_title_name = 'The Most Consumer Functions in TPC-DS Queries - 10GB'
pdf_name = 'tpcds10gb2'

##### END OF REQUIRED CHANGES #####

import subprocess
import re
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import argparse
import pprint

query_list = []

## You can use this command line argument e.g.:
# python3 allinonce.py --hlfunc="Sort"
## to highlight desired function in the bar chart
parser = argparse.ArgumentParser(description='Create Configuration')
parser.add_argument('-hf', '--hlfunc', type=str, help='Specify function to highlight it', default='')
parser.add_argument('-ql', '--querylist', type=str, help='Specify query list for special graphs', default='')
parser.add_argument('-p', '--part', type=str, help='Specify a part (1-10) to make a smaller part of queries graph', default='')
parser.add_argument('-bt', '--bottomed', action='store_true', help='Make bottomed highlighted function graphs', default=False)
args = parser.parse_args()

if ''.join(args.querylist.split()) != '':    
    query_list = [each_number.strip() for each_number in args.querylist.split(',')]
    query_list[:] = [int(x) for x in query_list if x.strip()]
    
which_part = 1
if args.part != '':  
    if int(args.part) <= 10 and int(args.part) >= 1:
        which_part = int(args.part)

    if args.querylist == '':
        query_list = list(range(10*(which_part-1)+1, 10*(which_part-1)+ (11 if which_part != 10 else 10)))

if len(query_list) > 0 and len(query_list) < maxnumofqueries+1:
    numofqueries = len(query_list)

## If you want to add a function adding to functions list is sufficient, it will generate extra colors automatically
## If you want to remove a function removing from function list is sufficient, it will remove extra colors
## However, if you want to match colors and functions one-to-one, you need to add colors to colors list as you added functions to functions list
## Always, just leave 'Other' as last element
functions = ['Other'] #['Parallel Hash Join', 'Sort', 'Index Scan', 'Index Only Scan', 'Parallel Seq Scan', 'Gather', 'Gather Merge', 'Bitmap Heap Scan', 'CTE Scan', 'Partial HashAggregate', 'Seq Scan', 'HashAggregate', 'Finalize GroupAggregate', 'MixedAggregate', 'Hash Join', 'Other']

colors=['blue', 'green', 'red', '#F5DEB3', 'cyan', 'magenta', 'yellow', '#800000', '#FF8C00', '#00FF7F', '#4682B4', '#800080', '#8B4513', '#696969', '#808000', 'black']

## These colors for highlighting desired function
h1color = 'blue' ## desired function color
h2color = '#808080' ## other functions color

## 1 to 99 (numofqueries) numbers for x axis of bar plot
xlist = []

## Number of functions list each with numofqueries items filled with 0 (default 16x99 matrix)
## This list is using to save percentages of each desired function for each query
ylist = [[0 for x in range(numofqueries)] for y in range(len(functions))]

## A list to save percentages of the most consumer functions for each query
maxylist = []
## A list to save names of the most consumer functions for each query
maxnamelist = []

## Even in one exception do not order
dont_order = False

for count in range(1, numofqueries+1):
    try:
        max_prcnt = 0
        name_of_max = ''
        
        table_txt = open(tabletxts_path + tabletxt_pfx + (query_list[count-1] if numofqueries != maxnumofqueries else count).__str__() + tabletxt_sfx, 'r')
        
        for each_row in table_txt:
            data = each_row.split('|')
            each_prcnt = float(data[3].replace('%', '').strip())

            if each_prcnt > max_prcnt:
                max_prcnt = each_prcnt
                name_of_max = data[0]
            
        table_txt.close()
        
        maxnamelist.append(name_of_max)
        maxylist.append(max_prcnt)

    ## If there is an exception above, probably the analyzed text is empty or not found because of the syntax errors in the queries
    except Exception as e:
        maxnamelist.append('empty')
        maxylist.append(0)
        
        dont_order = True

maxnamedict = {i:maxnamelist.count(i) for i in maxnamelist}
sorted_maxnamedict = sorted(maxnamedict.items(), key=lambda x:x[1], reverse=True)

## TODO I can do it via also empty functions list, we need to think about that
## If most consumer function not in list then append functions list
for each_pair in sorted_maxnamedict[::-1]:
    if each_pair[0] not in functions:
        if len(functions) <= 1: ## either there is other in the list or empty
            functions.insert(0, each_pair[0])
        else:
            functions.insert(functions.index(functions[-2]), each_pair[0])
        ylist.append([0]*numofqueries)

for count in range(1, numofqueries+1):
    try:
        query_number = query_list[count-1] if numofqueries != maxnumofqueries else count
    
        ## Saves query numbers for x axis of the plot
        xlist.append(query_number.__str__())
    
        max_prcnt = 0
        name_of_max = ''
        
        table_txt = open(tabletxts_path + tabletxt_pfx + query_number.__str__() + tabletxt_sfx, 'r')
        
        for each_row in table_txt:
            data = each_row.split('|')
            each_prcnt = float(data[3].replace('%', '').strip())
            
            if data[0] in functions:
                ylist[functions.index(data[0])][count-1] = float(data[3].replace('%', '').strip())
            else: ## For other functions
                ylist[functions.index(functions[-1])][count-1] += float(data[3].replace('%', '').strip())

            if each_prcnt > max_prcnt:
                max_prcnt = each_prcnt
                name_of_max = data[0]
            
        table_txt.close()
        
        ## Prints depesz url, the most consumer functions and the percentages for each query
        ## Keep in mind that max percentages are not normalized while printing, they are normalizing in the bar chart
        print(tabletxt_pfx + query_number.__str__() + tabletxt_sfx + ' --> ' + name_of_max + ' ' + max_prcnt.__str__())

    ## If there is an exception above, probably the analyzed text is empty or not found because of the syntax errors in the queries
    except Exception as e:
        print(e)
        print(tabletxt_pfx + query_number.__str__() + tabletxt_sfx + ' --> empty')
        print()

print()      

## This prints number of the most consumer functions out of 99 (numofqueries) query in descending order
pprint.pprint(sorted_maxnamedict)

print(functions)

## This is for if you add extra functions to functions list and don't specify the color for them, it generates random colors for them.
import random
random.seed(1487) ## generate same colors for same number of functions by seeding random
get_rand_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))

## Either functions removed or added to functions list it arranges the colors list accordingly, and for example, after adding extra functions, it adds extra colors randomly
if len(functions) > len(colors):
    extra_colors = get_rand_colors(len(functions) - len(colors))
    for each_color in extra_colors:
        colors.insert(colors.index(colors[-2]), each_color)
elif len(functions) < len(colors):
    for i in range(0, len(colors) - len(functions)):
        colors.pop(colors.index(colors[-2]))

## Order lists by max consumer functions
if not dont_order:
    temp_functions = functions
    for each_pair in sorted_maxnamedict[::-1]:
        ylist.insert(0, ylist.pop(temp_functions.index(each_pair[0])))
        colors.insert(0, colors.pop(temp_functions.index(each_pair[0])))
        functions.remove(each_pair[0]) ## remove max names from functions
        functions.insert(0, each_pair[0]) ## insert them as reversed order in the beginning of list

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
        if i != skip_index:
            colors[i] = h2color #'#808080' #'black'
        else:
            colors[i] = h1color #'blue'

## make bottomed
if highlight and args.bottomed:
    ## bir tane degistirecegim icin burada, index karismayacak yoksa temp tutmak lazim
    ylist.insert(0, ylist.pop(functions.index(args.hlfunc)))
    colors.insert(0, colors.pop(functions.index(args.hlfunc)))
    functions.remove(args.hlfunc) ## remove max names from functions
    functions.insert(0, args.hlfunc) ## insert them as reversed order in the beginning


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

