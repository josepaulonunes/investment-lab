# How the screener sets a fair price (Nov 2026)

## The problem
The first version of the screener assumed each company keeps today's growth (up to 25% a year) for 10 straight years, with a 9% discount rate for everyone. That made Nvidia look worth twice its price and Autodesk more than twice. Research says that assumption is too generous, so I changed it.

## What the research says
- High growth rarely lasts. Chan, Karceski and Lakonishok studied US companies from 1951 to 1997: very high growth happens but is rare, there is almost no persistence beyond chance, and analysts' long term forecasts are too optimistic. Their conclusion: valuations that assume high growth for many years rest on shaky foundations (Journal of Finance, 2003)
- Mauboussin's Base Rate Book looks at the 1,000 biggest companies in the world every year since 1950: very few grow sales above 20% a year for 10 years, and the bigger the company, the rarer it is (Credit Suisse, 2015 and 2016)
- Over the long run, the typical company grows about as fast as the economy (same Chan, Karceski and Lakonishok paper). That is why the growth after year 10 is 2.5%
- The discount rate is the return investors ask for: the risk free rate plus the equity risk premium, scaled by how risky the company is (CAPM). Damodaran's implied equity risk premium for the US was 4.23% in January 2026

## The new method
- Risk free rate: the US 10 year Treasury yield, downloaded each time the screener runs
- Equity risk premium: 4.23% (Damodaran, January 2026). I update it every January
- Discount rate per company: risk free + beta x 4.23%. Beta is kept between 0.8 and 1.6, because one company's beta from past prices is noisy (Damodaran prefers sector betas for the same reason)
- Growth: today's revenue growth, capped at 25%
- Careful fair price: growth falls in a straight line from today's rate to 2.5% by year 10. This is the standard way to model growth fading (Damodaran's DCF models work the same way)
- Optimistic fair price: today's growth for all 10 years (the old method)

## What the verdicts mean now
- BUY: price below the careful fair price. Good business at a price that works even if growth slows down like it usually does
- FAIR: between the two. A fair price only if growth stays high for longer than most companies manage
- WATCH: above the optimistic price. The price assumes more than today's growth for 10 years. In my words: stupidly expensive
- The weekly check gives BUY EXTRA below the careful price (it already has a safety margin built in, so I don't ask for another 20% on top) and EXPENSIVE above the optimistic one. EXPENSIVE never pauses a plan by itself: changes wait for January, because one point more or less in the discount rate moves the fair price by 20 to 30%

## What I accept
For a company growing 25% a year, the careful price is about half the optimistic one. So most great companies will not be BUY most of the time. That is the honest answer: the market already pays well for quality. A model is a check on my enthusiasm, not a prediction.

## Sources
- Chan, Karceski and Lakonishok, The Level and Persistence of Growth Rates, Journal of Finance 58(2), 2003. https://www.nber.org/papers/w8282
- Mauboussin, Callahan and Majd, The Base Rate Book, Credit Suisse, 2016
- Damodaran, Equity Risk Premiums: Determinants, Estimation and Implications, 2026 edition, and his data page: https://pages.stern.nyu.edu/adamodar/
