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

    def get_price_history(self) -> str | None:
        """
        Fetches historical price data for the specified period and returns it as a formatted string.

        Returns:
            A string containing historical price data, or a message indicating no data is available, or None on error.
        """
        try:
            history = self._ticker.history(period=self.period)
            if history.empty:
                return f"No price history data found for {self.ticker_symbol} for period {self.period}."
            return f"PRICE HISTORY OF {self.ticker_symbol} ({self.period}):\n" + history.to_string()
        except Exception as e:
            print(f"Error fetching price history for {self.ticker_symbol}: {e}")
            return None

    def get_dividends_splits(self) -> str:
        """
        Fetches dividend and split data and returns it as a formatted string.

        Returns:
            A string containing dividend and split data, or messages indicating no data is available.
        """
        output = ""
        try:
            dividends = self._ticker.dividends
            if dividends.empty:
                 output += f"No dividend data found for {self.ticker_symbol}.\n"
            else:
                output += f"DIVIDENDS OF {self.ticker_symbol}:\n" + dividends.to_string() + "\n\n"
        except Exception as e:
            print(f"Error fetching dividends for {self.ticker_symbol}: {e}")
            output += f"Error fetching dividends for {self.ticker_symbol}: {e}\n\n"

        try:
            splits = self._ticker.splits
            if splits.empty:
                 output += f"No split data found for {self.ticker_symbol}.\n"
            else:
                output += f"SPLITS OF {self.ticker_symbol}:\n" + splits.to_string() + "\n"
        except Exception as e:
            print(f"Error fetching splits for {self.ticker_symbol}: {e}")
            output += f"Error fetching splits for {self.ticker_symbol}: {e}\n"

        return output.strip() # Remove trailing newline if any

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

    def get_financials(self) -> str:
        """
        Fetches financial statements (income statement, balance sheet, cash flow) and returns them as a formatted string.

        Returns:
            A string containing financial statement data, or messages indicating no data is available for specific types.
        """
        output = ""

        financials_df = self._fetch_income_statement()
        if financials_df.empty:
            output += f"No income statement data found for {self.ticker_symbol}.\n\n"
        else:
            output += f"INCOME STATEMENT OF {self.ticker_symbol}:\n" + financials_df.to_string() + "\n\n"

        balance_sheet_df = self._fetch_balance_sheet()
        if balance_sheet_df.empty:
            output += f"No balance sheet data found for {self.ticker_symbol}.\n\n"
        else:
            output += f"BALANCE SHEET OF {self.ticker_symbol}:\n" + balance_sheet_df.to_string() + "\n\n"

        cashflow_df = self._fetch_cashflow()
        if cashflow_df.empty:
            output += f"No cash flow data found for {self.ticker_symbol}.\n"
        else:
            output += f"CASH FLOW OF {self.ticker_symbol}:\n" + cashflow_df.to_string() + "\n"

        return output.strip() # Remove trailing newline if any

    def get_company_info(self) -> str | None:
        """
        Fetches general company information and returns it as a formatted string.

        Returns:
            A string containing company information, or a message indicating no data is available, or None on error.
        """
        try:
            info = self._ticker.info
            if not info:
                return f"No company info found for {self.ticker_symbol}."

            output = f"COMPANY INFO FOR {self.ticker_symbol}:\n"
            # Format key pieces of info nicely
            output += f"  Sector: {info.get('sector', 'N/A')}\n"
            output += f"  Industry: {info.get('industry', 'N/A')}\n"
            output += f"  Market Cap: {info.get('marketCap', 'N/A')}\n"
            output += f"  Website: {info.get('website', 'N/A')}\n"
            # Add more info if desired, or just include the whole dict string
            # output += str(info) # Uncomment to include the full dictionary representation

            return output.strip()
        except Exception as e:
            print(f"Error fetching company info for {self.ticker_symbol}: {e}")
            return None

    def get_institutional_holdings(self) -> str:
        """
        Fetches major and institutional shareholder data and returns it as a formatted string.

        Returns:
            A string containing holdings data, or messages indicating no data is available.
        """
        output = ""
        try:
            major_holders = self._ticker.major_holders
            if major_holders.empty:
                 output += f"No major holders data found for {self.ticker_symbol}.\n"
            else:
                output += f"MAJOR HOLDERS OF {self.ticker_symbol}:\n" + major_holders.to_string() + "\n\n"
        except Exception as e:
            print(f"Error fetching major holders for {self.ticker_symbol}: {e}")
            output += f"Error fetching major holders for {self.ticker_symbol}: {e}\n\n"

        try:
            institutional_holders = self._ticker.institutional_holders
            if institutional_holders.empty:
                 output += f"No institutional holders data found for {self.ticker_symbol}.\n"
            else:
                output += f"INSTITUTIONAL HOLDERS OF {self.ticker_symbol}:\n" + institutional_holders.to_string() + "\n"
        except Exception as e:
            print(f"Error fetching institutional holders for {self.ticker_symbol}: {e}")
            output += f"Error fetching institutional holders for {self.ticker_symbol}: {e}\n"

        return output.strip() # Remove trailing newline if any


# Example Usage (Optional - can be removed for production code)
if __name__ == "__main__":
    ticker = "NVDA" # Example ticker
    period = "1d" # Example period

    fetcher = CompanyFinancialData(ticker, period)

    print(f"--- Fetching data for {ticker} ({period}) ---")

    price_history_str = fetcher.get_price_history()
    if price_history_str is not None:
        print("\n--- Price History ---")
        print(price_history_str)

    dividends_splits_str = fetcher.get_dividends_splits()
    print("\n--- Dividends and Splits ---")
    print(dividends_splits_str)

    financials_str = fetcher.get_financials()
    print("\n--- Financial Statements ---")
    print(financials_str)

    company_info_str = fetcher.get_company_info()
    if company_info_str is not None:
        print("\n--- Company Info ---")
        print(company_info_str)

    holdings_str = fetcher.get_institutional_holdings()
    print("\n--- Holdings Data ---")
    print(holdings_str)
    print("\n--- Data fetching complete ---")