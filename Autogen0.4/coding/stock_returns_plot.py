# filename: stock_returns_plot.py
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Define the stock tickers and the start date
tickers = ['NVIDIA', 'Tesla']
start_date = '2024-01-01'

# Download the data
data = yf.download(tickers, start=start_date)['Adj Close']

# Calculate the daily returns
returns = data.pct_change()

# Plot the returns
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(returns[ticker], label=ticker)
plt.title('NVIDIA and Tesla Stock Returns YTD 2024')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.legend()
plt.savefig('nvidia_tesla_2024_ytd.png')
plt.show()
