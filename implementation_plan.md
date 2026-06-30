# Implementation Plan - Chrome Bookmark Cleanup Updates

We will enhance the `chrome-bookmark-cleanup` CLI tool to support saving removed duplicates and printing execution statistics.

## User Review Required

> [!IMPORTANT]
> **Duplicates File Suffix and Formatting**:
> - The removed duplicates will be written to a file with the same format as the main output, named with suffix `-dups` inserted before the file extension.
> - Example: If output path is `/path/to/cleaned.json`, the duplicates file will be `/path/to/cleaned-dups.json`.
> - If `--output` is not specified (output is written to stdout), the duplicates will be saved to a file named `<input_filename_base>-dups.<format>` in the current directory.
>
> **Statistics Logging**:
> - Statistics will be logged to `sys.stderr` in a human-readable format.
> - This keeps `stdout` clean for pipelining/redirecting outputs.

## Proposed Changes

### Core Module

#### [MODIFY] [cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/cleanup.py)
Update to:
- Return a list of removed duplicate nodes along with their original folder paths.
- Calculate and return statistics including:
  - Input bookmark count
  - Output bookmark count
  - Duplicate bookmarks removed
  - Same-URL bookmarks merged (moved)
  - Empty folders removed

#### [MODIFY] [main.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/main.py)
Update to:
- Accept output formatting for the removed duplicates list.
- Determine the duplicates file path (by appending `-dups`).
- Save the duplicates in the same format.
- Output statistics to `sys.stderr`.

---

### Tests

#### [MODIFY] [test_cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cleanup.py)
Add assertions checking the statistics return values and the list of returned duplicates.

#### [MODIFY] [test_cli.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cli.py)
Update integration tests to verify the generation of the `-dups` files and check stderr statistics output.

---

### Documentation

#### [MODIFY] [README.md](file:///Users/hwang/github/ChromeBookmarkCleanup/README.md)
Update the README to thoroughly detail:
- Purpose and features of the tool.
- Installation and build instructions.
- CLI usage, options, and output examples.
- Running unit and integration tests.

## Verification Plan

### Automated Tests
Run pytest:
```bash
pytest -v
```

### Manual Verification
1. Run CLI tool on a test file.
2. Confirm the `-dups` file is generated next to the output file (or created in the CWD if stdout is used).
3. Confirm that statistics are printed to `stderr`.
