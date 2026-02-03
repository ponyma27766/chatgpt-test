# chatgpt-test

## Data pipeline (daily market data)

### From zero to success

```bash
python3 -m pipeline.fetch \
  --symbol aapl.us \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --output-dir data \
  --format csv
```

Expected output (path printed):

```
data/aapl.us_2024-01-01_2024-01-31.csv
```

```bash
python3 -m pipeline.validate \
  --input data/aapl.us_2024-01-01_2024-01-31.csv \
  --report-dir reports
```

Expected output (path printed):

```
reports/validate_<timestamp>.md
```

### Make targets

```bash
make data
make validate
```
