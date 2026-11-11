class portfolio_simulation:
    """Class to simulate a savings portfolio with different account types and contributions."""
    def __init__(
            self,
            initial_balance: float = 0.0,
            cash_interest: float = 4.5,
            investment_interest: float = 7.0,
            time_horizon: int = 1,
            yearly_contribution: float = 0.0,
            yearly_increase: float = 0,
            current_year: int = 0,
            split: dict = None,
            lisa_overspill: bool = False):
        """Initialize the portfolio simulation with the given parameters."""

        self.portfolio = {
            "LISA Cash": initial_balance * (split.get("lisa_cash", 0) if split else 0),
            "LISA Stocks": initial_balance * (split.get("lisa_stocks", 0) if split else 0),
            "ISA Cash": initial_balance * (split.get("isa_cash", 0) if split else 0),
            "ISA Stocks": initial_balance * (split.get("isa_stocks", 0) if split else 0)
        }

        self.balance = initial_balance
        self.history = [initial_balance]
        self.cash_interest = cash_interest
        self.investment_interest = investment_interest
        self.split = split if split is not None else {}
        self.time_horizon = time_horizon
        self.yearly_contribution = yearly_contribution
        self.yearly_increase = yearly_increase
        self.current_year = current_year
        self.lisa_overspill = lisa_overspill
        self.cash_comparison = 0.0

    def simulate_year(self):
        """Simulate the portfolio for one year, applying interest and yearly contributions."""

        if self.lisa_overspill and self.yearly_contribution * (
            self.split.get("lisa_cash", 0) + 
            self.split.get("lisa_stocks", 0)
            ) > 4000:
                
                lisa_contribution = 4000
                isa_contribution = self.yearly_contribution - lisa_contribution
                lisa_cash_ratio = self.split.get("lisa_cash", 0) / (self.split.get("lisa_cash", 0) + self.split.get("lisa_stocks", 0)) if (self.split.get("lisa_cash", 0) + self.split.get("lisa_stocks", 0)) > 0 else 0
                isa_cash_ratio = self.split.get("isa_cash", 0) / (self.split.get("isa_cash", 0) + self.split.get("isa_stocks", 0)) if (self.split.get("isa_cash", 0) + self.split.get("isa_stocks", 0)) > 0 else 0

                self.portfolio["LISA Cash"] += (lisa_contribution + 1000) * lisa_cash_ratio
                self.portfolio["LISA Stocks"] += (lisa_contribution + 1000) * (1 - lisa_cash_ratio)
                self.portfolio["ISA Cash"] += isa_contribution * isa_cash_ratio
                self.portfolio["ISA Stocks"] += isa_contribution * (1 - isa_cash_ratio)

        else:
            self.portfolio["ISA Cash"] += self.yearly_contribution * self.split.get("isa_cash", 0)
            self.portfolio["ISA Stocks"] += self.yearly_contribution * self.split.get("isa_stocks", 0)
            self.portfolio["LISA Cash"] += self.yearly_contribution * self.split.get("lisa_cash", 0)
            self.portfolio["LISA Cash"] += min(4000, self.yearly_contribution * self.split.get("lisa_cash", 0) * 0.25)
            self.portfolio["LISA Stocks"] += self.yearly_contribution * self.split.get("lisa_stocks", 0)
            self.portfolio["LISA Stocks"] += min(4000, self.yearly_contribution * self.split.get("lisa_stocks", 0) * 0.25)

        self.portfolio["ISA Cash"] *= 1 + self.cash_interest / 100
        self.portfolio["ISA Stocks"] *= 1 + self.investment_interest / 100
        self.portfolio["LISA Cash"] *= 1 + self.cash_interest / 100
        self.portfolio["LISA Stocks"] *= 1 + self.investment_interest / 100

        self.cash_comparison += self.yearly_contribution

        self.balance = sum(self.portfolio.values())
        self.history.append(self.balance)

    def simulate(self):
        """Simulate the portfolio over the entire time horizon."""
        if self.split is None:
            return
        for _ in range(self.time_horizon):
            self.simulate_year()
            self.increase_yearly_contribution()
            self.current_year += 1

    def get_history(self):
        """Return the historical portfolio balances."""
        return self.history
    
    def get_portfolio(self):
        """Return the current portfolio balances."""
        return self.portfolio

    def get_balance(self):
        """Return the current total portfolio balance."""
        return self.balance

    def get_split(self):
        """Return the current split configuration."""
        return self.split

    def increase_yearly_contribution(self):
        
        """Increase the yearly contribution by a fixed amount or a percentage."""

        self.yearly_contribution *= 1 + self.yearly_increase / 100

    def display_portfolio(self):
        """Display the current portfolio balances."""
        print("Portfolio Breakdown:")
        for account, balance in self.portfolio.items():
            value = '{:,.2f}'.format(balance)
            print(f"{account}: {value}")
        print(f"Total balance: {self.get_balance():,.2f}")
        print(f"Cash comparison: {self.cash_comparison:,.2f}")


if __name__ == "__main__":
    portfolio = portfolio_simulation(
        yearly_contribution=10000,
        yearly_increase=5,
        cash_interest=2,
        investment_interest=7,
        time_horizon=30,
        split={
            "isa_cash": 0.3,
            "isa_stocks": 0.3,
            "lisa_cash": 0.2,
            "lisa_stocks": 0.2
        }
    )
    
    portfolio.simulate()
    portfolio.display_portfolio()

