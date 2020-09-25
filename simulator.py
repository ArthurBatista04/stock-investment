import csv
import os
import numpy as np
from genetic_algorithm import genetic_algorithm

def pre_process():
	companies = [ i for i in os.listdir('./csv')]

	companies_variances = []
	for company in companies:
		with open('./csv/' + company, mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file)
			interval = []
			for (index, data) in enumerate(csv_reader):
				year = data['Data/Hora'][-4:]
				if(year == '2014' or year == '2015'):
					interval.append(float(data['Variação'].replace(',','.')))
			companies_variances.append(variance_38d_6m_1y(interval))

	return companies,companies_variances

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
	companies, variance = pre_process()
	x = {i:variance[index] for (index,i) in enumerate(companies)}
	a = sorted(x.items(), key=lambda y: y[1])    
	print(a)
	print()
	for (index,i) in enumerate(a):
		print(f' PICK NUMBER {index+1} = {i[0]}')
	print()
	saldo = 100000
	x, y = genetic_algorithm(1000,variance)
	for (index,i) in enumerate(x.gene):
		print(f'{companies[index]} =  {i * saldo}')
	
	


if __name__ == "__main__":
	main()
