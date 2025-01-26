// Transaction state
const state = {
    network: 'mainnet',
    txHash: null
};

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8001',
    TIMEOUT: 15000
};

// DOM Elements
const elements = {
    networkBadge: document.getElementById('network-badge'),
    networkName: document.getElementById('network-name'),
    txStatus: document.getElementById('tx-status'),
    txHash: document.getElementById('tx-hash'),
    txFrom: document.getElementById('tx-from'),
    txTo: document.getElementById('tx-to'),
    txAmount: document.getElementById('tx-amount'),
    txFee: document.getElementById('tx-fee'),
    txBlock: document.getElementById('tx-block'),
    txTimestamp: document.getElementById('tx-timestamp'),
    txNonce: document.getElementById('tx-nonce'),
    txSize: document.getElementById('tx-size'),
    txData: document.getElementById('tx-data')
};

// Utility functions
function formatTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() / 1000) - timestamp);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

function formatAddress(address) {
    if (!address) return '';
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
}

function formatAmount(amount) {
    return parseFloat(amount).toFixed(6);
}

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

async function fetchWithTimeout(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_CONFIG.BASE_URL}${endpoint}`;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    
    try {
        const response = await fetch(url, {
            ...options,
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

// Transaction functions
async function loadTransaction() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        state.txHash = urlParams.get('hash') || window.location.pathname.split('/').pop();
        state.network = urlParams.get('network') || 'mainnet';
        
        // Update network badge
        elements.networkName.textContent = state.network.charAt(0).toUpperCase() + state.network.slice(1);
        elements.networkBadge.className = `network-badge ${state.network}`;
        
        const response = await fetchWithTimeout(`/api/transaction/${state.txHash}?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch transaction');
        
        const tx = await response.json();
        
        // Update transaction status
        elements.txStatus.className = `status-indicator ${tx.status === 'success' ? 'success' : 'pending'}`;
        elements.txStatus.textContent = tx.status.charAt(0).toUpperCase() + tx.status.slice(1);
        
        // Update transaction details
        elements.txHash.textContent = tx.hash;
        elements.txFrom.textContent = tx.from;
        elements.txFrom.href = `/address/${tx.from}?network=${state.network}`;
        elements.txTo.textContent = tx.to;
        elements.txTo.href = `/address/${tx.to}?network=${state.network}`;
        elements.txAmount.textContent = `${formatAmount(tx.amount)} ROOT`;
        elements.txFee.textContent = `${formatAmount(tx.fee)} ROOT`;
        elements.txBlock.textContent = `#${tx.block_index}`;
        elements.txBlock.href = `/block/${tx.block_hash}?network=${state.network}`;
        elements.txTimestamp.textContent = `${new Date(tx.timestamp * 1000).toLocaleString()} (${formatTimeAgo(tx.timestamp)})`;
        elements.txNonce.textContent = tx.nonce;
        elements.txSize.textContent = formatSize(tx.size);
        
        // Format and display transaction data
        if (tx.data) {
            try {
                const formattedData = JSON.stringify(JSON.parse(tx.data), null, 2);
                elements.txData.textContent = formattedData;
            } catch {
                elements.txData.textContent = tx.data;
            }
        } else {
            elements.txData.textContent = 'No data';
        }
        
    } catch (error) {
        console.error('Error loading transaction:', error);
        showNotification('Failed to load transaction details', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white max-w-md animate-fade-in`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', loadTransaction); 