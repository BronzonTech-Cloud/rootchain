import { NextResponse } from 'next/server'
import { RootWallet } from '../../../../../blockchain/wallet/wallet'

export async function POST(request: Request) {
  try {
    const { network } = await request.json()
    
    if (!network || !['mainnet', 'testnet'].includes(network)) {
      return NextResponse.json(
        { error: 'Invalid network. Must be either mainnet or testnet' },
        { status: 400 }
      )
    }

    const wallet = new RootWallet(network)
    const walletInfo = wallet.create_wallet()

    return NextResponse.json({
      ...walletInfo,
      network,
      symbol: network === 'mainnet' ? 'ROOT' : 'tROOT'
    })
  } catch (error) {
    console.error('Error creating wallet:', error)
    return NextResponse.json(
      { error: 'Failed to create wallet' },
      { status: 500 }
    )
  }
} 