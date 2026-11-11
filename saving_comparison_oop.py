class portfolio_simulation:
    def __init__(
            self,
            initial_balance: float = 0.0,
            cash_interest: float = 4.5,
            investment_interest: float = 7.0,
            time_horizon: int = 1,
            split: dict = None):

        self.portfolio = {
            "LISA Cash": initial_balance * self.split.get("cash", 0),
            "LISA Investment": initial_balance * self.split.get("investment", 0),
            "ISA Cash": initial_balance * self.split.get("isa_cash", 0),
            "ISA Investment": initial_balance * self.split.get("isa_investment", 0)
        }

        self.balance = initial_balance
        self.history = [initial_balance]
        self.cash_interest = cash_interest
        self.investment_interest = investment_interest
        self.split = split if split is not None else {}
        self.time_horizon = time_horizon

    def simulate_year(self):

        
        cash_allocation = self.balance * self.split.get("cash", 0)
        investment_allocation = self.balance * self.split.get("investment", 0)

        cash_allocation *= 1 + self.cash_interest / 100
        investment_allocation *= 1 + self.investment_interest / 100

        self.balance = cash_allocation + investment_allocation
        self.history.append(self.balance)

    def simulate(self):
        for _ in range(self.time_horizon):
            self.simulate_year()
