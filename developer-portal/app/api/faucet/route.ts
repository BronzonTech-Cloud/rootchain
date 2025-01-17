import { NextResponse } from 'next/server'
import { RootChain } from '../../../../blockchain/core/blockchain'
import { RootWallet } from '../../../../blockchain/wallet/wallet'

const testnet = new RootChain('testnet')
const FAUCET_PRIVATE_KEY = process.env.FAUCET_PRIVATE_KEY || ''
const FAUCET_ADDRESS = process.env.FAUCET_ADDRESS || 'trtc_faucet'

// Rate limiting
const requestLimits: { [key: string]: number[] } = {}
const RATE_LIMIT = 5 // requests per day
const DAY_MS = 24 * 60 * 60 * 1000

export async function POST(request: Request) {
  try {
    const { address, amount } = await request.json()
    
    // Validate address format
    if (!address || !address.startsWith('trtc_')) {
      return NextResponse.json(
        { error: 'Invalid testnet address' },
        { status: 400 }
      )
    }

    // Validate amount
    const numAmount = Number(amount)
    if (isNaN(numAmount) || numAmount <= 0 || numAmount > 100) {
      return NextResponse.json(
        { error: 'Invalid amount. Must be between 0 and 100 tROOT' },
        { status: 400 }
      )
    }

    // Check rate limit
    const now = Date.now()
    if (!requestLimits[address]) {
      requestLimits[address] = []
    }

    // Remove old requests
    requestLimits[address] = requestLimits[address].filter(
      time => now - time < DAY_MS
    )

    if (requestLimits[address].length >= RATE_LIMIT) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Try again in 24 hours' },
        { status: 429 }
      )
    }

    // Create transaction
    const wallet = new RootWallet('testnet')
    const tx = wallet.create_transaction(
      FAUCET_ADDRESS,
      address,
      amount,
      FAUCET_PRIVATE_KEY
    )

    // Add transaction to blockchain
    testnet.add_transaction(tx)

    // Update rate limit
    requestLimits[address].push(now)

    return NextResponse.json({
      status: 'success',
      transaction: tx
    })
  } catch (error) {
    console.error('Error processing faucet request:', error)
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    )
  }
} 