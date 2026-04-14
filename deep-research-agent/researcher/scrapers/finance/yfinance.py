import yfinance as yf
import pandas as pd

class CompanyFinancialData:
    """
    Fetches various types of financial data for a given company ticker.
    """
    def __init__(self, ticker_symbol: str, period: str = "1d"):
        """
        Initializes the fetcher with a company ticker and data period.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., "AAPL").
            period: The period for historical data (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max").
        """
        if not ticker_symbol:
            raise ValueError("Ticker symbol cannot be empty.")
        self.ticker_symbol = ticker_symbol
        self.period = period
        self._ticker = yf.Ticker(ticker_symbol)

    def get_price_history(self) -> pd.DataFrame | None:
        """
        Fetches historical price data for the specified period.

        Returns:
            A pandas DataFrame containing historical price data, or None if data is not available.
        """
        try:
            history = self._ticker.history(period=self.period)
            if history.empty:
                print(f"No price history data found for {self.ticker_symbol} for period {self.period}.")
                return None
            return history
        except Exception as e:
            print(f"Error fetching price history for {self.ticker_symbol}: {e}")
            return None

    def get_dividends_splits(self) -> dict:
        """
        Fetches dividend and split data.

        Returns:
            A dictionary containing 'dividends' (DataFrame) and 'splits' (DataFrame),
            or empty DataFrames if data is not available.
        """
        data = {}
        try:
            dividends = self._ticker.dividends
            if dividends.empty:
                 print(f"No dividend data found for {self.ticker_symbol}.")
            data['dividends'] = dividends
        except Exception as e:
            print(f"Error fetching dividends for {self.ticker_symbol}: {e}")
            data['dividends'] = pd.DataFrame()

        try:
            splits = self._ticker.splits
            if splits.empty:
                 print(f"No split data found for {self.ticker_symbol}.")
            data['splits'] = splits
        except Exception as e:
            print(f"Error fetching splits for {self.ticker_symbol}: {e}")
            data['splits'] = pd.DataFrame()

        return data

    def _fetch_income_statement(self) -> pd.DataFrame:
        """
        Fetches the income statement.

        Returns:
            A pandas DataFrame containing the income statement, or an empty DataFrame if data is not available.
        """
        try:
            financials = self._ticker.financials
            if financials.empty:
                 print(f"No income statement data found for {self.ticker_symbol}.")
            return financials
        except Exception as e:
            print(f"Error fetching income statement for {self.ticker_symbol}: {e}")
            return pd.DataFrame()

    def _fetch_balance_sheet(self) -> pd.DataFrame:
        """
        Fetches the balance sheet.

        Returns:
            A pandas DataFrame containing the balance sheet, or an empty DataFrame if data is not available.
        """
        try:
            balance_sheet = self._ticker.balance_sheet
            if balance_sheet.empty:
                 print(f"No balance sheet data found for {self.ticker_symbol}.")
            return balance_sheet
        except Exception as e:
            print(f"Error fetching balance sheet for {self.ticker_symbol}: {e}")
            return pd.DataFrame()

    def _fetch_cashflow(self) -> pd.DataFrame:
        """
        Fetches the cash flow statement.

        Returns:
            A pandas DataFrame containing the cash flow statement, or an empty DataFrame if data is not available.
        """
        try:
            cashflow = self._ticker.cashflow
            if cashflow.empty:
                 print(f"No cash flow data found for {self.ticker_symbol}.")
            return cashflow
        except Exception as e:
            print(f"Error fetching cash flow for {self.ticker_symbol}: {e}")
            return pd.DataFrame()

    def get_financials(self) -> dict:
        """
        Fetches financial statements (income statement, balance sheet, cash flow).

        Returns:
            A dictionary containing 'financials', 'balance_sheet', and 'cashflow'
            (each a DataFrame), or empty DataFrames if data is not available for a specific type.
        """
        data = {
            'financials': self._fetch_income_statement(),
            'balance_sheet': self._fetch_balance_sheet(),
            'cashflow': self._fetch_cashflow()
        }
        return data

    def get_company_info(self) -> dict | None:
        """
        Fetches general company information.

        Returns:
            A dictionary containing company information, or None if data is not available.
        """
        try:
            info = self._ticker.info
            if not info:
                print(f"No company info found for {self.ticker_symbol}.")
                return None
            return info
        except Exception as e:
            print(f"Error fetching company info for {self.ticker_symbol}: {e}")
            return None

    def get_institutional_holdings(self) -> dict:
        """
        Fetches major and institutional shareholder data.

        Returns:
            A dictionary containing 'major_holders' and 'institutional_holders'
            (each a DataFrame), or empty DataFrames if data is not available.
        """
        data = {}
        try:
            major_holders = self._ticker.major_holders
            if major_holders.empty:
                 print(f"No major holders data found for {self.ticker_symbol}.")
            data['major_holders'] = major_holders
        except Exception as e:
            print(f"Error fetching major holders for {self.ticker_symbol}: {e}")
            data['major_holders'] = pd.DataFrame()

        try:
            institutional_holders = self._ticker.institutional_holders
            if institutional_holders.empty:
                 print(f"No institutional holders data found for {self.ticker_symbol}.")
            data['institutional_holders'] = institutional_holders
        except Exception as e:
            print(f"Error fetching institutional holders for {self.ticker_symbol}: {e}")
            data['institutional_holders'] = pd.DataFrame()

        return data

# Example Usage (Optional - can be removed for production code)
if __name__ == "__main__":
    ticker = "NVDA" # Example ticker
    period = "1d" # Example period

    fetcher = CompanyFinancialData(ticker, period)

    print(f"--- Fetching data for {ticker} ({period}) ---")

    price_history = fetcher.get_price_history()
    if price_history is not None:
        print("\n--- Price History ---")
        print(price_history.head())

    dividends_splits = fetcher.get_dividends_splits()
    print("\n--- Dividends ---")
    print(dividends_splits['dividends'].head())
    print("\n--- Splits ---")
    print(dividends_splits['splits'].head())

    financials_data = fetcher.get_financials()
    print("\n--- Financials (Income Statement) ---")
    print(financials_data['financials'].head())
    print("\n--- Balance Sheet ---")
    print(financials_data['balance_sheet'].head())
    print("\n--- Cash Flow ---")
    print(financials_data['cashflow'].head())

    company_info = fetcher.get_company_info()
    if company_info is not None:
        print("\n--- Company Info ---")
        # Print a few key pieces of info
        print(f"Sector: {company_info.get('sector')}")
        print(f"Industry: {company_info.get('industry')}")
        print(f"Market Cap: {company_info.get('marketCap')}")
        print(f"Website: {company_info.get('website')}")


    holdings_data = fetcher.get_institutional_holdings()
    print("\n--- Major Holders ---")
    print(holdings_data['major_holders'].head())
    print("\n--- Institutional Holders ---")
    print(holdings_data['institutional_holders'].head())

    print("\n--- Data fetching complete ---")