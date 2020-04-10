class _Position:
    def __init__(self, shares, share_price):
        if share_price <= 0:
            raise ValueError("Please enter a positive number for share_price")
        self.shares = shares
        self.position_size = float(shares * share_price)

    def buy(self, shares, share_price):
        if shares < 0 or share_price <= 0:
            raise ValueError(" Please enter positive numbers for shares and share_price")
        if self.shares >= 0:
            self.shares += shares
            self.position_size += shares * share_price
            return float('NaN')
        else:  # covering short position
            if abs(self.shares) >= shares:
                profit = (self.position_size / self.shares) * shares - share_price * shares
                self.position_size += share_price * shares
                self.shares += shares
                return profit
            else:

                self.shares += shares
                self.position_size += self.shares * share_price
                return self.position_size - share_price * self.shares

    def sell(self, shares, share_price):
        if shares < 0 or share_price <= 0:
            raise ValueError(" Please enter positive numbers for shares and share_price")
        if self.shares <= 0:
            self.shares -= shares
            self.position_size -= shares * share_price
            return float('NaN')
        else:  # covering long position
            if self.shares >= shares:
                profit = (self.position_size / self.shares) * shares - share_price * shares
                self.shares -= shares
                return profit
            else:
                self.shares -= shares
                self.position_size -= self.shares * share_price
                return self.position_size - share_price * self.shares

    def clear_position(self, share_price):
        if self.shares < 0:
            self.buy(self.shares, share_price)
        else:
            self.sell(self.shares, share_price)
    def to_dict(self):
        if self.shares != 0:
            return {'shares': self.shares, 'avg_share_price': self.position_size / self.shares}
        else:
            return {'shares': self.shares, 'avg_share_price': 0}