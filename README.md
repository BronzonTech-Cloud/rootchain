# RootChain

RootChain is a next-generation blockchain platform with its native cryptocurrency ROOT. It features a secure wallet system, blockchain explorer, and ICO platform.

## Features

- Native ROOT token with initial supply of 1,000,000 tokens
- Secure wallet system with 24-word mnemonic phrases
- Comprehensive blockchain explorer
- ICO platform with Stripe integration
- Smart contract support
- Decentralized architecture

## Project Structure

```
rootchain/
├── blockchain/           # Core blockchain implementation
│   ├── core/            # Core blockchain components
│   ├── wallet/          # Wallet implementation
│   └── contracts/       # Smart contract system
├── wallet-frontend/     # Wallet web interface
├── wallet-backend/      # Wallet API server
├── explorer/            # Blockchain explorer
└── landing-page/        # Landing page with ICO system
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- Stripe account for payment processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rootchain.git
cd rootchain
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following:
```
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
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

The services will be available at:
- Wallet: http://localhost:8000
- Explorer: http://localhost:8001
- Landing Page & ICO: http://localhost:8002

## Wallet Features

- Create new wallets with 24-word mnemonic phrases
- Recover existing wallets
- Send and receive ROOT tokens
- View transaction history
- Purchase ROOT tokens with credit card

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/rootchain 