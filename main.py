"""Main entry point for the accounting application.

This module serves as the application entry point, configuring logging,
wiring dependencies, and starting the application.
"""

import logging
import sys

from data import AccountData
from operations import AccountOperations
from ui import AccountUI


def configure_logging() -> None:
    """Configure application logging.
    
    Sets up logging with INFO level and a readable format for
    development and troubleshooting.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_app() -> AccountUI:
    """Factory function to create and wire the application components.
    
    This function implements dependency injection, creating all necessary
    components and wiring them together. This centralizes dependency
    configuration and makes the application easy to test.
    
    Returns:
        A fully configured AccountUI instance ready to run
    """
    # Create data layer
    data_store = AccountData()
    
    # Create business logic layer with injected data store
    operations = AccountOperations(data_store)
    
    # Create UI layer with injected operations
    ui = AccountUI(operations)
    
    return ui


def main() -> None:
    """Main application entry point.
    
    Configures the application, creates all components, and runs the
    main loop with comprehensive error handling.
    """
    configure_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing Accounting System")
        app = create_app()
        app.run()
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        logger.info("Application terminated by user")
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\nA critical error occurred: {e}")
        print("Please check the logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
