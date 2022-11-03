import argparse
import codecs

parser = argparse.ArgumentParser(description='Create Configuration')
parser.add_argument('-f', '--filename', type=str, help='Specify file name to fix encoding', default='')
args = parser.parse_args()

with codecs.open(args.filename, encoding='utf-8', errors='replace') as file:
    fixedstr = file.read()

with open(args.filename, 'w') as file:
    file.write(fixedstr)

