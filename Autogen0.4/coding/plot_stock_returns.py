# filename: plot_stock_returns.py
import yfinance as yf
import matplotlib.pyplot as plt

# Define the start date
start_date = '2024-01-01'

# Download the stock data for NVIDIA and TESLA
nvidia_data = yf.download('NVDA', start=start_date)
tesla_data = yf.download('TSLA', start=start_date)

# Calculate the daily returns
nvidia_returns = nvidia_data['Adj Close'].pct_change()
tesla_returns = tesla_data['Adj Close'].pct_change()

# Create the plot
plt.plot(nvidia_returns.index, nvidia_returns, label='NVIDIA')
plt.plot(tesla_returns.index, tesla_returns, label='TESLA')
plt.xlabel('Date')
plt.ylabel('Daily Return')
plt.title('NVIDIA and TESLA Stock Returns YTD 2024')
plt.legend()
plt.grid(True)
plt.savefig('nvidia_tesla_2024_ytd.png')
plt.show()
