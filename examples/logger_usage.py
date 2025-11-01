"""Example usage of the centralized logger."""

from src.utils.logger import logger, setup_logger


def example_basic_logging():
    """Basic logging examples."""
    logger.info("Starting process...")
    logger.info("Processing %d files", 42)
    logger.warning("Configuration file not found, using defaults")
    logger.error("Failed to connect to database: %s", "Connection timeout")


def example_with_debug():
    """Example with debug level logging."""
    # Enable debug logging
    debug_logger = setup_logger(name="debug_example", level="DEBUG")
    
    debug_logger.debug("Detailed variable state: %s", {"key": "value"})
    debug_logger.info("Operation completed")


def example_error_handling():
    """Example of logging in error handling."""
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division error occurred: %s", str(e))
        logger.debug("Stack trace details...", exc_info=True)


if __name__ == "__main__":
    print("=== Basic Logging ===")
    example_basic_logging()
    
    print("\n=== Debug Logging ===")
    example_with_debug()
    
    print("\n=== Error Handling ===")
    example_error_handling()
