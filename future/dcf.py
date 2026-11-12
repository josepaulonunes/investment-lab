# Value of one share today: the cash of the next 10 years plus what comes after
def dcf_value(cash, growth, discount):
    value = 0
    for year in range(1, 11):
        # 5 years at full growth, then it falls in a straight line to 4% in year 10
        rate = growth
        if year > 5:
            rate = growth + (0.04 - growth) * (year - 5) / 5
        cash = cash * (1 + rate)
        value = value + cash / (1 + discount) ** year
    # After year 10 the cash grows 2.25% a year
    final = cash * 1.0225 / (discount - 0.0225)
    return value + final / (1 + discount) ** 10


# Yearly return if I buy at today's price and the base case happens
def expected_return(price, cash, growth):
    rate = 0.03
    while rate < 0.30 and dcf_value(cash, growth, rate) > price:
        rate = rate + 0.001
    return rate
