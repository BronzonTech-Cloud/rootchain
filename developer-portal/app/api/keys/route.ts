import { NextResponse } from 'next/server'
import crypto from 'crypto'

// In a real implementation, this would be stored in a database
const apiKeys: {
  [key: string]: {
    id: string
    name: string
    key: string
    network: 'mainnet' | 'testnet'
    created: string
    lastUsed: string
    status: 'active' | 'inactive'
  }
} = {}

function generateApiKey(network: string): string {
  const prefix = network === 'mainnet' ? 'root_prod_' : 'root_test_'
  const randomBytes = crypto.randomBytes(16).toString('hex')
  return `${prefix}${randomBytes}`
}

export async function GET() {
  try {
    return NextResponse.json(Object.values(apiKeys))
  } catch (error) {
    console.error('Error fetching API keys:', error)
    return NextResponse.json(
      { error: 'Failed to fetch API keys' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { name, network } = await request.json()
    
    if (!name || typeof name !== 'string') {
      return NextResponse.json(
        { error: 'Name is required' },
        { status: 400 }
      )
    }

    if (!network || !['mainnet', 'testnet'].includes(network)) {
      return NextResponse.json(
        { error: 'Invalid network. Must be either mainnet or testnet' },
        { status: 400 }
      )
    }

    const id = crypto.randomUUID()
    const key = generateApiKey(network)
    const now = new Date().toISOString()

    const apiKey = {
      id,
      name,
      key,
      network: network as 'mainnet' | 'testnet',
      created: now,
      lastUsed: '-',
      status: 'active' as const
    }

    apiKeys[id] = apiKey

    return NextResponse.json(apiKey)
  } catch (error) {
    console.error('Error creating API key:', error)
    return NextResponse.json(
      { error: 'Failed to create API key' },
      { status: 500 }
    )
  }
}

export async function PATCH(request: Request) {
  try {
    const { id, status } = await request.json()
    
    if (!id || !apiKeys[id]) {
      return NextResponse.json(
        { error: 'Invalid API key ID' },
        { status: 400 }
      )
    }

    if (!['active', 'inactive'].includes(status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be either active or inactive' },
        { status: 400 }
      )
    }

    apiKeys[id].status = status as 'active' | 'inactive'

    return NextResponse.json(apiKeys[id])
  } catch (error) {
    console.error('Error updating API key:', error)
    return NextResponse.json(
      { error: 'Failed to update API key' },
      { status: 500 }
    )
  }
} 