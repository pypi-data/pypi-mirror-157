'''
Nepal-Stock-Tracker

A python script that gets the stock information as per the company symbol
provided by the user from https://merolagani.com/LatestMarket.aspx. This
script supports for the stock information of Nepal only.

By ghanteyyy https://github.com/ghanteyyy
MIT License

Usage:
    - If you want GUI window then Run NepalStockTracker.py directly

    - To get data of respective company only

        from NepalStockTracker import tracker

        data = tracker('Company Symbol', show_gui=False)  # Returns stock information of the given company symbol
        print(data.details)  # Printing the stock information from above returned data'''


__all__ = ['tracker']
__version__ = '0.0.1'
__author__ = 'ghanteyyy'


from . import NepalStockTracker


def tracker(company_symbol, show_gui):
    ''' - company_symbol must be the abbreviation of company name
        - show_gui must be either True or False
            when True it shows the GUI window
    '''

    nsm = NepalStockTracker.StockTracker(company_symbol, show_gui)

    if nsm:
        return nsm
