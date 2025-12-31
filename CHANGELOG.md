## [3.0.0] – 2025-05-06

### Breaking Changes
- Renamed all `.rawTransaction` properties to `.raw_transaction` (Web3.py v7 naming).
- Completely refactored middleware for Web3.py v7: now a class-based middleware using `wrap_make_request`.
- Overhauled `FlashbotProvider`:
  - Replaced internal Web3 HTTP utils with `requests.post`.
  - Switched to EIP-191 signing via `eth_account.messages.encode_defunct`.
  - Removed deprecated imports from `eth_account._utils`.

### Added
- Official compatibility with Web3.py v7 (7.x series).
- Expanded tests covering `_parse_signed_tx` for legacy, EIP-2930 (type=1), and EIP-1559 (type=2) transactions.
- Configurable `request_timeout` parameter for `FlashbotProvider` (default: 10 seconds).
- Custom exception hierarchy: `FlashbotsError`, `InvalidTransactionError`, `TransactionSignatureError`, `BlockExtrapolationError`, `FlashbotsRequestError`.
- Explicit `__all__` exports in package `__init__.py`.

### Fixed
- Ensured numeric RLP fields (bytes) are converted to `int`.
- Added recovery of `chainId` for legacy transactions signed under EIP-155.
- Updated examples (`examples/simple.py`) to use `.raw_transaction` and new middleware/provider APIs.

### Changed
- Replaced `assert` statements with explicit validation raising domain-specific exceptions.
- Replaced lambda functions with list comprehensions for better readability.
- Improved error handling in `FlashbotProvider` with specific exception types for timeouts and connection errors.
- Added return type hints to `simulate()` and `extrapolate_timestamp()` methods.
- Migrated from Poetry to uv for package management (PEP 621 compliant `pyproject.toml`).

