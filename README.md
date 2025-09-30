# MT5 Trade Connector

A Python-based automated trading connector for MetaTrader 5 (MT5) platform with trailing stop functionality and risk management features.

## Features

- **Automated Trading**: Execute market orders (buy/sell/close) programmatically
- **Trailing Stop**: Automatic trailing stop loss adjustment based on price movements
- **Risk Management**: Built-in daily and monthly loss limit controls
- **Position Management**: Prevent multiple positions per strategy and auto-close opposite positions
- **Multi-Timeframe Support**: Works with M1, M5, M15, M30, H1, H4, and D1 timeframes
- **Thread-Safe**: Uses threading for concurrent operations

## Requirements

- Python 3.6+
- MetaTrader 5 terminal installed
- MT5 trading account

## Installation

1. Clone this repository:
```bash
git clone https://github.com/abdlhannan/MT5_Trade_Connector.git
cd MT5_Trade_Connector
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Trading Example

```python
from MT5_Connector import MT5_TRADECONNECTOR

# Initialize the connector
connector = MT5_TRADECONNECTOR(
    login=12345678,
    password="your_password",
    strategy_name="MyStrategy",
    TimeFrame="M15",
    maxposition=3,
    PATH="",  # Path to MT5 terminal (optional)
    TrailingStopOn=True
)

# Execute a long position
connector.marketorder_trade_execution(
    PAIR="EURUSD",
    lot_size=0.1,
    TP=50,  # Take profit in pips
    SL=30,  # Stop loss in pips
    POSITION='LONG'
)

# Execute a short position
connector.marketorder_trade_execution(
    PAIR="GBPUSD",
    lot_size=0.1,
    TP=50,
    SL=30,
    POSITION='SHORT'
)

# Close a position
connector.marketorder_trade_execution(
    PAIR="EURUSD",
    lot_size=0.1,
    TP=0,
    SL=0,
    POSITION='CLOSE'
)
```

### Risk Management Example

```python
from MT5_Connector import RiskManagement_v1

# Initialize risk management
risk_mgmt = RiskManagement_v1(
    login=12345678,
    password="your_password",
    PATH="",
    daily_limit=0.05,    # 5% daily loss limit
    monthly_limit=0.10   # 10% monthly loss limit
)

# Check daily loss limits
risk_mgmt.daily_losslimit_check()
```

### Data Retrieval Example

```python
from utils import MT5_DATAGENERATOR_v2

# Get historical data
df = MT5_DATAGENERATOR_v2(
    pair="EURUSD",
    time_frame="H1",
    win=100  # Number of bars
)

print(df.head())
```

## Key Components

### MT5_TRADECONNECTOR

Main trading class that handles order execution and position management.

**Parameters:**
- `login`: MT5 account login ID
- `password`: MT5 account password
- `strategy_name`: Name of your trading strategy (max 3 words)
- `TimeFrame`: Timeframe ('M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1')
- `maxposition`: Maximum number of positions allowed per strategy
- `PATH`: Path to MT5 terminal (optional)
- `TrailingStopOn`: Enable trailing stop functionality (default: False)

**Key Methods:**
- `marketorder_trade_execution()`: Execute market orders
- `avoid_multiple_positions()`: Control position limits
- `change_stoploss()`: Update trailing stop loss

### RiskManagement_v1

Risk management class with loss limit controls.

**Parameters:**
- `login`: MT5 account login ID
- `password`: MT5 account password
- `PATH`: Path to MT5 terminal
- `daily_limit`: Daily loss limit as percentage (default: 0.05)
- `monthly_limit`: Monthly loss limit as percentage (default: 0.10)

### MT5_DATAGENERATOR_v2

Utility function to retrieve historical price data from MT5.

**Parameters:**
- `pair`: Trading pair symbol (e.g., 'EURUSD')
- `time_frame`: Timeframe string
- `win`: Number of bars to retrieve

**Returns:** pandas DataFrame with OHLCV data

## Supported Timeframes

- M1: 1 minute
- M5: 5 minutes
- M15: 15 minutes
- M30: 30 minutes
- H1: 1 hour
- H4: 4 hours
- D1: 1 day

## Important Notes

- **Strategy Name**: Should be maximum 3 words
- **Trailing Stop**: When enabled, the connector automatically adjusts stop loss based on favorable price movements
- **Position Management**: The system prevents opening more than `maxposition` positions per strategy and automatically closes opposite positions
- **Thread Safety**: Trailing stop functionality runs in separate threads

## Error Handling

The connector includes comprehensive error handling:
- Connection failures are logged with error codes
- Failed orders display detailed error information
- Invalid parameters raise appropriate exceptions

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

**Trading financial instruments carries risk. This software is provided for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred while using this software.**

## Support

For issues and questions, please open an issue on GitHub.

## Author

[Your Name/Username]
