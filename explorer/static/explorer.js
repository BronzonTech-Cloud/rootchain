// Explorer state
const state = {
    network: 'mainnet',
    updateInterval: null,
    isLoading: false
};

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8001',
    TIMEOUT: 15000
};

// DOM Elements
const elements = {
    networkBadges: {
        mainnet: document.getElementById('mainnet-btn'),
        testnet: document.getElementById('testnet-btn')
    },
    stats: {
        latestBlock: document.getElementById('latest-block'),
        totalTxs: document.getElementById('total-txs'),
        avgBlockTime: document.getElementById('avg-block-time'),
        networkTps: document.getElementById('network-tps'),
        // New network health metrics
        activeValidators: document.getElementById('active-validators'),
        networkDifficulty: document.getElementById('network-difficulty'),
        networkHashrate: document.getElementById('network-hashrate'),
        // New token metrics
        totalSupply: document.getElementById('total-supply'),
        circulatingSupply: document.getElementById('circulating-supply'),
        totalStaked: document.getElementById('total-staked'),
        // New transaction metrics
        pendingTxs: document.getElementById('pending-txs'),
        avgFee: document.getElementById('avg-fee'),
        volume24h: document.getElementById('volume-24h')
    },
    latestBlocks: document.getElementById('latest-blocks'),
    latestTransactions: document.getElementById('latest-transactions'),
    searchForm: document.getElementById('search-form'),
    searchInput: document.getElementById('search-input')
};

// Network switching
Object.entries(elements.networkBadges).forEach(([network, button]) => {
    button?.addEventListener('click', () => {
        Object.values(elements.networkBadges).forEach(btn => {
            btn?.classList.add('opacity-50');
        });
        button.classList.remove('opacity-50');
        state.network = network;
        updateExplorer();
    });
});

// Search functionality
elements.searchForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = elements.searchInput?.value.trim();
    if (!query) return;

    try {
        state.isLoading = true;
        
        // Try to determine query type
        let endpoint;
        if (query.startsWith('rtc_') || query.startsWith('trtc_')) {
            endpoint = `/api/address/${query}`;
        } else if (query.length === 64) {  // Assuming 32-byte hash
            // Try both block and transaction endpoints
            try {
                const blockResponse = await fetchWithTimeout(`/api/block/${query}?network=${state.network}`);
                if (blockResponse.ok) {
                    window.location.href = `/block/${query}`;
                    return;
                }
            } catch (error) {
                console.error('Block search failed:', error);
            }
            
            endpoint = `/api/transaction/${query}`;
        } else {
            throw new Error('Invalid search query');
        }
        
        const response = await fetchWithTimeout(endpoint);
        if (!response.ok) throw new Error('Not found');
        
        const data = await response.json();
        
        // Redirect based on result type
        if ('balance' in data) {
            window.location.href = `/address/${query}`;
        } else if ('transactions' in data) {
            window.location.href = `/block/${query}`;
        } else {
            window.location.href = `/transaction/${query}`;
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('No results found', 'error');
    } finally {
        state.isLoading = false;
    }
});

// Chart state
const charts = {
    hashrate: null,
    supply: null,
    transactions: null,
    blockTime: null,
    txTypes: null
};

// Chart Configuration
const CHART_CONFIG = {
    hashrate: {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${formatHashrate(context.raw)}`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => formatHashrate(value)
                    }
                }
            }
        }
    },
    supply: {
        type: 'doughnut',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.label}: ${formatAmount(context.raw)} ROOT`
                    }
                }
            }
        }
    },
    transactions: {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    },
    blockTime: {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Block Time (seconds)'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Blocks'
                    }
                }
            }
        }
    },
    txTypes: {
        type: 'pie',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    }
};

// Transaction Types
const TX_TYPES = {
    transfer: {
        label: 'Transfer',
        color: 'rgb(59, 130, 246)',
        icon: '↔️'
    },
    stake: {
        label: 'Stake',
        color: 'rgb(16, 185, 129)',
        icon: '🔒'
    },
    delegate: {
        label: 'Delegate',
        color: 'rgb(139, 92, 246)',
        icon: '📊'
    },
    contract: {
        label: 'Contract',
        color: 'rgb(249, 115, 22)',
        icon: '📜'
    },
    reward: {
        label: 'Reward',
        color: 'rgb(234, 179, 8)',
        icon: '🎁'
    }
};

// Update functions
async function updateStats() {
    try {
        const response = await fetchWithTimeout(`/api/stats?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const stats = await response.json();
        
        // Update basic stats
        elements.stats.latestBlock.textContent = stats.latest_block;
        elements.stats.totalTxs.textContent = stats.total_transactions.toLocaleString();
        elements.stats.avgBlockTime.textContent = `${stats.average_block_time.toFixed(2)}s`;
        elements.stats.networkTps.textContent = stats.tps.toFixed(2);
        
        // Update network health metrics
        elements.stats.activeValidators.textContent = stats.active_validators;
        elements.stats.networkDifficulty.textContent = formatDifficulty(stats.difficulty);
        elements.stats.networkHashrate.textContent = formatHashrate(stats.hashrate);
        
        // Update token metrics
        elements.stats.totalSupply.textContent = `${formatAmount(stats.total_supply)} ROOT`;
        elements.stats.circulatingSupply.textContent = `${formatAmount(stats.circulating_supply)} ROOT`;
        elements.stats.totalStaked.textContent = `${formatAmount(stats.total_staked)} ROOT`;
        
        // Update transaction metrics
        elements.stats.pendingTxs.textContent = stats.pending_transactions;
        elements.stats.avgFee.textContent = `${formatAmount(stats.average_fee)} ROOT`;
        elements.stats.volume24h.textContent = `${formatAmount(stats.volume_24h)} ROOT`;
        
        // Update charts
        if (charts.hashrate) {
            charts.hashrate.data.labels = stats.hashrate_history.map(item => new Date(item.timestamp * 1000));
            charts.hashrate.data.datasets[0].data = stats.hashrate_history.map(item => item.hashrate);
            charts.hashrate.update();
        }
        
        if (charts.transactions) {
            charts.transactions.data.labels = stats.tx_history.map(item => new Date(item.timestamp * 1000));
            charts.transactions.data.datasets[0].data = stats.tx_history.map(item => item.count);
            charts.transactions.update();
        }
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function updateLatestBlocks() {
    try {
        const response = await fetchWithTimeout(`/api/blocks/latest?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch blocks');
        
        const blocks = await response.json();
        
        elements.latestBlocks.innerHTML = blocks.map(block => `
            <div class="block-item animate-fade-in">
                <div class="flex flex-col">
                    <a href="/block/${block.hash}" class="font-medium hover:text-blue-600">
                        Block #${block.index}
                    </a>
                    <span class="text-sm text-gray-500">
                        ${formatTimeAgo(block.timestamp)}
                    </span>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-500">
                        ${block.transactions.length} txs
                    </div>
                    <div class="text-sm text-gray-500">
                        ${formatSize(block.size)}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating blocks:', error);
    }
}

async function updateLatestTransactions() {
    try {
        const response = await fetchWithTimeout(`/api/transactions/latest?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch transactions');
        
        const transactions = await response.json();
        
        elements.latestTransactions.innerHTML = transactions.map(tx => `
            <div class="transaction-item animate-fade-in">
                <div class="flex flex-col">
                    <a href="/transaction/${tx.hash}" class="hash-display short hover:text-blue-600">
                        ${tx.hash}
                    </a>
                    <div class="text-sm text-gray-500 mt-1">
                        From: <a href="/address/${tx.from}" class="hover:text-blue-600">${formatAddress(tx.from)}</a>
                        <br/>
                        To: <a href="/address/${tx.to}" class="hover:text-blue-600">${formatAddress(tx.to)}</a>
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
        console.error('Error updating transactions:', error);
    }
}

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

// Additional utility functions
function formatDifficulty(difficulty) {
    if (difficulty >= 1e12) return `${(difficulty / 1e12).toFixed(2)}T`;
    if (difficulty >= 1e9) return `${(difficulty / 1e9).toFixed(2)}G`;
    if (difficulty >= 1e6) return `${(difficulty / 1e6).toFixed(2)}M`;
    if (difficulty >= 1e3) return `${(difficulty / 1e3).toFixed(2)}K`;
    return difficulty.toFixed(2);
}

function formatHashrate(hashrate) {
    if (hashrate >= 1e12) return `${(hashrate / 1e12).toFixed(2)} TH/s`;
    if (hashrate >= 1e9) return `${(hashrate / 1e9).toFixed(2)} GH/s`;
    if (hashrate >= 1e6) return `${(hashrate / 1e6).toFixed(2)} MH/s`;
    if (hashrate >= 1e3) return `${(hashrate / 1e3).toFixed(2)} KH/s`;
    return `${hashrate.toFixed(2)} H/s`;
}

// Chart initialization
function initializeCharts(data) {
    // Hashrate chart
    const hashrateData = {
        labels: data.hashrate_history.map(item => new Date(item.timestamp * 1000)),
        datasets: [{
            data: data.hashrate_history.map(item => item.hashrate),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4
        }]
    };
    
    charts.hashrate = new Chart(
        document.getElementById('hashrate-chart'),
        {
            ...CHART_CONFIG.hashrate,
            data: hashrateData
        }
    );
    
    // Supply chart
    const supplyData = {
        labels: ['Circulating', 'Staked', 'Reserved'],
        datasets: [{
            data: [
                data.circulating_supply,
                data.total_staked,
                data.total_supply - data.circulating_supply - data.total_staked
            ],
            backgroundColor: [
                'rgb(59, 130, 246)',
                'rgb(16, 185, 129)',
                'rgb(107, 114, 128)'
            ]
        }]
    };
    
    charts.supply = new Chart(
        document.getElementById('supply-chart'),
        {
            ...CHART_CONFIG.supply,
            data: supplyData
        }
    );
    
    // Transaction chart
    const txData = {
        labels: data.tx_history.map(item => new Date(item.timestamp * 1000)),
        datasets: [{
            label: 'Transactions',
            data: data.tx_history.map(item => item.count),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4
        }]
    };
    
    charts.transactions = new Chart(
        document.getElementById('tx-chart'),
        {
            ...CHART_CONFIG.transactions,
            data: txData
        }
    );
    
    // Block time distribution chart
    const blockTimeData = {
        labels: data.block_time_distribution.map(item => item.time),
        datasets: [{
            data: data.block_time_distribution.map(item => item.count),
            backgroundColor: '#3B82F6'
        }]
    };
    
    charts.blockTime = new Chart(
        document.getElementById('block-time-chart'),
        {
            ...CHART_CONFIG.blockTime,
            data: blockTimeData
        }
    );
    
    // Transaction types chart
    const txTypesData = {
        labels: Object.values(TX_TYPES).map(type => type.label),
        datasets: [{
            data: data.tx_types.map(item => item.count),
            backgroundColor: Object.values(TX_TYPES).map(type => type.color)
        }]
    };
    
    charts.txTypes = new Chart(
        document.getElementById('tx-types-chart'),
        {
            ...CHART_CONFIG.txTypes,
            data: txTypesData
        }
    );
}

// Update explorer data
async function updateExplorer() {
    await Promise.all([
        updateStats(),
        updateLatestBlocks(),
        updateLatestTransactions()
    ]);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchWithTimeout(`/api/stats?network=${state.network}`)
        .then(response => response.json())
        .then(data => {
            initializeCharts(data);
            updateExplorer();
            // Update every 10 seconds
            setInterval(updateExplorer, 10000);
        })
        .catch(error => {
            console.error('Error initializing explorer:', error);
            showNotification('Failed to initialize explorer', 'error');
        });
}); 