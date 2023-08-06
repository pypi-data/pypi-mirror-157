# Nepal Stock Tracker

A python script that gets the stock information as per the company symbol
provided by the user from [Mero Lagani](https://merolagani.com/LatestMarket.aspx). This
script supports for the stock information of Nepal only.

<img src="https://github.com/ghanteyyy/NepalStockTracker/raw/main/NepalStockTracker/assets/1.png">

# Installation

NepalStockTracker is available on PyPI. You can install it through pip:

`pip install NepalStockTracker`

# Usage

- If you want GUI window then Run **NepalStockTracker.py** directly

- To get data only

  ```python
  from NepalStockTracker import tracker

  data = tracker('Company Symbol', show_gui=False)  # Returns stock information of the given company symbol
  print(data.details)  # Printing the stock information from above returned data
  ```
