// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    TIMEOUT: 15000,
    HEADERS: {
        'Content-Type': 'application/json',
        'X-API-Key': 'YJMiJqoKKSpVvzAilQ9AIB5z0UYge1YmQqqDEU1a_KM'  // Default development API key
    }
};

// Wallet state management
class WalletState {
    constructor() {
        this.wallet = null;
        this.network = 'mainnet';
        this.isLoading = false;
        this.updateInterval = null;
        this.isConnected = false;
    }

    async checkConnection() {
        try {
            const response = await fetchWithTimeout(`${API_CONFIG.BASE_URL}/health`);
            this.isConnected = response.ok;
            if (!this.isConnected) {
                showNotification('Cannot connect to wallet backend. Please ensure it is running.', 'error');
            }
            return this.isConnected;
        } catch (error) {
            this.isConnected = false;
            showNotification('Wallet backend is not accessible. Please ensure it is running on port 8000.', 'error');
            return false;
        }
    }

    setWallet(wallet) {
        this.wallet = wallet;
        this.startAutoUpdate();
    }

    setNetwork(network) {
        this.network = network;
        this.updateUI();
    }

    startAutoUpdate() {
        if (this.updateInterval) clearInterval(this.updateInterval);
        this.updateInterval = setInterval(() => this.updateWalletInfo(), 30000);
    }

    clearWallet() {
        this.wallet = null;
        if (this.updateInterval) clearInterval(this.updateInterval);
        this.updateUI();
    }
}

const state = new WalletState();

// DOM Elements
const elements = {
    networkBadges: {
        mainnet: document.getElementById('mainnet-btn'),
        testnet: document.getElementById('testnet-btn')
    },
    createWallet: document.getElementById('create-wallet'),
    recoverWallet: document.getElementById('recover-wallet'),
    sendForm: document.getElementById('send-form'),
    walletInfo: document.getElementById('wallet-info'),
    noWallet: document.getElementById('no-wallet'),
    walletAddress: document.getElementById('wallet-address'),
    walletBalance: document.getElementById('wallet-balance'),
    tokenSymbol: document.getElementById('token-symbol'),
    privateKey: document.getElementById('private-key'),
    mnemonic: document.getElementById('wallet-mnemonic'),
    loadingSpinner: document.getElementById('loading-spinner'),
    transactionList: document.getElementById('transaction-list')
};

// Network switching
Object.entries(elements.networkBadges).forEach(([network, button]) => {
    button?.addEventListener('click', () => {
        Object.values(elements.networkBadges).forEach(btn => {
            btn?.classList.add('opacity-50');
        });
        button.classList.remove('opacity-50');
        state.network = network;
        console.log('Network switched to:', network);
    });
});

// Wallet creation
elements.createWallet?.addEventListener('click', async () => {
    try {
        showLoading(true);
        const response = await fetchWithTimeout('/api/wallet/create', {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify({ network: state.network })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create wallet');
        }
        
        const wallet = await response.json();
        state.setWallet(wallet);
        showWalletSection(true);
        showNotification(`Wallet created successfully on ${state.network}! Please save your recovery phrase.`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to create wallet', 'error');
    } finally {
        showLoading(false);
    }
});

// Wallet recovery
elements.recoverWallet?.addEventListener('click', async () => {
    const mnemonicInput = document.querySelector('textarea#mnemonic');
    const mnemonic = mnemonicInput?.value.trim();
    
    if (!mnemonic) {
        showNotification('Please enter your recovery phrase', 'error');
        return;
    }

    try {
        showLoading(true);
        const response = await fetchWithTimeout('/api/wallet/recover', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                network: state.network,
                mnemonic: mnemonic
            })
        });
        
        if (!response.ok) throw new Error(await response.text());
        
        const wallet = await response.json();
        state.setWallet(wallet);
        showWalletSection(false);
        showNotification('Wallet recovered successfully!', 'success');
        mnemonicInput.value = '';
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to recover wallet', 'error');
    } finally {
        showLoading(false);
    }
});

// Send tokens
elements.sendForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const toAddress = document.getElementById('to-address')?.value;
    const amount = document.getElementById('amount')?.value;
    
    if (!toAddress || !amount || !state.wallet) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    try {
        showLoading(true);
        const response = await fetchWithTimeout('/api/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                from_address: state.wallet.address,
                to_address: toAddress,
                amount: parseFloat(amount),
                private_key: state.wallet.private_key,
                network: state.network
            })
        });
        
        if (!response.ok) throw new Error(await response.text());
        
        const result = await response.json();
        showNotification('Transaction sent successfully!', 'success');
        await state.updateWalletInfo();
        
        // Clear form
        document.getElementById('to-address').value = '';
        document.getElementById('amount').value = '';
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to send tokens', 'error');
    } finally {
        showLoading(false);
    }
});

// Helper functions
async function updateWalletInfo() {
    if (!state.wallet) return;
    
    try {
        const response = await fetchWithTimeout(`/api/wallet/${state.wallet.address}?network=${state.network}`);
        if (!response.ok) throw new Error(await response.text());
        
        const info = await response.json();
        elements.walletBalance.textContent = formatBalance(info.balance);
        elements.tokenSymbol.textContent = info.symbol;
        
        updateTransactionHistory(info.transactions);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to update wallet info', 'error');
    }
}

function showWalletSection(showPrivate = false) {
    elements.noWallet?.classList.add('hidden');
    elements.walletInfo?.classList.remove('hidden');
    
    if (elements.walletAddress) elements.walletAddress.textContent = state.wallet.address;
    if (elements.walletBalance) elements.walletBalance.textContent = formatBalance(state.wallet.balance);
    if (elements.tokenSymbol) elements.tokenSymbol.textContent = state.wallet.symbol;
    
    const privateKeySection = document.getElementById('private-key-section');
    if (showPrivate && privateKeySection) {
        privateKeySection.classList.remove('hidden');
        if (elements.privateKey) elements.privateKey.textContent = state.wallet.private_key;
        if (elements.mnemonic) elements.mnemonic.textContent = state.wallet.mnemonic;
        
        // Log wallet info for debugging
        console.log('Wallet Info:', {
            address: state.wallet.address,
            privateKey: state.wallet.private_key,
            mnemonic: state.wallet.mnemonic
        });
    }
}

function updateTransactionHistory(transactions) {
    if (!elements.transactionList) return;
    
    elements.transactionList.innerHTML = transactions.map(tx => `
        <div class="transaction-item ${tx.type === 'send' ? 'transaction-sent' : 'transaction-received'} p-4 rounded-lg">
            <div class="flex justify-between items-center">
                <div class="flex items-center">
                    <span class="text-lg mr-2">${tx.type === 'send' ? '↑' : '↓'}</span>
                    <div>
                        <span class="font-medium">${tx.type === 'send' ? 'Sent' : 'Received'}</span>
                        <span class="ml-2 text-gray-500">${formatBalance(tx.amount)} ${state.wallet.symbol}</span>
                    </div>
                </div>
                <div class="text-sm text-gray-500">
                    ${formatDate(tx.timestamp)}
                </div>
            </div>
            <div class="mt-2 text-sm text-gray-500 address-text">
                ${tx.type === 'send' ? 'To: ' : 'From: '}${formatAddress(tx.type === 'send' ? tx.recipient : tx.sender)}
            </div>
        </div>
    `).join('');
}

function showLoading(show) {
    state.isLoading = show;
    if (elements.loadingSpinner) {
        elements.loadingSpinner.classList.toggle('hidden', !show);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white max-w-md`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Utility functions
function formatBalance(balance) {
    return parseFloat(balance).toFixed(6);
}

function formatAddress(address) {
    if (!address) return '';
    return `${address.slice(0, 8)}...${address.slice(-8)}`;
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

async function fetchWithTimeout(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_CONFIG.BASE_URL}${endpoint}`;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...API_CONFIG.HEADERS,
                ...options.headers
            },
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error('Request timed out');
        }
        throw error;
    }
}

// Initialize Stripe
const stripe = Stripe('pk_test_51Po3etLhWzKxLkQ3o6JPLFVpwIFheR0XbSuougvBg6qo6DTEWKMrr5jKIXZMNtjlSZ3FVVKZeWWhSeR8NhvEvIEJ00pkV5mEgG');  // Replace with your Stripe publishable key
let stripeElements;

// ICO Purchase
const icoForm = document.getElementById('ico-form');
const purchaseAmount = document.getElementById('purchase-amount');
const tokenAmount = document.getElementById('token-amount');
const recipientAddress = document.getElementById('recipient-address');

// Update token amount when purchase amount changes
purchaseAmount?.addEventListener('input', (e) => {
    const usdAmount = parseFloat(e.target.value) || 0;
    const tokens = (usdAmount / 90).toFixed(6);  // $90 per token
    if (tokenAmount) tokenAmount.textContent = tokens;
});

// Auto-fill recipient address if wallet is connected
function updateRecipientAddress() {
    if (state.wallet && recipientAddress) {
        recipientAddress.value = state.wallet.address;
    }
}

// Handle ICO purchase
icoForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = parseFloat(purchaseAmount?.value || '0');
    const address = recipientAddress?.value?.trim();
    
    if (amount < 90) {
        showNotification('Minimum purchase amount is $90', 'error');
        return;
    }
    
    if (!address) {
        showNotification('Please enter a recipient wallet address', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        // Create payment intent
        const response = await fetchWithTimeout('/api/payment/create-intent', {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify({
                amount: amount,
                network: state.network,
                wallet_address: address
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create payment');
        }
        
        const { clientSecret, token_amount } = await response.json();
        
        // Show Stripe payment element
        const paymentElement = document.getElementById('payment-element');
        if (!paymentElement) return;
        
        paymentElement.classList.remove('hidden');
        
        if (!stripeElements) {
            stripeElements = stripe.elements({
                clientSecret,
                appearance: {
                    theme: 'stripe',
                    variables: {
                        colorPrimary: '#3B82F6',
                    },
                },
            });
        }
        
        const payment = stripeElements.create('payment');
        
        // Handle payment submission
        const result = await stripe.confirmPayment({
            elements: stripeElements,
            confirmParams: {
                return_url: window.location.origin,
            },
        });
        
        if (result.error) {
            throw new Error(result.error.message);
        }
        
        showNotification(`Successfully purchased ${token_amount} ROOT tokens! They will be sent to your wallet shortly.`, 'success');
        
        // Clear form
        purchaseAmount.value = '';
        updateWalletInfo();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to process payment', 'error');
    } finally {
        showLoading(false);
    }
});

// Update recipient address when wallet is connected
elements.createWallet?.addEventListener('click', () => {
    setTimeout(updateRecipientAddress, 1000);  // Wait for wallet creation
});

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    updateNetworkUI(state.network);
    await state.checkConnection();
    updateRecipientAddress();
}); 