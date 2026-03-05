import requests
from binance.client import Client
from fpdf import FPDF
import datetime
import os
from tqdm import tqdm

# Coins to exclude from the PDF report
EXCLUDED_COINS = {
    'USDC', 'USDT', 'BUSD', 'TUSD' , 'WBTC'  # Add any other coins you want to exclude
}

# Haram coins list (text will be marked in red)
HARAM_COINS = {
    'BNB', 'SHIB', 'BCH', 'PEPE', 'UNI', 'ONDO', 'AAVE', 'RENDER', 'ENA',
    'POL', 'S', 'JUP', 'BNSOL', 'MKR', 'BONK', 'IMX', 'NEXO', 'INJ', 'CRV',
    'DEXE', 'RAY', 'LDO', 'SAND', 'KAIA', 'FLOKI', 'CAKE', 'MOVE',
    'MANA', 'JTO', 'WIF', 'PENDLE', 'OM', 'VIRTUAL', 'DYDX', 'KAVA',
    'LAYER', 'RUNE', 'STRK', 'PENGU', 'NEO', 'AXS', 'BERA', 'COMP', 'LUNC',
    'SUN', 'TURBO', 'JST', 'ZRO', 'GNO', 'SUPER', '1INCH', 'SNX', 'EIGEN'
}


def format_market_cap(market_cap):
    """Format market cap to human-readable format (1M, 1B, 1T)"""
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap/1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap/1_000_000:.2f}M"
    elif market_cap >= 1_000:
        return f"${market_cap/1_000:.2f}K"
    else:
        return f"${market_cap:.2f}"

def get_binance_client():
    api_key = os.getenv('BINANCE_API_KEY', '') 
    api_secret = os.getenv('BINANCE_API_SECRET', '') 
    return Client(api_key, api_secret)

def get_binance_coins(client):
    print("\nFetching Binance trading pairs...")
    exchange_info = client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
    print(f"Found {len(symbols)} trading pairs")
    return symbols

def get_market_caps():
    print("\nFetching market cap data from CoinGecko...")
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1,
        'sparkline': 'false'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        market_caps = {}
        for coin in tqdm(data, desc="Processing coins", unit="coin"):
            symbol = coin['symbol'].upper()
            market_caps[symbol] = {
                'name': coin['name'],
                'market_cap': coin['market_cap'],
                'price': coin['current_price']
            }
        return market_caps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market cap data: {e}")
        return {}

def create_pdf_report(coins_data, filename="binance_coins_market_cap.pdf"):
    print(f"\nGenerating PDF report with {len(coins_data)} coins...")
    pdf = FPDF()
    pdf.add_page()
    
    # Calculate total table width and center position
    table_width = 200  # Sum of all column widths
    left_margin = (pdf.w - table_width) / 2
    
    
    # Table header (centered)
    pdf.set_x(left_margin)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(15, 10, "#", border=1, align='C')
    pdf.cell(60, 10, "Coin Name", border=1, align='C')
    pdf.cell(30, 10, "Symbol", border=1, align='C')
    pdf.cell(50, 10, "Market Cap", border=1, align='C')
    pdf.cell(45, 10, "Price (USD)", border=1, align='C')
    pdf.ln()
    
    # Table rows with text coloring (centered)
    pdf.set_font("Arial", size=10)
    row_number = 1
    for symbol, data in coins_data.items():
        base_symbol = symbol[:-4] if symbol.endswith('USDT') else symbol
        
        # Skip excluded coins
        if base_symbol in EXCLUDED_COINS:
            continue
            
        is_haram = base_symbol in HARAM_COINS
        
        # Set text color and position
        pdf.set_x(left_margin)
        pdf.set_text_color(255, 0, 0) if is_haram else pdf.set_text_color(0, 128, 0)
        
        pdf.cell(15, 10, str(row_number), border=1, align='C')
        pdf.cell(60, 10, data['name'], border=1)
        pdf.cell(30, 10, symbol, border=1, align='C')
        pdf.cell(50, 10, format_market_cap(data['market_cap']), border=1, align='R')
        pdf.cell(45, 10, f"${data['price']:,.4f}", border=1, align='R')
        pdf.ln()
        
        # Reset text color to black for next row
        pdf.set_text_color(0, 0, 0)
        row_number += 1
        
        if row_number % 25 == 0 and row_number < len(coins_data):
            pdf.add_page()
            pdf.set_x(left_margin)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(15, 10, "#", border=1, align='C')
            pdf.cell(60, 10, "Coin Name", border=1, align='C')
            pdf.cell(30, 10, "Symbol", border=1, align='C')
            pdf.cell(50, 10, "Market Cap", border=1, align='C')
            pdf.cell(45, 10, "Price (USD)", border=1, align='C')
            pdf.ln()
            pdf.set_font("Arial", size=10)
    
    pdf.output(filename)
    print(f"PDF report generated: {filename}")

def main():
    print("=== Binance Coin Market Cap Report Generator ===")
    
    client = get_binance_client()
    binance_symbols = get_binance_coins(client)
    market_caps = get_market_caps()
    
    # Filter and sort data
    binance_coins_data = {}
    for symbol in binance_symbols:
        base_symbol = symbol[:-4] if symbol.endswith('USDT') else symbol
        if base_symbol in market_caps and base_symbol not in EXCLUDED_COINS:
            binance_coins_data[symbol] = market_caps[base_symbol]
    
    sorted_coins = sorted(binance_coins_data.items(), 
                         key=lambda x: x[1]['market_cap'], 
                         reverse=True)
    binance_coins_data = dict(sorted_coins)
    
    create_pdf_report(binance_coins_data)
    print("Process completed successfully!")

if __name__ == "__main__":
    main()