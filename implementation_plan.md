# Chrome Bookmark Cleanup CLI Tool

This tool will parse Chrome's Netscape-format HTML bookmark files, clean duplicate entries, merge bookmarks with identical URLs but different names, delete empty folders recursively, and output the result in HTML, JSON, CSV, or TSV.

## User Review Required

> [!IMPORTANT]
> **Resolution of Same-URL-Different-Names (Grouping & Positioning)**:
> When multiple bookmarks have the same URL but different names, the tool will:
> 1. Find the newest bookmark based on its `ADD_DATE` (defaulting to 0 if missing).
> 2. Determine its parent folder (the target folder).
> 3. Move all bookmarks with this URL to that target folder.
> 4. Position them consecutively at the index of the newest bookmark in the target folder, sorted by their `ADD_DATE` ascending.
>
> Please verify if this ordering and placement approach aligns with your expectations.

## Proposed Changes

### Configuration and Packaging

#### [NEW] [pyproject.toml](file:///Users/hwang/github/ChromeBookmarkCleanup/pyproject.toml)
Defines project metadata and dependencies. Configures the command-line entry point `chrome-bookmark-cleanup`.

---

### Core Module

#### [NEW] [__init__.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/__init__.py)
Package initialization.

#### [NEW] [parser.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/parser.py)
Implements:
- `BookmarkNode` representing bookmark files, folders, and bookmarks in a tree structure.
- `BookmarkParser` subclass of `html.parser.HTMLParser` to parse Netscape HTML bookmark format.
- `writer` module / function to serialize the `BookmarkNode` tree back into Chrome-compatible HTML.

#### [NEW] [cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/cleanup.py)
Implements:
- Duplicate detection (exact name + URL matches, keeping the newest one).
- Grouping/moving of bookmarks with same URL but different names to the newest one's folder.
- Recursive deletion of empty folders.

#### [NEW] [main.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/main.py)
Implements CLI parsing with `argparse`, output format routing (HTML, JSON, CSV, TSV), and file writing.

---

### Tests

#### [NEW] [conftest.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/conftest.py)
Shared pytest fixtures, including sample bookmark files.

#### [NEW] [test_parser.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_parser.py)
Unit tests for HTML bookmark parsing and generation.

#### [NEW] [test_cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cleanup.py)
Unit tests verifying duplicate removal, same-URL movement, and empty folder deletion.

#### [NEW] [test_cli.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cli.py)
Integration tests running the CLI command with various flags (`--format json`, `--format csv`, etc.) and verifying output formats.

## Verification Plan

### Automated Tests
We will install the package in editable mode and run pytest:
```bash
pip install -e .
pytest -v
```

### Manual Verification
1. Create a dummy bookmark file with duplicates, nested folders, empty folders, and same-URL/different-name items.
2. Run the CLI tool:
   ```bash
   chrome-bookmark-cleanup path/to/input.html -o path/to/output.html
   ```
3. Inspect output structures for HTML, JSON, and CSV formats.
