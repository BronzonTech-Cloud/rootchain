from blockchain.core import RootChain
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize blockchain
        chain = RootChain(network="development")
        logger.info("RootChain initialized successfully")
        
        # Create genesis block if needed
        if len(chain.chain) == 0:
            chain.create_genesis_block()
            logger.info("Genesis block created")
        
        # Log chain info
        network_info = chain.get_network_info()
        logger.info(f"Network Info: {network_info}")
        
        # Keep the blockchain running
        logger.info("Blockchain is running. Press Ctrl+C to stop.")
        while True:
            # Process pending transactions
            if chain.pending_transactions:
                chain.mine_pending_transactions("miner_address")
                logger.info("Mined new block with pending transactions")
            
    except KeyboardInterrupt:
        logger.info("Shutting down RootChain...")
    except Exception as e:
        logger.error(f"Error running blockchain: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 