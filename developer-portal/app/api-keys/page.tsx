'use client'

import { useState, useEffect } from 'react'
import { Dialog } from '@headlessui/react'
import toast from 'react-hot-toast'

interface APIKey {
  id: string
  name: string
  key: string
  network: 'mainnet' | 'testnet'
  created: string
  lastUsed: string
  status: 'active' | 'inactive'
}

export default function APIKeys() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [selectedNetwork, setSelectedNetwork] = useState<'mainnet' | 'testnet'>('testnet')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchApiKeys()
  }, [])

  const fetchApiKeys = async () => {
    try {
      const response = await fetch('/api/keys')
      if (!response.ok) throw new Error('Failed to fetch API keys')
      const data = await response.json()
      setApiKeys(data)
    } catch (error) {
      toast.error('Failed to load API keys')
    }
  }

  const createNewKey = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newKeyName,
          network: selectedNetwork,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to create API key')
      }

      const newKey = await response.json()
      setApiKeys([...apiKeys, newKey])
      setIsOpen(false)
      setNewKeyName('')
      toast.success('API key created successfully')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create API key')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleKeyStatus = async (id: string, newStatus: 'active' | 'inactive') => {
    try {
      const response = await fetch('/api/keys', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id,
          status: newStatus,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to update API key')
      }

      const updatedKey = await response.json()
      setApiKeys(apiKeys.map(key => key.id === id ? updatedKey : key))
      toast.success('API key status updated')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to update API key')
    }
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold leading-6 text-gray-900">API Keys</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your API keys for accessing RootChain services. Create separate keys for mainnet and testnet.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            className="block rounded-md bg-purple-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-purple-500"
          >
            Generate New Key
          </button>
        </div>
      </div>

      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                      Name
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      API Key
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Network
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Last Used
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {apiKeys.map((key) => (
                    <tr key={key.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                        {key.name}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{key.key}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                          key.network === 'mainnet' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'
                        }`}>
                          {key.network}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{key.created}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{key.lastUsed}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                          key.status === 'active' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                          {key.status}
                        </span>
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <button
                          onClick={() => toggleKeyStatus(key.id, key.status === 'active' ? 'inactive' : 'active')}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          {key.status === 'active' ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <Dialog open={isOpen} onClose={() => setIsOpen(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="mx-auto max-w-sm rounded-lg bg-white p-6">
            <Dialog.Title className="text-lg font-medium leading-6 text-gray-900">Generate New API Key</Dialog.Title>
            <div className="mt-4">
              <label htmlFor="key-name" className="block text-sm font-medium text-gray-700">
                Key Name
              </label>
              <input
                type="text"
                id="key-name"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="e.g. Development Key"
              />
            </div>
            <div className="mt-4">
              <label htmlFor="network" className="block text-sm font-medium text-gray-700">
                Network
              </label>
              <select
                id="network"
                value={selectedNetwork}
                onChange={(e) => setSelectedNetwork(e.target.value as 'mainnet' | 'testnet')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
              >
                <option value="testnet">Testnet</option>
                <option value="mainnet">Mainnet</option>
              </select>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={createNewKey}
                disabled={isLoading || !newKeyName}
                className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  )
} 