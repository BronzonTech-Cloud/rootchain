'use client'

import { useState } from 'react'
import toast from 'react-hot-toast'

interface Transaction {
  hash: string
  sender: string
  recipient: string
  amount: string
  timestamp: number
}

export default function Faucet() {
  const [address, setAddress] = useState('')
  const [amount, setAmount] = useState('10')
  const [isLoading, setIsLoading] = useState(false)
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])

  const requestTokens = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('/api/faucet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address,
          amount: Number(amount),
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to request tokens')
      }

      const data = await response.json()
      setRecentTransactions([data.transaction, ...recentTransactions].slice(0, 5))
      toast.success(`Successfully sent ${amount} tROOT to ${address}`)
      setAddress('')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to send tokens')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Testnet Faucet
        </h2>
        <p className="mt-2 text-sm text-gray-500">
          Request test tokens for development and testing on the RootChain testnet.
        </p>
      </div>

      <div className="overflow-hidden rounded-lg bg-white shadow">
        <div className="px-4 py-5 sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-base font-semibold leading-6 text-gray-900">Request Tokens</h3>
              <p className="mt-1 text-sm text-gray-500">
                You can request up to 100 tROOT tokens per day for your testnet address.
              </p>
              <div className="mt-6 space-y-4">
                <div className="rounded-md bg-blue-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3 flex-1 md:flex md:justify-between">
                      <p className="text-sm text-blue-700">Testnet addresses start with trtc_</p>
                    </div>
                  </div>
                </div>
                <div className="rounded-md bg-yellow-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-700">
                        These tokens have no real value and are for testing only.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-5 md:col-span-2 md:mt-0">
              <form onSubmit={requestTokens}>
                <div className="grid grid-cols-6 gap-6">
                  <div className="col-span-6">
                    <label htmlFor="address" className="block text-sm font-medium leading-6 text-gray-900">
                      Testnet Address
                    </label>
                    <input
                      type="text"
                      name="address"
                      id="address"
                      value={address}
                      onChange={(e) => setAddress(e.target.value)}
                      placeholder="trtc_..."
                      className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                    />
                  </div>

                  <div className="col-span-6 sm:col-span-3">
                    <label htmlFor="amount" className="block text-sm font-medium leading-6 text-gray-900">
                      Amount (tROOT)
                    </label>
                    <select
                      id="amount"
                      name="amount"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                    >
                      <option value="10">10 tROOT</option>
                      <option value="50">50 tROOT</option>
                      <option value="100">100 tROOT</option>
                    </select>
                  </div>
                </div>
                <div className="mt-6 flex items-center justify-end gap-x-6">
                  <button
                    type="submit"
                    disabled={isLoading || !address}
                    className="rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Sending...' : 'Request Tokens'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-lg bg-white shadow">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-base font-semibold leading-6 text-gray-900">Recent Distributions</h3>
          <div className="mt-6">
            {recentTransactions.length > 0 ? (
              <div className="flow-root">
                <ul role="list" className="-mb-8">
                  {recentTransactions.map((transaction, idx) => (
                    <li key={transaction.hash}>
                      <div className="relative pb-8">
                        {idx !== recentTransactions.length - 1 ? (
                          <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                        ) : null}
                        <div className="relative flex space-x-3">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center ring-8 ring-white">
                              <svg className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
                              </svg>
                            </span>
                          </div>
                          <div className="flex min-w-0 flex-1 justify-between space-x-4">
                            <div>
                              <p className="text-sm text-gray-500">
                                Sent <span className="font-medium text-gray-900">{transaction.amount} tROOT</span> to{' '}
                                <span className="font-medium text-gray-900">{transaction.recipient}</span>
                              </p>
                            </div>
                            <div className="whitespace-nowrap text-right text-sm text-gray-500">
                              <time dateTime={new Date(transaction.timestamp * 1000).toISOString()}>
                                {new Date(transaction.timestamp * 1000).toLocaleString()}
                              </time>
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="text-center text-sm text-gray-500">
                No recent token distributions
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 