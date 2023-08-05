# dmstockapi

- API documentation: https://dmstockapi/docs/api
- API version: 1.0.0
- Package version: 1.0.0

## Installation

Install package

```sh
pip install dmstockapi
```

## Getting Started

```python
import dmstockapi

# Setup client
client = dmstockapi.Client(api_key="API KEY")

# Stock candles
res = client.stock_candles('000001.SZ',_from='2021-01-01')
print(res)

# Convert to Pandas Dataframe
import pandas as pd

print(pd.DataFrame(res))


```

## License

Apache License
