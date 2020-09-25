import csv
import os
import numpy as np
from genetic_algorithm import genetic_algorithm
from bank import Bank


def pre_process():
    companies = [i for i in os.listdir('./csv')]

    companies_variances = []
    companies_prices = {}
    for company in companies:
        prices = []
        with open('./csv/' + company, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            interval = []
            for data in csv_reader:
                year = data['Data/Hora'][-4:]
                if(year == '2014' or year == '2015'):
                    interval.append(float(data['Variação'].replace(',', '.')))
                else:
                    prices.append(float(data['Cotação'].replace(',', '.')))
                companies_prices[company[:-4]] = prices
            companies_variances.append(variance_38d_6m_1y(interval))

    return companies, companies_variances, companies_prices


def variance_38d_6m_1y(interval):
    days_38 = np.array_split(interval, 38)  # [[1,2,... 38], [] ... 13]
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


def simulator_setup(companies, initial_distribution, amount_to_invest):
    banks = {}
    for index, company in enumerate(companies):
        banks[company[:-4]] = Bank(amount_to_invest *
                                   initial_distribution[index])
    return banks


def print_banks(companies, banks):
    for company in companies:
        print(company[:-4])
        print(
            f"shares: {banks[company[:-4]].number_of_shares} | safe: {banks[company[:-4]].safe_box} ")


def main():
    companies, variance, companies_prices = pre_process()
    weakest, strongest = genetic_algorithm(1000, variance)

    banks = simulator_setup(companies, weakest.gene, 100000)
    for company, prices in companies_prices.items():
        banks[company].purchase(1, prices[0])

    print_banks(companies, banks)


if __name__ == "__main__":
    main()
