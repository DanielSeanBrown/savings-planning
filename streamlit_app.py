import pandas as pd
import plotly.express as px
import streamlit as st


ACCOUNT_NAMES = ["LISA Cash", "LISA Stocks", "ISA Cash", "ISA Stocks"]


def normalise_split(split: dict) -> dict:
    """Return allocation weights that sum to 1."""
    values = {name: max(0.0, float(split.get(name, 0.0))) for name in ACCOUNT_NAMES}
    total = sum(values.values())
    if total <= 0:
        raise ValueError("Allocate at least some contributions to an account.")
    return {name: value / total for name, value in values.items()}


def simulate_portfolio(
    initial_balance: float,
    yearly_contribution: float,
    yearly_increase_pct: float,
    cash_interest_pct: float,
    investment_return_pct: float,
    years: int,
    split: dict,
    lisa_overspill: bool = True,
    lisa_annual_limit: float = 4000.0,
    lisa_bonus_rate_pct: float = 25.0,
) -> pd.DataFrame:
    """
    Annual savings simulation.

    Contributions are added at the start of each year, the LISA bonus is
    added to eligible LISA contributions, and then annual growth is applied.
    This is an annual approximation; it does not model the exact date on
    which a LISA provider credits each bonus.
    """
    weights = normalise_split(split)

    # Allocate the opening balance using the same portfolio weights.
    balances = {name: initial_balance * weights[name] for name in ACCOUNT_NAMES}

    rows = [{
        "Year": 0,
        **balances,
        "Total Contributions": 0.0,
        "LISA Bonus": 0.0,
        "Investment Growth": 0.0,
        "Portfolio Value": sum(balances.values()),
        "Cumulative Contributions": initial_balance,
    }]

    contribution = float(yearly_contribution)
    cumulative_contributions = float(initial_balance)

    lisa_cash_weight = weights["LISA Cash"]
    lisa_stocks_weight = weights["LISA Stocks"]
    lisa_weight = lisa_cash_weight + lisa_stocks_weight
    isa_cash_weight = weights["ISA Cash"]
    isa_stocks_weight = weights["ISA Stocks"]
    isa_weight = isa_cash_weight + isa_stocks_weight

    for year in range(1, years + 1):
        opening_total = sum(balances.values())

        # Initially allocate the year's contribution according to the chosen split.
        lisa_cash_contribution = contribution * lisa_cash_weight
        lisa_stocks_contribution = contribution * lisa_stocks_weight
        isa_cash_contribution = contribution * isa_cash_weight
        isa_stocks_contribution = contribution * isa_stocks_weight

        # Apply one £4,000 annual LISA contribution limit across BOTH LISA types.
        total_lisa_contribution = lisa_cash_contribution + lisa_stocks_contribution
        lisa_bonus = min(
            lisa_annual_limit * lisa_bonus_rate_pct / 100.0,
            total_lisa_contribution * lisa_bonus_rate_pct / 100.0,
        )

        if total_lisa_contribution > lisa_annual_limit:
            if lisa_overspill:
                excess = total_lisa_contribution - lisa_annual_limit
                # Scale both LISA contributions proportionally down to the limit.
                if total_lisa_contribution > 0:
                    scale = lisa_annual_limit / total_lisa_contribution
                    lisa_cash_contribution *= scale
                    lisa_stocks_contribution *= scale

                # Divert the excess into the ISA, preserving the ISA cash/stocks mix.
                if isa_weight > 0:
                    isa_cash_contribution += excess * isa_cash_weight / isa_weight
                    isa_stocks_contribution += excess * isa_stocks_weight / isa_weight
                else:
                    # If no ISA allocation was specified, keep the excess outside
                    # the LISA rather than silently exceeding the LISA allowance.
                    isa_cash_contribution += excess
            else:
                # If overspill is disabled, contributions above the LISA limit
                # are simply not allocated to the LISA in this simplified model.
                excess = total_lisa_contribution - lisa_annual_limit
                scale = lisa_annual_limit / total_lisa_contribution
                lisa_cash_contribution *= scale
                lisa_stocks_contribution *= scale

        # Allocate the single LISA bonus in proportion to the eligible LISA deposits.
        eligible_lisa_total = lisa_cash_contribution + lisa_stocks_contribution
        if eligible_lisa_total > 0:
            lisa_cash_bonus = lisa_bonus * lisa_cash_contribution / eligible_lisa_total
            lisa_stocks_bonus = lisa_bonus * lisa_stocks_contribution / eligible_lisa_total
        else:
            lisa_cash_bonus = 0.0
            lisa_stocks_bonus = 0.0

        balances["LISA Cash"] += lisa_cash_contribution + lisa_cash_bonus
        balances["LISA Stocks"] += lisa_stocks_contribution + lisa_stocks_bonus
        balances["ISA Cash"] += isa_cash_contribution
        balances["ISA Stocks"] += isa_stocks_contribution

        # Apply annual growth after contributions and bonus.
        before_growth = sum(balances.values())
        balances["LISA Cash"] *= 1 + cash_interest_pct / 100.0
        balances["ISA Cash"] *= 1 + cash_interest_pct / 100.0
        balances["LISA Stocks"] *= 1 + investment_return_pct / 100.0
        balances["ISA Stocks"] *= 1 + investment_return_pct / 100.0
        after_growth = sum(balances.values())

        annual_growth = after_growth - before_growth
        cumulative_contributions += contribution
        rows.append({
            "Year": year,
            **balances,
            "Total Contributions": contribution,
            "LISA Bonus": lisa_bonus,
            "Investment Growth": annual_growth,
            "Portfolio Value": after_growth,
            "Cumulative Contributions": cumulative_contributions,
        })

        contribution *= 1 + yearly_increase_pct / 100.0

    return pd.DataFrame(rows)


st.set_page_config(page_title="Savings Portfolio Simulator", page_icon="📈", layout="wide")
st.title("Savings Portfolio Simulator")
st.caption(
    "Explore how contributions, account allocation, LISA bonuses and assumed "
    "returns affect your projected savings."
)

with st.sidebar:
    st.header("Simulation settings")
    initial_balance = st.number_input("Initial portfolio (£)", min_value=0.0, value=0.0, step=500.0)
    yearly_contribution = st.number_input("First-year contribution (£)", min_value=0.0, value=9600.0, step=500.0)
    yearly_increase_pct = st.number_input("Annual contribution increase (%)", min_value=-100.0, value=0.0, step=1.0)
    years = st.slider("Time horizon (years)", min_value=1, max_value=50, value=30)

    st.divider()
    st.subheader("Assumed annual returns")
    cash_interest_pct = st.number_input("Cash interest (%)", min_value=-100.0, max_value=100.0, value=3.5, step=0.25)
    investment_return_pct = st.number_input("Investment return (%)", min_value=-100.0, max_value=100.0, value=7.0, step=0.25)

    st.divider()
    st.subheader("Contribution allocation")
    st.caption("Set the share of each year's contribution allocated to each account.")
    lisa_cash_pct = st.slider("LISA Cash (%)", 0, 100, 20)
    lisa_stocks_pct = st.slider("LISA Stocks (%)", 0, 100, 20)
    isa_cash_pct = st.slider("ISA Cash (%)", 0, 100, 30)
    isa_stocks_pct = st.slider("ISA Stocks (%)", 0, 100, 30)
    split_total = lisa_cash_pct + lisa_stocks_pct + isa_cash_pct + isa_stocks_pct
    st.caption(f"Allocation total: {split_total}%")
    lisa_overspill = st.checkbox("Move LISA contributions above £4,000 into ISA", value=True)

    if split_total != 100:
        st.warning("The allocation percentages must total 100%. Adjust the sliders before viewing the simulation.")

if split_total == 100:
    split = {
        "LISA Cash": lisa_cash_pct / 100.0,
        "LISA Stocks": lisa_stocks_pct / 100.0,
        "ISA Cash": isa_cash_pct / 100.0,
        "ISA Stocks": isa_stocks_pct / 100.0,
    }

    history = simulate_portfolio(
        initial_balance=initial_balance,
        yearly_contribution=yearly_contribution,
        yearly_increase_pct=yearly_increase_pct,
        cash_interest_pct=cash_interest_pct,
        investment_return_pct=investment_return_pct,
        years=years,
        split=split,
        lisa_overspill=lisa_overspill,
    )

    final = history.iloc[-1]
    total_paid_in = final["Cumulative Contributions"]
    total_bonus = history["LISA Bonus"].sum()
    total_growth = history["Investment Growth"].sum()

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Projected portfolio", f"£{final['Portfolio Value']:,.0f}")
    metric2.metric("Contributions", f"£{total_paid_in:,.0f}")
    metric3.metric("LISA bonuses", f"£{total_bonus:,.0f}")
    metric4.metric("Growth", f"£{total_growth:,.0f}")

    st.subheader("Portfolio growth")
    growth_chart = px.line(
        history,
        x="Year",
        y=["Portfolio Value", "Cumulative Contributions"],
        labels={"value": "Value (£)", "variable": "Series"},
        markers=True,
    )
    growth_chart.update_layout(legend_title_text="", hovermode="x unified")
    st.plotly_chart(growth_chart, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Account balances over time")
        account_chart = px.area(
            history,
            x="Year",
            y=ACCOUNT_NAMES,
            labels={"value": "Balance (£)", "variable": "Account"},
        )
        st.plotly_chart(account_chart, use_container_width=True)

    with right:
        st.subheader("Final portfolio allocation")
        allocation = pd.DataFrame({
            "Account": ACCOUNT_NAMES,
            "Balance": [final[name] for name in ACCOUNT_NAMES],
        })
        allocation = allocation[allocation["Balance"] > 0]
        if not allocation.empty:
            allocation_chart = px.pie(
                allocation,
                names="Account",
                values="Balance",
                hole=0.45,
            )
            st.plotly_chart(allocation_chart, use_container_width=True)
        else:
            st.info("No opening balance or contributions have been allocated.")

    st.subheader("Annual breakdown")
    display_history = history.copy()
    money_columns = ACCOUNT_NAMES + [
        "Total Contributions", "LISA Bonus", "Investment Growth",
        "Portfolio Value", "Cumulative Contributions"
    ]
    for column in money_columns:
        display_history[column] = display_history[column].map(lambda x: f"£{x:,.2f}")
    st.dataframe(display_history, use_container_width=True, hide_index=True)

    st.download_button(
        "Download simulation as CSV",
        data=history.to_csv(index=False).encode("utf-8"),
        file_name="savings_portfolio_projection.csv",
        mime="text/csv",
    )
else:
    st.info("Once the allocation totals 100%, the simulation and charts will appear.")

st.divider()
st.caption(
    "Model limitations: annual periods; contributions and LISA bonuses are assumed "
    "to be added before that year's growth; returns are constant assumptions, not "
    "forecasts. Tax rules, provider fees, inflation, market volatility and exact "
    "LISA bonus-crediting dates are not modelled."
)
