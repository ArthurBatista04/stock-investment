import csv
import numpy as np

def pre_process():
	with open('renner.csv', mode='r') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		interval = []
		for (index, data) in enumerate(csv_reader):
			year = data['Data/Hora'][-4:]
			if(year == '2014' or year == '2015'):
				interval.append(float(data['Variação'].replace(',','.')))
		return variance_38d_6m_1y(interval)

def variance_38d_6m_1y(interval):
	days_38 = np.array_split(interval, 38) # [[1,2,... 38], [] ... 13]
	months_6 = np.array_split(interval, 123)
	year_1 = np.array_split(interval, 247)
	var_38 = []
	var_6 = []
	var_1 = []
	for interval in days_38:
		var_38.append(np.var(interval))
	for interval in months_6:
		var_6.append(np.var(interval))
	for interval in year_1:
		var_1.append(np.var(interval))
	return np.mean(var_38) * 3 + np.mean(var_6) * 2 + np.mean(var_1)

def main():
	print(pre_process())# [0.3,0.2,0.1] A B C => variação 38 * 3 + variação 6 meses * 2 + variação 1 ano * 3
	


if __name__ == "__main__":
	main()
