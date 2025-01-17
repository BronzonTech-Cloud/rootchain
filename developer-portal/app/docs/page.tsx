'use client'

import { useState } from 'react'
import { Tab } from '@headlessui/react'
import { CodeBlock, dracula } from 'react-code-blocks'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const apiEndpoints = [
  {
    name: 'Create Wallet',
    method: 'POST',
    endpoint: '/api/wallet/create',
    description: 'Create a new wallet for the specified network',
    request: `{
  "network": "mainnet" | "testnet"
}`,
    response: `{
  "address": "rtc_1234567890abcdef",
  "private_key": "0x...",
  "mnemonic": "word1 word2 ...",
  "balance": "0",
  "network": "mainnet",
  "symbol": "ROOT"
}`
  },
  {
    name: 'Transfer Tokens',
    method: 'POST',
    endpoint: '/api/transfer',
    description: 'Transfer tokens between addresses on the same network',
    request: `{
  "from_address": "rtc_sender",
  "to_address": "rtc_recipient",
  "amount": "10.0",
  "private_key": "0x..."
}`,
    response: `{
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
}`
  }
]

const guides = [
  {
    title: 'Getting Started',
    content: `
# Getting Started with RootChain

Follow these steps to start building on RootChain:

1. Generate an API key from the [API Keys](/api-keys) page
2. Request test tokens from the [Faucet](/faucet)
3. Create your first wallet using the API
4. Make your first transaction

## Installation

\`\`\`bash
# Install via npm
npm install rootchain-sdk

# Or via yarn
yarn add rootchain-sdk
\`\`\`

## Quick Start

\`\`\`javascript
import { RootChain } from 'rootchain-sdk'

// Initialize the SDK
const rootchain = new RootChain({
  apiKey: 'your_api_key',
  network: 'testnet' // or 'mainnet'
})

// Create a new wallet
const wallet = await rootchain.createWallet()
console.log(wallet.address)

// Send tokens
const tx = await rootchain.transfer({
  from: wallet.address,
  to: 'trtc_recipient',
  amount: '10.0',
  privateKey: wallet.privateKey
})
console.log(tx.hash)
\`\`\`
`
  },
  {
    title: 'Smart Contracts',
    content: `
# Smart Contracts on RootChain

RootChain supports ERC-20 compatible smart contracts. Here's how to deploy and interact with them:

## Deploying a Token Contract

\`\`\`javascript
import { RootChain, TokenContract } from 'rootchain-sdk'

const rootchain = new RootChain({
  apiKey: 'your_api_key',
  network: 'testnet'
})

// Deploy a new token contract
const token = await rootchain.deployContract(TokenContract, {
  name: 'MyToken',
  symbol: 'MTK',
  decimals: 18,
  totalSupply: '1000000'
})

console.log('Contract deployed at:', token.address)
\`\`\`

## Interacting with Contracts

\`\`\`javascript
// Transfer tokens
await token.transfer('trtc_recipient', '100')

// Check balance
const balance = await token.balanceOf('trtc_address')
console.log('Balance:', balance.toString())
\`\`\`
`
  }
]

export default function Documentation() {
  const [selectedTab, setSelectedTab] = useState(0)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Documentation
        </h2>
        <p className="mt-2 text-sm text-gray-500">
          Comprehensive guides and API reference for building on RootChain.
        </p>
      </div>

      <div className="w-full">
        <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
          <Tab.List className="flex space-x-1 rounded-xl bg-purple-900/20 p-1">
            <Tab
              className={({ selected }) =>
                classNames(
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                  'ring-white ring-opacity-60 ring-offset-2 ring-offset-purple-400 focus:outline-none focus:ring-2',
                  selected
                    ? 'bg-white text-purple-700 shadow'
                    : 'text-gray-600 hover:bg-white/[0.12] hover:text-purple-600'
                )
              }
            >
              API Reference
            </Tab>
            <Tab
              className={({ selected }) =>
                classNames(
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                  'ring-white ring-opacity-60 ring-offset-2 ring-offset-purple-400 focus:outline-none focus:ring-2',
                  selected
                    ? 'bg-white text-purple-700 shadow'
                    : 'text-gray-600 hover:bg-white/[0.12] hover:text-purple-600'
                )
              }
            >
              Guides
            </Tab>
          </Tab.List>
          <Tab.Panels className="mt-4">
            <Tab.Panel>
              <div className="space-y-4">
                {apiEndpoints.map((endpoint) => (
                  <div key={endpoint.name} className="overflow-hidden rounded-lg bg-white shadow">
                    <div className="px-4 py-5 sm:p-6">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium leading-6 text-gray-900">{endpoint.name}</h3>
                        <span className="inline-flex items-center rounded-md bg-purple-100 px-2.5 py-0.5 text-sm font-medium text-purple-800">
                          {endpoint.method}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-gray-500">{endpoint.description}</p>
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900">Endpoint</h4>
                        <div className="mt-1 font-mono text-sm text-gray-600">{endpoint.endpoint}</div>
                      </div>
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900">Request</h4>
                        <div className="mt-1">
                          <CodeBlock
                            text={endpoint.request}
                            language="json"
                            theme={dracula}
                            showLineNumbers={false}
                          />
                        </div>
                      </div>
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900">Response</h4>
                        <div className="mt-1">
                          <CodeBlock
                            text={endpoint.response}
                            language="json"
                            theme={dracula}
                            showLineNumbers={false}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Tab.Panel>
            <Tab.Panel>
              <div className="space-y-4">
                {guides.map((guide) => (
                  <div key={guide.title} className="overflow-hidden rounded-lg bg-white shadow">
                    <div className="px-4 py-5 sm:p-6">
                      <div className="prose max-w-none">
                        <h2 className="text-lg font-medium leading-6 text-gray-900">{guide.title}</h2>
                        <div className="mt-4">
                          <CodeBlock
                            text={guide.content}
                            language="markdown"
                            theme={dracula}
                            showLineNumbers={false}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  )
} 