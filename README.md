# RootChain

RootChain is a next-generation blockchain platform with its native cryptocurrency ROOT. It features a secure wallet system, blockchain explorer, ICO platform, and a comprehensive developer portal.

## Features

- Native ROOT token with initial supply of 1,000,000 tokens
- Secure wallet system with 24-word mnemonic phrases
- Comprehensive blockchain explorer
- ICO platform with Stripe integration
- Smart contract support
- Decentralized architecture
- Multi-network support (Mainnet and Testnet)
- Advanced monitoring and metrics
- High-performance caching system
- Rate limiting and API security
- Modern developer portal with API management
- Interactive testnet faucet
- Code examples and documentation

## Project Structure

```
rootchain/
├── blockchain/           # Core blockchain implementation
│   ├── core/            # Core blockchain components
│   ├── wallet/          # Wallet implementation
│   └── contracts/       # Smart contract system
├── wallet-frontend/     # Wallet web interface
├── wallet-backend/      # Wallet API server
│   ├── tests/          # Unit and integration tests
│   ├── logs/           # Application logs
│   └── API.md          # API documentation
├── explorer/            # Blockchain explorer
├── landing-page/        # Landing page with ICO system
└── developer-portal/    # Developer portal and documentation
    ├── app/            # Next.js application
    └── docs/           # API documentation and guides
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- Stripe account for payment processing
- Redis (optional, for enhanced caching)
- Prometheus (optional, for metrics collection)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bronzontech-Cloud/rootchain.git
cd rootchain
```

2. Install Python dependencies:
```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependency Versions
Key package versions used in this project:
```
fastapi==0.68.1
uvicorn==0.15.0
python-dotenv==0.19.0
stripe==2.60.0
pydantic==1.8.2
prometheus-client==0.11.0
sentry-sdk[fastapi]==1.3.1
pytest==6.2.5
pytest-asyncio==0.15.1
httpx==0.19.0
python-multipart==0.0.5
requests==2.26.0
python-jose[cryptography]==3.3.0
redis==3.5.3
locust==2.2.1
```

### Troubleshooting Installation

If you encounter dependency conflicts:

1. Use a fresh virtual environment:
```bash
python -m venv fresh_venv
source fresh_venv/bin/activate  # On Windows use: fresh_venv\Scripts\activate
pip install --upgrade pip
```

2. Install dependencies in order:
```bash
# Core dependencies first
pip install fastapi==0.68.1 uvicorn==0.15.0 pydantic==1.8.2

# Then install the rest
pip install -r requirements.txt
```

3. If conflicts persist, you can force specific versions:
```bash
pip install --no-deps -r requirements.txt
pip install httpx==0.19.0 requests==2.26.0 --no-deps
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following:
```
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
API_KEY=your_api_key
SENTRY_DSN=your_sentry_dsn
ENVIRONMENT=development
CACHE_TYPE=redis  # or memory
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Running the Services

1. Start the blockchain node:
```bash
python blockchain/core/blockchain.py
```

2. Start the wallet service:
```bash
cd wallet-backend
python app.py
```

3. Start the explorer:
```bash
cd explorer
python app.py
```

4. Start the landing page and ICO platform:
```bash
cd landing-page
python app.py
```

5. Start the developer portal:
```bash
cd developer-portal
npm run dev
```

The services will be available at:
- Wallet: http://localhost:8000
- Explorer: http://localhost:8001
- Landing Page & ICO: http://localhost:8002
- Developer Portal: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs
- Metrics: http://localhost:8001/metrics

## Wallet Features

- Create new wallets with 24-word mnemonic phrases
- Recover existing wallets
- Send and receive ROOT tokens
- View transaction history
- Purchase ROOT tokens with credit card
- Support for both mainnet and testnet
- Real-time balance updates
- Transaction fee estimation
- Gas price optimization
- Cross-network transfer prevention

## Smart Contracts

RootChain supports various types of smart contracts:
- Token contracts (ERC-20 compatible)
- ICO contracts
- Custom contracts through the smart contract system

## Security

- Secure wallet generation with BIP39 mnemonic phrases
- Cryptographic transaction signing
- Decentralized consensus mechanism
- Secure smart contract execution
- API key authentication
- Rate limiting protection
- Input validation and sanitization
- Network-specific address validation

## Monitoring & Performance

- Prometheus metrics integration
- Request latency tracking
- Error tracking with Sentry
- Structured JSON logging
- Log rotation and management
- Cache performance metrics
- Network health monitoring
- Gas price tracking

## Testing

The wallet backend includes comprehensive testing:
```bash
# Run unit tests
pytest tests/test_wallet.py

# Run edge case tests
pytest tests/test_edge_cases.py

# Run load tests
locust -f tests/locustfile.py --host=http://localhost:8000
```
## Developer Portal

The RootChain Developer Portal provides a comprehensive suite of tools and resources for developers:

### Features
- **API Key Management**: Create and manage API keys for both mainnet and testnet
- **Testnet Faucet**: Request test tokens for development (up to 100 tROOT)
- **Documentation**: Comprehensive API reference and integration guides
- **Code Examples**: Ready-to-use code snippets in multiple languages
- **Real-time Updates**: Toast notifications and transaction status tracking

### Tech Stack
- Next.js 14
- React with TypeScript
- Tailwind CSS
- HeadlessUI components
- Real-time notifications

### Prerequisites
- Node.js 18.x or later
- npm or yarn

For detailed information about the developer portal, see the [developer portal README](developer-portal/README.md). 

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Charles Bronzon - bronzontech@pm.me
Project Link: https://github.com/Bronzontech-Cloud/rootchain 