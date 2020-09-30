import csv
import os
import numpy as np
from genetic_algorithm import genetic_algorithm
from bank import Bank

indicators_interval = 10


def pre_process():
    companies = [i for i in os.listdir('./csv')]

    companies_variances = []
    companies_prices = []
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
                    prices.append(float(
                        data['Cotação'].replace(',', '.')))
            companies_prices.append(prices[::-1])
            companies_variances.append(variance_38d_6m_1y(interval[::-1]))

    return companies, companies_variances, companies_prices


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
    print(initial_distribution)
    t = sum(initial_distribution)
    for i, j in enumerate(initial_distribution):
        initial_distribution[i] = j / t
    print(sum(initial_distribution))
    print(initial_distribution)
    # if(sum(initial_distribution) > 1):
    #     difference = sum(initial_distribution) - 1
    #     index = initial_distribution.index(max(initial_distribution))
    #     initial_distribution[index] -= difference
    # elif(sum(initial_distribution) < 1):
    #     difference = 1 - sum(initial_distribution)
    #     index = initial_distribution.index(max(initial_distribution))
    #     initial_distribution[index] += difference
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
            f"share: {companies[index][:-4]} initial_value: {banks[index].initial_value} | safe: {banks[index].safe_box} | result: {banks[index].safe_box - banks[index].initial_value} | percentage: {int(calculate_percentage(banks[index].initial_value, banks[index].safe_box))}% ")
        print('========================================================================================================================')

    print(
        f"Initial value: {initial_value} | Final value: {final_value} | Percentage: {int(calculate_percentage(initial_value, final_value))}%")
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

    return 100 - (100 / (1 + (price_gain() / price_loss())))


def indicator(company_prices, current_day):
    sma = simple_moving_avarage(company_prices, current_day)
    rsi = relative_strength_index(company_prices, current_day)
    if(company_prices[current_day] < sma):
        if(rsi >= 70 and rsi < 80):
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
    percentage = calculate_percentage(
        highest_profit.initial_value, highest_profit.safe_box)
    print(
        f"Higher profit was from {share_name[:-4]} share with profit of {int(percentage)}%")


def print_lowest_profit(banks, companies):
    profits = []
    for bank in banks:
        profits.append(bank.safe_box - bank.initial_value)
    lowest_profit = banks[profits.index(min(profits))]
    share_name = companies[profits.index(min(profits))]
    percentage = calculate_percentage(
        lowest_profit.initial_value, lowest_profit.safe_box)
    print(
        f"Lower profit was from {share_name[:-4]} share with profit of {int(percentage)}%")


def calculate_percentage(initial_value, final_value):
    return ((final_value - initial_value) /
            initial_value) * 100


def main():
    companies, variance, companies_prices_2016 = pre_process()
    _, strongest = genetic_algorithm(1000, variance)

    banks = simulator_setup(len(companies), strongest.gene, 100000)

    for index in range(len(companies)):
        company_prices = companies_prices_2016[index]
        for current_day in range(indicators_interval, len(company_prices)):
            call = indicator(company_prices, current_day)
            if(call[0] == 'purchase'):
                banks[index].purchase(call[1], company_prices[current_day])
            elif(call[0] == 'sell'):
                banks[index].sell(call[1], company_prices[current_day])

    for index in range(len(companies)):
        banks[index].sell(1, companies_prices_2016[index][-1])

    print_banks(companies, banks)

    print_highest_profit(banks, companies)

    print_lowest_profit(banks, companies)


if __name__ == "__main__":
    main()
