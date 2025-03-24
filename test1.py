import os
import sys
import json
import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
from datetime import datetime

class BarChartFuturesScraper:
    def __init__(self, log_level=logging.INFO):
        self.logger = self._setup_logger(log_level)
        self.base_url = 'https://www.barchart.com/futures/quotes/Futures'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html',
        }
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('plots', exist_ok=True)

    def _setup_logger(self, log_level):
        logger = logging.getLogger('BarChartFuturesScraper')
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        file_handler = logging.FileHandler('logs/barchart_futures.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger

    def fetch_html(self) -> Optional[str]:
        try:
            self.logger.info("Fetching HTML content")
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch HTML content: {e}")
            return None

    def parse_html(self, html_content: str) -> Optional[pd.DataFrame]:
        try:
            if not html_content:
                self.logger.error("No HTML content to parse")
                return None
            
            # Use pandas to read tables from HTML
            dfs = pd.read_html(html_content)
            if dfs:
                self.logger.info(f"Extracted {len(dfs)} tables from HTML")
                return dfs[0]
            else:
                self.logger.error("No tables found in HTML")
                return None
        except ValueError as e:
            self.logger.error(f"Failed to parse HTML: {e}")
            return None

    def save_data(self, df: pd.DataFrame):
        if df is not None and not df.empty:
            excel_path = f'data/futures_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            df.to_excel(excel_path, index=False)
            self.logger.info(f"Data saved to {excel_path}")

    def run(self):
        try:
            html_content = self.fetch_html()
            if html_content is None:
                self.logger.error("Failed to retrieve HTML content")
                return

            futures_df = self.parse_html(html_content)
            if futures_df is None or futures_df.empty:
                self.logger.error("Failed to parse futures data")
                return

            self.save_data(futures_df)
            self.logger.info("Scraping and saving completed successfully")

        except Exception as e:
            self.logger.error(f"Execution failed: {e}")


def main():
    scraper = BarChartFuturesScraper(log_level=logging.INFO)
    scraper.run()


if __name__ == "__main__":
    main()
