# RootChain Wallet API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All API endpoints require an API key passed in the `X-API-Key` header:
```
X-API-Key: your_api_key
```

## Rate Limiting
- 100 requests per minute per IP address
- Status code 429 returned when limit exceeded

## Endpoints

### Create Wallet
```http
POST /wallet/create
```

**Request Body:**
```json
{
    "network": "mainnet" | "testnet"
}
```

**Response:**
```json
{
    "address": "rtc_1234567890abcdef",
    "private_key": "0x...",
    "mnemonic": "word1 word2 ...",
    "balance": "0",
    "network": "mainnet",
    "symbol": "ROOT"
}
```

### Recover Wallet
```http
POST /wallet/recover
```

**Request Body:**
```json
{
    "network": "mainnet" | "testnet",
    "mnemonic": "24-word mnemonic phrase"
}
```

**Response:** Same as Create Wallet

### Get Wallet Details
```http
GET /wallet/{address}
```

**Response:**
```json
{
    "address": "rtc_1234567890abcdef",
    "balance": "100.0",
    "network": "mainnet",
    "symbol": "ROOT",
    "transactions": [
        {
            "sender": "rtc_sender",
            "recipient": "rtc_recipient",
            "amount": "10.0",
            "timestamp": 1234567890,
            "block_number": 1234
        }
    ]
}
```

### Transfer Tokens
```http
POST /transfer
```

**Request Body:**
```json
{
    "from_address": "rtc_sender",
    "to_address": "rtc_recipient",
    "amount": "10.0",
    "private_key": "0x..."
}
```

**Response:**
```json
{
    "status": "success",
    "transaction": {
        "hash": "0x...",
        "sender": "rtc_sender",
        "recipient": "rtc_recipient",
        "amount": "10.0"
    },
    "network": "mainnet",
    "gas_used": "21000",
    "fee": "0.00021"
}
```

### Create Payment Intent
```http
POST /payment/create-intent
```

**Request Body:**
```json
{
    "amount": "90.0",
    "network": "mainnet"
}
```

**Response:**
```json
{
    "clientSecret": "pi_..."
}
```

## Error Responses

All errors follow this format:
```json
{
    "detail": "Error message"
}
```

Common status codes:
- 400: Bad Request (invalid input)
- 403: Invalid API key
- 429: Rate limit exceeded
- 500: Server error

## Network-Specific Information

### Mainnet
- Address prefix: "rtc_"
- Token symbol: "ROOT"
- Treasury address: "rtc_treasury"

### Testnet
- Address prefix: "trtc_"
- Token symbol: "tROOT"
- Treasury address: "trtc_treasury"

## Monitoring

### Prometheus Metrics
Available at `:8001/metrics`:
- `wallet_request_count`: Request count by endpoint
- `wallet_request_latency_seconds`: Request latency by endpoint

### Logging
- Structured JSON logs in `logs/wallet.log`
- Log rotation: 10MB per file, 5 backup files 