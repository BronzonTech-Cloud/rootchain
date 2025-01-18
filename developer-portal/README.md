# RootChain Developer Portal

A modern, full-featured developer portal for the RootChain blockchain platform. Built with Next.js 14, React, and Tailwind CSS.

## Features

### 🔑 API Key Management
- Create and manage API keys for both mainnet and testnet
- Toggle key status (active/inactive)
- View key usage history and details
- Automatic key prefix based on network (root_prod_ / root_test_)

### 💧 Testnet Faucet
- Request test tokens for development (up to 100 tROOT)
- Rate limiting (5 requests per address per day)
- View recent token distributions
- Real-time transaction status updates

### 📚 Documentation
- Comprehensive API reference
- Integration guides
- Network-specific information
- Best practices and tutorials

### 💻 Code Examples
- Ready-to-use code snippets
- Multiple language support (JavaScript/Python)
- Smart contract deployment examples
- Wallet integration guides

### 🔄 Real-time Updates
- Toast notifications for actions
- Transaction status tracking
- Error handling with descriptive messages
- Loading states for better UX

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS, HeadlessUI
- **Code Highlighting**: react-code-blocks
- **State Management**: React Hooks
- **Notifications**: react-hot-toast

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn
- Git

### Installation

```bash
cd developer-portal
```

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
```
FAUCET_PRIVATE_KEY=your_faucet_private_key
FAUCET_ADDRESS=your_faucet_address
```

### Development

Run the development server:
```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) to view the portal.

## Project Structure

```
developer-portal/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── api-keys/          # API key management page
│   ├── documentation/     # Documentation page
│   ├── examples/          # Code examples page
│   ├── faucet/           # Testnet faucet page
│   └── layout.tsx        # Root layout
├── components/            # Reusable components
├── public/               # Static assets
└── styles/              # Global styles
```

## API Routes

### Create Wallet
```
POST /api/wallet/create
Body: { network: 'mainnet' | 'testnet' }
```

### Request Test Tokens
```
POST /api/faucet
Body: { address: string, amount: number }
```

### Manage API Keys
```
GET /api/keys
POST /api/keys
Body: { name: string, network: 'mainnet' | 'testnet' }
PATCH /api/keys
Body: { id: string, status: 'active' | 'inactive' }
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository .
