import pandas as pd
import numpy as np

'''
This script compares different savings strategies over time.
It calculates the total savings for each strategy and provides a comparison.

Initial startegies for comparison include:
 - LISA Stocks & Bonds
 - LISA Cash
 - ISA Stocks & Bonds
 - ISA Cash
Which utilise these savings accounts only.

Further mixed strategies can be added to compare combinations of these accounts.
- LISA & ISA Overspill (strategy that utilises LISA accounts to maximum bonus and spills over to ISA accounts)
- Mixed (combination of LISA and ISA accounts using dictionaries to define the allocation ratios)
'''
STARTING_AMOUNT = 0
YEARLY_CONTRIBUTION = 6000
TIME_HORIZON = 40
STOCKS_BONDS_INTEREST = 0.075
CASH_INTEREST = 0.042

CONTROL_VARIABLES = {
    "STARTING_AMOUNT": STARTING_AMOUNT,
    "YEARLY_CONTRIBUTION": YEARLY_CONTRIBUTION,
    "TIME_HORIZON": TIME_HORIZON,
    "STOCKS_BONDS_INTEREST": STOCKS_BONDS_INTEREST,
    "CASH_INTEREST": CASH_INTEREST
}

# Default allocation ratios for mixed strategies
default_allocation = {
    "lisa_stocks_bonds": 0.25,
    "lisa_cash": 0.25,
    "isa_stocks_bonds": 0.25,
    "isa_cash": 0.25
}

stocks_bonds_allocation = {
    "lisa_stocks_bonds": 0.5,
    "lisa_cash": 0.0,
    "isa_stocks_bonds": 0.5,
    "isa_cash": 0.0
}

cash_allocation = {
    "lisa_stocks_bonds": 0.0,
    "lisa_cash": 0.5,
    "isa_stocks_bonds": 0.0,
    "isa_cash": 0.5
}

def display_control_variables():
    for key, value in CONTROL_VARIABLES.items():
        print(f"{key}: {value}")
    print()

def cash(
    time: int = TIME_HORIZON,
    starting_amount: float = 0,
    yearly_contribution: float = YEARLY_CONTRIBUTION,
    ):
    
    portfolio = starting_amount
    for _ in range(time):
        portfolio += yearly_contribution
    return round(portfolio, 2)

def lisa_stocks_bonds(
    interest: float = 0.075,
    time: int = TIME_HORIZON,
    starting_amount: float = 0,
    yearly_contribution: float = YEARLY_CONTRIBUTION,
    ):
    
    portfolio = starting_amount
    for _ in range(time):
        portfolio += yearly_contribution
        portfolio += 0.25 * yearly_contribution if yearly_contribution <= 4000 * 0.25 else 4000 * 0.25
        portfolio *= (1 + interest)
    return round(portfolio, 2)

def lisa_cash(
        interest: float = 0.042,
        time: int = TIME_HORIZON,
        starting_amount: float = 0,
        yearly_contribution: float = YEARLY_CONTRIBUTION,
        ):
    
    return round(lisa_stocks_bonds(
        interest=interest,
        time=time,
        starting_amount=starting_amount,
        yearly_contribution=yearly_contribution
    ), 2)
    
def isa_stocks_bonds(
        interest: float = 0.075,
        time: int = TIME_HORIZON,
        starting_amount: float = 0,
        yearly_contribution: float = YEARLY_CONTRIBUTION,
        ):
    
    portfolio = starting_amount
    for _ in range(time):
        portfolio += yearly_contribution
        portfolio *= (1 + interest)
    return round(portfolio, 2)

def isa_cash(
        interest: float = 0.042,
        time: int = TIME_HORIZON,
        starting_amount: float = 0,
        yearly_contribution: float = YEARLY_CONTRIBUTION,
        ):
    
    return round(isa_stocks_bonds(
        interest=interest,
        time=time,
        starting_amount=starting_amount,
        yearly_contribution=yearly_contribution
    ), 2)

def lisa_isa_overspill(
        time: int = TIME_HORIZON,
        starting_amount: float = 0,
        yearly_contribution: float = YEARLY_CONTRIBUTION,
        interest: float = 0.042,
        ):

    holdings = {
        "lisa": starting_amount if starting_amount <= 4000 else 4000,
        "isa": starting_amount - 4000 if starting_amount > 4000 else 0
    }

    for _ in range(time):
        holdings["lisa"] += yearly_contribution if holdings["lisa"] + yearly_contribution <= 4000 else 4000 - holdings["lisa"]
        overspill = yearly_contribution - (4000 - holdings["lisa"]) if holdings["lisa"] < 4000 else yearly_contribution
        holdings["isa"] += overspill

        holdings["lisa"] *= (1 + interest)
        holdings["isa"] *= (1 + interest)



    return round(holdings["lisa"] + holdings["isa"], 2)

def mixed(
        allocation: dict = default_allocation,
        time: int = TIME_HORIZON,
        starting_amount: float = 0,
        yearly_contribution: float = YEARLY_CONTRIBUTION
        ):


    portfolio = {
        key: starting_amount * allocation[key] for key in allocation
    }

    # Dictionary mapping strategy names to their corresponding functions
    func_dict = {
        "cash": cash,
        "lisa_stocks_bonds": lisa_stocks_bonds,
        "lisa_cash": lisa_cash,
        "isa_stocks_bonds": isa_stocks_bonds,
        "isa_cash": isa_cash,
        "lisa_isa_overspill": lisa_isa_overspill
    }

    for _ in range(time):
        for key in portfolio:
            portfolio[key] += func_dict[key](
                time=1,
                starting_amount=portfolio[key],
                yearly_contribution=yearly_contribution * allocation[key]
            ) - portfolio[key]


    return round(sum(portfolio.values()), 2)


def display_results(results):
    results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    cash_total = cash()
    lisa_stocks_bonds_total = lisa_stocks_bonds(interest=STOCKS_BONDS_INTEREST)
    lisa_cash_total = lisa_cash(interest=CASH_INTEREST)
    isa_stocks_bonds_total = isa_stocks_bonds(interest=STOCKS_BONDS_INTEREST)
    isa_cash_total = isa_cash(interest=CASH_INTEREST)
    lisa_isa_overspill_cash_total = lisa_isa_overspill(interest=CASH_INTEREST)
    lisa_isa_overspill_stocks_bonds_total = lisa_isa_overspill(interest=STOCKS_BONDS_INTEREST)
    mixed_total = mixed(allocation=default_allocation)
    mixed_cash_total = mixed(allocation=cash_allocation)
    mixed_stocks_bonds_total = mixed(allocation=stocks_bonds_allocation)

    results = {
        "cash_total": cash_total,
        "lisa_stocks_bonds_total": lisa_stocks_bonds_total,
        "lisa_cash_total": lisa_cash_total,
        "isa_stocks_bonds_total": isa_stocks_bonds_total,
        "isa_cash_total": isa_cash_total,
        "lisa_isa_overspill_cash_total": lisa_isa_overspill_cash_total,
        "lisa_isa_overspill_stocks_bonds_total": lisa_isa_overspill_stocks_bonds_total,
        "mixed_total": mixed_total,
        "mixed_cash_total": mixed_cash_total,
        "mixed_stocks_bonds_total": mixed_stocks_bonds_total
    }

    display_control_variables()
    display_results(results)