-----"""User interface layer for the accounting application.

This module implements the presentation layer, handling user interaction
through a menu-driven command-line interface.
"""

import logging

from constants import MENU_TEXT, MENU_OPTIONS
from exceptions import InvalidAmountError
from operations import AccountOperations
from validators import validate_menu_choice


logger = logging.getLogger(__name__)


class AccountUI:
    """Command-line user interface for the accounting system.
    
    This class implements the presentation layer, displaying menus and
    routing user choices to the operations layer. It follows the Single
    Responsibility Principle by focusing solely on user interaction.
    
    Attributes:
        _operations: The operations layer for handling business logic
    """
    
    def __init__(self, operations: AccountOperations) -> None:
        """Initialize the UI with an operations handler.
        
        Args:
            operations: The operations layer instance
        """
        self._operations = operations
    
    def _display_menu(self) -> None:
        """Display the main menu to the user."""
        print(MENU_TEXT)
    
    def _get_user_choice(self) -> int:
        """Get and validate user's menu choice.
        
        Returns:
            A validated menu choice (1-4), or 0 if input is invalid
        """
        try:
            choice_str = input("Enter your choice: ")
            return validate_menu_choice(choice_str)
        except InvalidAmountError as e:
            print(f"Invalid choice: {e}")
            logger.warning(f"Invalid menu choice: {e}")
            return 0  # Return 0 to continue the loop
    
    def run(self) -> None:
        """Run the main application loop.
        
        Displays the menu, gets user input, and routes to appropriate
        operations until the user chooses to exit.
        """
        logger.info("Application started")
        
        while True:
            try:
                self._display_menu()
                choice = self._get_user_choice()
                
                # Skip invalid choices
                if choice == 0:
                    continue
                
                # Handle exit
                if choice == 4:
                    print("\nThank you for using the Accounting System. Goodbye!")
                    logger.info("Application exited normally")
                    break
                
                # Route to operations
                _, operation = MENU_OPTIONS[choice]
                if operation:
                    self._operations.handle_operation(operation)
                    
            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user.")
                logger.info("Application interrupted by user (Ctrl+C)")
                break
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                print("Please try again.")
