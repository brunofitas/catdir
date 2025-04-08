# Changelog

## [1.0.0] - 2025-04-08

### Added
- Initial version of `catdir` with support for:
    - Tree creation from directory with ignore patterns
    - `.catignore` file with folder, filename, and extension support
    - Clean rendering of file contents with type detection
    - Full reconstruction from rendered text output
- Fully covered test suite with:
    - Unit tests for ignore logic and tree building
    - End-to-end tests for render + reconstruction
