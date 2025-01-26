// Block state
const state = {
    network: 'mainnet',
    blockHash: null
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
    blockNumber: document.getElementById('block-number'),
    blockHash: document.getElementById('block-hash'),
    blockTimestamp: document.getElementById('block-timestamp'),
    blockTxCount: document.getElementById('block-tx-count'),
    prevBlock: document.getElementById('prev-block'),
    blockSize: document.getElementById('block-size'),
    blockReward: document.getElementById('block-reward'),
    blockTransactions: document.getElementById('block-transactions')
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

// Block functions
async function loadBlock() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        state.blockHash = urlParams.get('hash') || window.location.pathname.split('/').pop();
        state.network = urlParams.get('network') || 'mainnet';
        
        // Update network badge
        elements.networkName.textContent = state.network.charAt(0).toUpperCase() + state.network.slice(1);
        elements.networkBadge.className = `network-badge ${state.network}`;
        
        const response = await fetchWithTimeout(`/api/block/${state.blockHash}?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch block');
        
        const block = await response.json();
        
        // Update block details
        elements.blockNumber.textContent = block.index;
        elements.blockHash.textContent = block.hash;
        elements.blockTimestamp.textContent = `${new Date(block.timestamp * 1000).toLocaleString()} (${formatTimeAgo(block.timestamp)})`;
        elements.blockTxCount.textContent = block.transactions.length;
        elements.prevBlock.textContent = block.previous_hash;
        elements.prevBlock.href = `/block/${block.previous_hash}?network=${state.network}`;
        elements.blockSize.textContent = formatSize(block.size);
        elements.blockReward.textContent = `${formatAmount(block.reward)} ROOT`;
        
        // Update transactions list
        elements.blockTransactions.innerHTML = block.transactions.map(tx => `
            <div class="transaction-item animate-fade-in">
                <div class="flex flex-col">
                    <a href="/transaction/${tx.hash}?network=${state.network}" 
                       class="hash-display short hover:text-blue-600">
                        ${tx.hash}
                    </a>
                    <div class="text-sm text-gray-500 mt-1">
                        From: <a href="/address/${tx.from}?network=${state.network}" 
                               class="hover:text-blue-600">
                            ${formatAddress(tx.from)}
                        </a>
                        <br/>
                        To: <a href="/address/${tx.to}?network=${state.network}" 
                              class="hover:text-blue-600">
                            ${formatAddress(tx.to)}
                        </a>
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-medium">
                        ${formatAmount(tx.amount)} ROOT
                    </div>
                    <div class="text-sm text-gray-500">
                        ${formatTimeAgo(tx.timestamp)}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading block:', error);
        showNotification('Failed to load block details', 'error');
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
document.addEventListener('DOMContentLoaded', loadBlock); 