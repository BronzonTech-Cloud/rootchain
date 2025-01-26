// Initialize Stripe
const stripe = Stripe('pk_test_51Po3etLhWzKxLkQ3o6JPLFVpwIFheR0XbSuougvBg6qo6DTEWKMrr5jKIXZMNtjlSZ3FVVKZeWWhSeR8NhvEvIEJ00pkV5mEgG');

// Initialize Stripe Elements
let elements;
let card;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Stripe Elements
    elements = stripe.elements();
    card = elements.create('card');
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element
    card.addEventListener('change', function(event) {
        const displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Update total price when amount changes
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function(e) {
            const amount = parseFloat(e.target.value) || 0;
            const totalPrice = amount * 90;
            document.getElementById('totalPrice').textContent = `Total: $${totalPrice.toFixed(2)}`;
        });
    }

    // Handle form submission
    const purchaseForm = document.getElementById('purchase-form');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitButton = purchaseForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';

            try {
                await purchaseTokens();
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Purchase Tokens';
            }
        });
    }
});

async function purchaseTokens() {
    const amount = parseFloat(document.getElementById('amount').value);
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    try {
        // Create payment intent
        const response = await fetch('/api/ico/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount,
                network: 'mainnet' // Default to mainnet
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create payment intent');
        }

        const { clientSecret } = await response.json();

        // Handle payment
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: 'ROOT Token ICO Purchase'
                }
            }
        });

        if (result.error) {
            // Show error to your customer
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                alert('Successfully purchased ROOT tokens!');
                document.getElementById('amount').value = '';
                card.clear();
                updateICOStatus();
            }
        }
    } catch (error) {
        console.error('Error:', error);
        const errorElement = document.getElementById('card-errors');
        errorElement.textContent = error.message || 'An error occurred during purchase';
    }
}

// Update ICO status
async function updateICOStatus() {
    try {
        const response = await fetch('/api/ico/status?network=mainnet');
        const data = await response.json();
        
        const availableTokens = document.getElementById('availableTokens');
        if (availableTokens) {
            availableTokens.textContent = `${data.available_tokens.toLocaleString()} ROOT`;
        }

        const statusElement = document.getElementById('ico-status');
        if (statusElement) {
            statusElement.textContent = `${data.tokens_sold.toLocaleString()} / ${data.total_tokens.toLocaleString()} ROOT tokens sold`;
        }
    } catch (error) {
        console.error('Error updating ICO status:', error);
    }
}

// Update status every 30 seconds
setInterval(updateICOStatus, 30000);
updateICOStatus(); // Initial update 