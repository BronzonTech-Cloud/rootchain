// Address state
const state = {
    network: 'mainnet',
    address: null,
    page: 1,
    txType: 'all',
    txDirection: 'all',
    charts: {
        balance: null,
        activity: null
    }
};

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8001',
    TIMEOUT: 15000,
    PAGE_SIZE: 20
};

// DOM Elements
const elements = {
    networkBadge: document.getElementById('network-badge'),
    networkName: document.getElementById('network-name'),
    address: document.getElementById('address'),
    balance: document.getElementById('balance'),
    totalSent: document.getElementById('total-sent'),
    totalReceived: document.getElementById('total-received'),
    txCount: document.getElementById('tx-count'),
    firstActivity: document.getElementById('first-activity'),
    lastActivity: document.getElementById('last-activity'),
    stakedAmount: document.getElementById('staked-amount'),
    validatorStatus: document.getElementById('validator-status'),
    delegationCount: document.getElementById('delegation-count'),
    balanceChart: document.getElementById('balance-chart'),
    activityChart: document.getElementById('activity-chart'),
    txTypeFilter: document.getElementById('tx-type-filter'),
    txDirectionFilter: document.getElementById('tx-direction-filter'),
    transactions: document.getElementById('transactions'),
    loadMore: document.getElementById('load-more')
};

// Chart Configuration
const CHART_CONFIG = {
    balance: {
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
                        label: (context) => `${formatAmount(context.raw)} ROOT`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => `${formatAmount(value)} ROOT`
                    }
                }
            }
        }
    },
    activity: {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.dataset.label}: ${context.raw}`
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    }
};

// Transaction Types
const TX_TYPES = {
    transfer: {
        label: 'Transfer',
        color: 'text-blue-600',
        icon: '↔️'
    },
    stake: {
        label: 'Stake',
        color: 'text-green-600',
        icon: '🔒'
    },
    delegate: {
        label: 'Delegate',
        color: 'text-purple-600',
        icon: '📊'
    },
    contract: {
        label: 'Contract',
        color: 'text-orange-600',
        icon: '📜'
    },
    reward: {
        label: 'Reward',
        color: 'text-yellow-600',
        icon: '🎁'
    }
};

// Event Listeners
elements.txTypeFilter?.addEventListener('change', (e) => {
    state.txType = e.target.value;
    state.page = 1;
    loadTransactions(true);
});

elements.txDirectionFilter?.addEventListener('change', (e) => {
    state.txDirection = e.target.value;
    state.page = 1;
    loadTransactions(true);
});

elements.loadMore?.addEventListener('click', () => {
    state.page++;
    loadTransactions(false);
});

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

// Chart functions
function initializeCharts(balanceHistory, activityHistory) {
    // Balance chart
    const balanceData = {
        labels: balanceHistory.map(item => new Date(item.timestamp * 1000)),
        datasets: [{
            data: balanceHistory.map(item => item.balance),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4
        }]
    };
    
    state.charts.balance = new Chart(elements.balanceChart, {
        ...CHART_CONFIG.balance,
        data: balanceData
    });
    
    // Activity chart
    const activityData = {
        labels: activityHistory.map(item => new Date(item.timestamp * 1000)),
        datasets: Object.keys(TX_TYPES).map(type => ({
            label: TX_TYPES[type].label,
            data: activityHistory.map(item => item[type] || 0),
            backgroundColor: TX_TYPES[type].color.replace('text', 'bg')
        }))
    };
    
    state.charts.activity = new Chart(elements.activityChart, {
        ...CHART_CONFIG.activity,
        data: activityData
    });
}

// Address functions
async function loadAddress() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        state.address = urlParams.get('address') || window.location.pathname.split('/').pop();
        state.network = urlParams.get('network') || 'mainnet';
        
        // Update network badge
        elements.networkName.textContent = state.network.charAt(0).toUpperCase() + state.network.slice(1);
        elements.networkBadge.className = `network-badge ${state.network}`;
        elements.address.textContent = state.address;
        
        // Fetch address details
        const response = await fetchWithTimeout(`/api/address/${state.address}?network=${state.network}`);
        if (!response.ok) throw new Error('Failed to fetch address');
        
        const data = await response.json();
        
        // Update overview
        elements.balance.textContent = `${formatAmount(data.balance)} ROOT`;
        elements.totalSent.textContent = `${formatAmount(data.total_sent)} ROOT`;
        elements.totalReceived.textContent = `${formatAmount(data.total_received)} ROOT`;
        elements.txCount.textContent = data.transaction_count.toLocaleString();
        elements.firstActivity.textContent = formatTimeAgo(data.first_activity);
        elements.lastActivity.textContent = formatTimeAgo(data.last_activity);
        elements.stakedAmount.textContent = `${formatAmount(data.staked_amount)} ROOT`;
        elements.validatorStatus.textContent = data.is_validator ? 'Active Validator' : 'Not a Validator';
        elements.delegationCount.textContent = data.delegation_count.toLocaleString();
        
        // Initialize charts
        initializeCharts(data.balance_history, data.activity_history);
        
        // Load initial transactions
        await loadTransactions(true);
        
    } catch (error) {
        console.error('Error loading address:', error);
        showNotification('Failed to load address details', 'error');
    }
}

async function loadTransactions(reset = false) {
    try {
        if (reset) {
            elements.transactions.innerHTML = '';
        }
        
        const response = await fetchWithTimeout(
            `/api/address/${state.address}/transactions?` +
            `network=${state.network}&` +
            `page=${state.page}&` +
            `limit=${API_CONFIG.PAGE_SIZE}&` +
            `type=${state.txType}&` +
            `direction=${state.txDirection}`
        );
        
        if (!response.ok) throw new Error('Failed to fetch transactions');
        
        const { transactions, has_more } = await response.json();
        
        elements.loadMore.style.display = has_more ? 'block' : 'none';
        
        const transactionHtml = transactions.map(tx => `
            <div class="transaction-item animate-fade-in">
                <div class="flex flex-col">
                    <div class="flex items-center space-x-2">
                        <span class="text-lg">${TX_TYPES[tx.type].icon}</span>
                        <a href="/transaction/${tx.hash}?network=${state.network}" 
                           class="hash-display short hover:text-blue-600">
                            ${tx.hash}
                        </a>
                        <span class="px-2 py-1 text-sm rounded-full ${TX_TYPES[tx.type].color} bg-opacity-10">
                            ${TX_TYPES[tx.type].label}
                        </span>
                    </div>
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
                        ${tx.from === state.address ? '-' : '+'}${formatAmount(tx.amount)} ROOT
                    </div>
                    <div class="text-sm text-gray-500">
                        ${formatTimeAgo(tx.timestamp)}
                    </div>
                </div>
            </div>
        `).join('');
        
        if (reset) {
            elements.transactions.innerHTML = transactionHtml;
        } else {
            elements.transactions.insertAdjacentHTML('beforeend', transactionHtml);
        }
        
    } catch (error) {
        console.error('Error loading transactions:', error);
        showNotification('Failed to load transactions', 'error');
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
document.addEventListener('DOMContentLoaded', loadAddress); 