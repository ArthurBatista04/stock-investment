class Bank(object):
    def __init__(self, safe_box):
        self.number_of_shares = 0
        self.safe_box = safe_box

    def purchase(self, porcentage, value_per_share):
        if(self.safe_box > 0 and self.safe_box >= value_per_share):
            value_to_buy = self.safe_box * porcentage
            while(value_to_buy >= value_per_share):
                self.safe_box -= value_per_share
                self.number_of_shares += 1
                value_to_buy -= value_per_share

    def sell(self, porcentage, value_per_share):
        if(self.number_of_shares > 1):
            number_of_shares_to_sell = abs(self.number_of_shares * porcentage)
            self.number_of_shares -= number_of_shares_to_sell
            self.safe_box += number_of_shares_to_sell * value_per_share
