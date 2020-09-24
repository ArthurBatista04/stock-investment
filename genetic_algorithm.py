import csv

quant = 10
interval = 15

def pre_process():
	with open('renner.csv', mode='r') as csv_file:
		variance = [0 for i in range(15)]
		csv_reader = csv.DictReader(csv_file)
		
		count2014 = 0
		count2015 = 0
		count = 0
		for (index, data) in enumerate(csv_reader):
			if(data['Data/Hora'].endswith('2014')):
				count2014 += float(data['Variação'].replace(',', '.'))
			if(data['Data/Hora'].endswith('2015')):
				count2015 += float(data['Variação'].replace(',', '.'))
			if(index % 15 == 0):
				variance[count] = data['Variação'].replace(',', '.')
				count+=1
		print(count2014/247)
		print(count2015/247)


def main():
	pre_process()


if __name__ == "__main__":
	main()
