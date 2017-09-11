import json;
import re;
from collections import defaultdict;

def getDistinct(list,str):
	uniqueNames = []
	for i in list:
		if(i.get(str,'') not in uniqueNames):
			uniqueNames.append(i.get(str,''));
	return uniqueNames

def getCombo(list):
	uniqueNames = []
	for i in list:
		if(i.get(str,'') not in uniqueNames):
			uniqueNames.append(i.get('manufacturer','')+'-'+i.get('family','')+'-'+i.get('model',''));
	return uniqueNames

def mostCommon (listA):
	d = defaultdict(int)
	for i in listA:
		d[i] += 1
	result = max(d.items(), key=lambda x: x[1])
	return result
	
# Reading the Products data
products = []
for line in open('products.txt', 'r'):
	products.append(json.loads(line))

	
# Reading the listings data
listings = []
for line in open('listings.txt', encoding='utf8'):
	listings.append(json.loads(line))


#Get rid of prefixes for common prefixes for some manufacturers
common_models = []
for y in getDistinct(products,'manufacturer'):
	model_pre = []
	totalByMan = 0
	for x in products:
		if x['manufacturer'] == y and x['model'].find('-') != -1:
			totalByMan += 1
			model_pre.append(x['model'].lower().split('-')[0])
	if model_pre != []:
		if mostCommon(model_pre)[1]/totalByMan > 0.5:
			common_models.append(y)

for y in common_models:
	for x in products:
		if x['manufacturer'] == y and x['model'].find('-') != -1:
			x['model'] = x['model'].split('-')[1]


#Do the matching
output =''
counter = 0
nomatches = 0
for x in products:
	listings_array = []
	model_splits = x['model'].lower().split() #Get list of model words if there is a space
	for y in listings:
		#get acronynm for manufacturer in listings data
		manufacturer_acronynm = ''
		for i in y['manufacturer'].upper().split():
			manufacturer_acronynm += i[0]
		
		#grab the title before 'for' or 'pour' is used to ignore accessories titles
		before_keyword, keyword, after_keyword = '','',''
		before_keyword = y['title']
		if 'for' in y['title']:
			before_keyword, keyword, after_keyword = y['title'].partition('for')
		elif 'pour' in y['title']:
			before_keyword, keyword, after_keyword = y['title'].partition('pour')
		
		#The magic
		if (re.search(r'%s' % x['manufacturer'],before_keyword,re.IGNORECASE)
			and (re.search(r'%s'% x['manufacturer'],y['manufacturer'],re.IGNORECASE)
			or re.search(r'%s'% x['manufacturer'],manufacturer_acronynm,re.IGNORECASE))):		#First check manufacturer is in title and if it is in manufacturer of listing or acronynm of it
			if (len(model_splits) == 1 and re.search(r'\b%s\b'% x['model'],before_keyword,re.IGNORECASE)
				and x['model'].find('-') == -1
				and re.search(r'\b%s\b'% x.get('family',''),before_keyword,re.IGNORECASE)):		#Condition #1 - When model is 1 word, check model and family in title
					listings_array.append(y)
					counter=counter +1
			elif ((len(model_splits) > 1 or x['model'].find('-') != -1) and
				(re.search(r'\b%s\b'% x['model'].replace(' Zoom','Z'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace(' Wide','W'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace('IS','Image Stabilized'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace('HS','High Sensitivity'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace('UZ','Ultra Zoom'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace('Wide','High Sensitivity'),before_keyword,re.IGNORECASE)
				or re.search(r'\b%s\b'% x['model'].replace(' ','-'),before_keyword,re.IGNORECASE))):	#Condition #2 - When model > 1 word, replace acronym models to equivalent meanings and hyphens for spaces to match to title
					listings_array.append(y)
					counter=counter +1
			elif ((len(model_splits) > 1 or x['model'].find('-') != -1) and
				(set(model_splits).issubset(set(before_keyword.lower().split()))
				or 
				set(x['model'].replace(' Zoom','Z').replace(' Wide','W').replace('IS','Image Stabilized')
				.replace('HS','High Sensitivity').replace('UZ','Ultra Zoom').replace('Wide','High Sensitivity')
				.replace('-',' ')
				.split()).issubset(set(before_keyword.lower().split())))):						  #Condition #3 - When model is > 1 word, search all words in title in any different order 
					listings_array.append(y)
					counter=counter +1
	output +='{"product_name":"' + x.get('product_name','') + '","listings":['
	for L in listings_array[:-1]:
		output += json.dumps(L).strip() + ','
		output += json.dumps(listings_array[-1]).strip()
	output += ']}\n'																				#Append product and equivalent listings to final variable
			
print ('Matched a total of '+str(counter)+' out of '+ str(len(listings)))							#Displays listings that have matched

# Writing results
with open('results.txt', 'w') as outfile:  
	outfile.write(output)
	
