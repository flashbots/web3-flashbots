"""Custom exceptions for the Flashbots library."""


class FlashbotsError(Exception):
    """Base exception for all Flashbots errors."""

    pass


class FlashbotsTransactionError(FlashbotsError):
    """Error related to transaction processing."""

    pass


class InvalidTransactionError(FlashbotsTransactionError):
    """Raised when a transaction is invalid or malformed."""

    pass


class TransactionSignatureError(FlashbotsTransactionError):
    """Raised when transaction signature verification fails."""

    pass


class BlockExtrapolationError(FlashbotsError):
    """Raised when block timestamp extrapolation fails."""

    pass


class FlashbotsProviderError(FlashbotsError):
    """Error related to the Flashbots provider."""

    pass


class FlashbotsRequestError(FlashbotsProviderError):
    """Raised when a request to Flashbots relay fails."""

    pass
