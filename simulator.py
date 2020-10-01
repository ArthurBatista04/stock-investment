import csv
import os
import numpy as np
from genetic_algorithm import genetic_algorithm
from bank import Bank

indicators_interval = 10
MONTHS = {0: 'January',
		  1: 'February',
		  2: 'March',
		  3: 'April',
		  4: 'May',
		  5: 'June',
		  6: 'July',
		  7: 'August',
		  8: 'September',
		  9: 'October',
		  10: 'November',
		  11: 'December'}


def pre_process():
	companies = [i for i in os.listdir('./csv')]

	companies_variances = []
	companies_prices = []
	companies_last_day_month_index = []
	for company in companies:
		prices = []
		dates_2016 = []
		with open('./csv/' + company, mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file)
			interval = []
			for index, data in enumerate(csv_reader):
				day, month, year = data['Data/Hora'].split('/')
				if(year == '2014' or year == '2015'):
					interval.append(float(data['Variação'].replace(',', '.')))
				else:
					prices.append(float(
						data['Cotação'].replace(',', '.')))
					dates_2016.append([int(day), int(month)-1])
			companies_prices.append(prices[::-1])
			companies_variances.append(variance_38d_6m_1y(interval[::-1]))
			companies_last_day_month_index.append(
				get_last_day_month_index(dates_2016[::-1]))
	return companies, normalize(companies_variances), companies_prices, companies_last_day_month_index


def get_last_day_month_index(dates):
	last_day_month_index = [{'day': 0, 'index': 0} for _ in range(12)]
	for index, data in enumerate(dates):
		day, month = data
		if(last_day_month_index[month]['day'] < day):
			last_day_month_index[month]['index'] = index
			last_day_month_index[month]['day'] = day
	return [i['index'] for i in last_day_month_index]


def normalize(values):
	return [i/sum(values) for i in values]


def variance_38d_6m_1y(interval):
	days_38 = np.array_split(interval, 38)
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


def simulator_setup(number_of_companies, initial_distribution, amount_to_invest):
	banks = []
	if(sum(initial_distribution) > 1):
		difference = sum(initial_distribution) - 1
		index = initial_distribution.index(max(initial_distribution))
		initial_distribution[index] += difference
	elif(sum(initial_distribution) < 1):
		difference = 1 - sum(initial_distribution)
		index = initial_distribution.index(max(initial_distribution))
		initial_distribution[index] += difference
	for i in range(number_of_companies):
		banks.append(Bank(amount_to_invest *
						  initial_distribution[i]))
	return banks


def print_banks(companies, banks):
	initial_value = 0
	final_value = 0
	for index in range(len(banks)):
		initial_value += banks[index].initial_value
		final_value += banks[index].safe_box
		print(
			f"Share: {companies[index][:-4]} Initial value: {banks[index].initial_value} | Safe box: {banks[index].safe_box} | Result: {banks[index].safe_box - banks[index].initial_value} | Number of shares: {banks[index].number_of_shares} | Percentage: {int(calculate_percentage_of_bank(banks[index].initial_value, banks[index].safe_box))}% ")
		print('========================================================================================================================')

	print(
		f"Initial value: {initial_value} | Final value: {final_value} | Percentage: {int(calculate_percentage_of_bank(initial_value, final_value))}%")
	print('========================================================================================================================')

def print_banks_month(companies, banks, companies_price_last_day_month):
	initial_value = 0
	final_value = 0
	for index in range(len(banks)):
		initial_value += banks[index].initial_value
		final_value += banks[index].safe_box + (banks[index].number_of_shares * companies_price_last_day_month[index])
		print(
			f"Share: {companies[index][:-4]} Initial value: {banks[index].initial_value} | Safe box + Shares Investment : {banks[index].safe_box + (banks[index].number_of_shares * companies_price_last_day_month[index])} | Result: {banks[index].safe_box + (banks[index].number_of_shares * companies_price_last_day_month[index]) - banks[index].initial_value} | Number of shares: {banks[index].number_of_shares} | Percentage: {int(calculate_percentage_of_bank(banks[index].initial_value, banks[index].safe_box + (banks[index].number_of_shares * companies_price_last_day_month[index])))}% ")
		print('========================================================================================================================')

	print(
		f"Initial value: {initial_value} | Safe Box + Shares Investment: {final_value} | Percentage: {int(calculate_percentage_of_bank(initial_value, final_value))}%")
	print('========================================================================================================================')

def simple_moving_avarage(company_prices, current_day):
	if current_day >= indicators_interval:
		return np.mean(company_prices[current_day - indicators_interval: current_day])


def relative_strength_index(company_prices, current_day):
	def price_gain():
		gain = 0
		for i in range(current_day - 1, current_day - indicators_interval, -1):
			if company_prices[i] - company_prices[i - 1] > 0:
				gain += abs(company_prices[i] - company_prices[i - 1])
		return gain / indicators_interval

	def price_loss():
		loss = 0
		for i in range(current_day - 1, current_day - indicators_interval, -1):
			if company_prices[i] - company_prices[i - 1] < 0:
				loss += abs(company_prices[i] - company_prices[i - 1])

		return loss / indicators_interval if loss / indicators_interval > 0 else 1

	return 100 - (100 / (1 + (price_gain()/price_loss())))


def indicator(company_prices, current_day):
	sma = simple_moving_avarage(company_prices, current_day)
	rsi = relative_strength_index(company_prices, current_day)
	if(company_prices[current_day] < sma):  # primeiro indicador de venda
		if(rsi >= 70 and rsi < 80):  # confirmação de venda
			return ('sell', 1/3)
		elif(rsi >= 80 and rsi < 90):
			return ('sell', 2/3)
		elif(rsi >= 90 and rsi <= 100):
			return ('sell', 1)
		else:
			return ('no_operation', 0)

	elif(company_prices[current_day] > sma):

		if(rsi <= 30 and rsi > 20):
			return ('purchase', 1/3)
		elif(rsi <= 20 and rsi > 10):
			return ('purchase', 2/3)
		elif(rsi <= 10 and rsi >= 0):
			return ('purchase', 1)
		else:
			return ('no_operation', 0)
	else:
		return ('no_operation', 0)


def print_highest_profit(banks, companies):
	profits = []
	for bank in banks:
		profits.append(bank.safe_box - bank.initial_value)
	highest_profit = banks[profits.index(max(profits))]
	share_name = companies[profits.index(max(profits))]
	percentage = calculate_percentage_of_bank(
		highest_profit.initial_value, highest_profit.safe_box)
	print(
		f"Higher profit was from {share_name[:-4]} share with profit of {int(percentage)}%")


def print_lowest_profit(banks, companies):
	profits = []
	for bank in banks:
		profits.append(bank.safe_box - bank.initial_value)
	lowest_profit = banks[profits.index(min(profits))]
	share_name = companies[profits.index(min(profits))]
	percentage = calculate_percentage_of_bank(
		lowest_profit.initial_value, lowest_profit.safe_box)
	print(
		f"Lower profit was from {share_name[:-4]} share with profit of {int(percentage)}%")


def print_expected_distribuiton(variance, companies):
	print('Expected Distribuiton:')
	res = {}
	for i in range(len(companies)):
		res[variance[i]] = companies[i]
	sort = sorted(variance)
	for place, key in enumerate(sort):
		print(f'{place + 1} place {res[key]} variance = {sort[place]}')

	print()


def print_actual_distribuiton(distribuition, companies):
	print('Actual Distribuiton')
	res = {}
	for i in range(len(companies)):
		res[distribuition[i]] = companies[i]
	sort = sorted(distribuition, reverse=True)
	for place, key in enumerate(sort):
		print(f'{place + 1} place {res[key]} distribuition = {sort[place]} %')

	print()


def calculate_percentage_of_bank(initial_value, final_value):
	return ((final_value - initial_value) /
			initial_value) * 100


def main():
	companies, variance, companies_prices_2016, companies_last_day_month_index = pre_process()
	print_expected_distribuiton(variance, companies)
	opt_gene = genetic_algorithm(1000, variance)

	print_actual_distribuiton(opt_gene.gene, companies)

	banks = simulator_setup(len(companies), opt_gene.gene, 100000)
	last_day_month_index = companies_last_day_month_index[0]
	for current_day in range(indicators_interval, 248):
		for index in range(len(companies)):
			company_prices = companies_prices_2016[index]
			call = indicator(company_prices, current_day)
			if(call[0] == 'purchase'):
				banks[index].purchase(call[1], company_prices[current_day])

			elif(call[0] == 'sell'):

				banks[index].sell(call[1], company_prices[current_day])

		if(current_day in last_day_month_index):
			print(f'Profits from {MONTHS[last_day_month_index.index(current_day)]}')
			print_banks_month(companies, banks, [company_prices[current_day] for company_prices in companies_prices_2016])
			print()

	for index in range(len(companies)):
		banks[index].sell(1, companies_prices_2016[index][-1])

	print('SELLING REMANDING SHARES....')
	print('FINAL RESULTS')
	print_banks(companies, banks)

	print_highest_profit(banks, companies)

	print_lowest_profit(banks, companies)


if __name__ == "__main__":
	main()
