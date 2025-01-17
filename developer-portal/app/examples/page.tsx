'use client'

import { useState } from 'react'
import { Tab } from '@headlessui/react'
import { CodeBlock, dracula } from 'react-code-blocks'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

const examples = [
  {
    title: 'Basic Wallet Integration',
    description: 'Learn how to integrate RootChain wallet functionality into your application.',
    code: {
      javascript: `import { RootChain } from 'rootchain-sdk'

// Initialize RootChain SDK
const rootchain = new RootChain({
  apiKey: 'your_api_key',
  network: 'testnet'
})

// Create a new wallet
async function createWallet() {
  const wallet = await rootchain.createWallet()
  console.log('New wallet created:', wallet.address)
  return wallet
}

// Get wallet balance
async function getBalance(address) {
  const balance = await rootchain.getBalance(address)
  console.log('Balance:', balance.toString(), 'ROOT')
  return balance
}

// Send tokens
async function sendTokens(from, to, amount, privateKey) {
  const tx = await rootchain.transfer({
    from,
    to,
    amount,
    privateKey
  })
  console.log('Transaction hash:', tx.hash)
  return tx
}`,
      python: `from rootchain import RootChain

# Initialize RootChain SDK
rootchain = RootChain(
    api_key='your_api_key',
    network='testnet'
)

# Create a new wallet
def create_wallet():
    wallet = rootchain.create_wallet()
    print(f'New wallet created: {wallet.address}')
    return wallet

# Get wallet balance
def get_balance(address):
    balance = rootchain.get_balance(address)
    print(f'Balance: {balance} ROOT')
    return balance

# Send tokens
def send_tokens(from_addr, to_addr, amount, private_key):
    tx = rootchain.transfer(
        from_address=from_addr,
        to_address=to_addr,
        amount=amount,
        private_key=private_key
    )
    print(f'Transaction hash: {tx.hash}')
    return tx`
    }
  },
  {
    title: 'Smart Contract Deployment',
    description: 'Example of deploying and interacting with a smart contract on RootChain.',
    code: {
      javascript: `import { RootChain, TokenContract } from 'rootchain-sdk'

// Initialize RootChain SDK
const rootchain = new RootChain({
  apiKey: 'your_api_key',
  network: 'testnet'
})

// Deploy a new token contract
async function deployToken() {
  const token = await rootchain.deployContract(TokenContract, {
    name: 'MyToken',
    symbol: 'MTK',
    decimals: 18,
    totalSupply: '1000000'
  })
  
  console.log('Contract deployed at:', token.address)
  return token
}

// Interact with the token contract
async function tokenOperations(tokenAddress) {
  const token = await rootchain.getContract(tokenAddress)
  
  // Get token info
  const name = await token.name()
  const symbol = await token.symbol()
  const totalSupply = await token.totalSupply()
  
  console.log('Token:', name, symbol)
  console.log('Total supply:', totalSupply.toString())
  
  // Transfer tokens
  const tx = await token.transfer('trtc_recipient', '100')
  console.log('Transfer tx:', tx.hash)
}`,
      python: `from rootchain import RootChain, TokenContract

# Initialize RootChain SDK
rootchain = RootChain(
    api_key='your_api_key',
    network='testnet'
)

# Deploy a new token contract
def deploy_token():
    token = rootchain.deploy_contract(TokenContract, 
        name='MyToken',
        symbol='MTK',
        decimals=18,
        total_supply='1000000'
    )
    
    print(f'Contract deployed at: {token.address}')
    return token

# Interact with the token contract
def token_operations(token_address):
    token = rootchain.get_contract(token_address)
    
    # Get token info
    name = token.name()
    symbol = token.symbol()
    total_supply = token.total_supply()
    
    print(f'Token: {name} {symbol}')
    print(f'Total supply: {total_supply}')
    
    # Transfer tokens
    tx = token.transfer('trtc_recipient', '100')
    print(f'Transfer tx: {tx.hash}')`
    }
  }
]

export default function Examples() {
  const [selectedTab, setSelectedTab] = useState(0)
  const [selectedLanguage, setSelectedLanguage] = useState<'javascript' | 'python'>('javascript')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Code Examples
        </h2>
        <p className="mt-2 text-sm text-gray-500">
          Explore example code snippets and implementations using the RootChain SDK.
        </p>
      </div>

      <div className="flex justify-end">
        <div className="inline-flex rounded-md shadow-sm">
          <button
            type="button"
            onClick={() => setSelectedLanguage('javascript')}
            className={classNames(
              selectedLanguage === 'javascript'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
              'relative inline-flex items-center rounded-l-md px-3 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
            )}
          >
            JavaScript
          </button>
          <button
            type="button"
            onClick={() => setSelectedLanguage('python')}
            className={classNames(
              selectedLanguage === 'python'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
              'relative -ml-px inline-flex items-center rounded-r-md px-3 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
            )}
          >
            Python
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {examples.map((example, index) => (
          <div key={example.title} className="overflow-hidden rounded-lg bg-white shadow">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium leading-6 text-gray-900">{example.title}</h3>
              <p className="mt-2 text-sm text-gray-500">{example.description}</p>
              <div className="mt-4">
                <CodeBlock
                  text={example.code[selectedLanguage]}
                  language={selectedLanguage}
                  theme={dracula}
                  showLineNumbers={true}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 