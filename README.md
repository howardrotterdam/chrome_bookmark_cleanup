# Chrome Bookmark Cleanup

`chrome-bookmark-cleanup` is a command-line interface (CLI) tool written in Python to clean, organize, and format exported Google Chrome HTML bookmark files.

## Purpose

Chrome's bookmark manager can easily accumulate duplicates, empty folders, and inconsistencies (e.g., identical URLs saved under different names in separate locations) over time. This tool automatically cleans up these issues, outputting a cleaned bookmarks file and saving the removed duplicates to a separate file.

There is a Chrome browser extension [Bookmarks clean up Chrome
extension][Bookmarks clean up Chrome extension] but it's slow in speed and
takes big amount of manual operations to check and delete duplicates. Also
there is no fine control based on bookmark name or add date.

## Features

1. **Duplicate Bookmark Removal**: Removes duplicate bookmarks where the name and URL are exactly the same, keeping only the newest bookmark (determined by the `ADD_DATE` attribute).
2. **URL Merging & Grouping**: If different bookmarks share the same URL but have different names, they are moved to the folder containing the newest bookmark and stored consecutively, ordered chronologically.
3. **Empty Folder Pruning**: Recursively removes any empty folders.
4. **Flexible Output Formats**: Supports outputting results in standard Chrome HTML format (suitable for immediate re-importing), JSON lists, CSV, or TSV formats.
5. **Removed Duplicates Log**: Automatically saves the removed duplicate entries to a separate file (e.g., `bookmarks-dups.html` or `bookmarks-dups.json`) next to the output file using the same format.
6. **Execution Statistics**: Prints detailed summaries of changes (input/output counts, duplicate count, merged count, pruned folder count) directly to `sys.stderr`.
7. **Folder Restructuring & Sorting**: Restructures a specified bookmark folder (and subfolders) recursively into date-based subfolders (`yyyy/yymmdd`) based on each bookmark's `ADD_DATE`. Under the same date folder, bookmarks are sorted alphabetically. Chinese titles are sorted by case-insensitive Pinyin order.

## Installation & Build

This project requires Python 3.8 or higher.

To install the project in editable mode (including optional testing dependencies):

```bash
git clone https://github.com/howardrotterdam/chrome_bookmark_cleanup.git
cd chrome_bookmark_cleanup
pip install -e ".[test]"
```

This registers the CLI command `chrome-bookmark-cleanup`.

## Usage

```bash
chrome-bookmark-cleanup <input_file> [options]
```

### Options

- `-o`, `--output <path>`: Path to write the cleaned bookmarks. If not specified, writes to standard output.
- `-f`, `--format <html|json|csv|tsv>`: Output format (default is `html`).
- `-s`, `--sort [<folder_path_or_name>]`: Specify a folder path (e.g., `"Bookmarks bar/My Folder"`) or folder title to restructure and sort. If no folder is specified, restructures and sorts all top-level folders.
- `-h`, `--help`: Show usage and help.

### Examples

**Clean bookmarks and save to HTML (default format):**
```bash
chrome-bookmark-cleanup bookmarks.html -o cleaned.html
```
*Note: This will also create `cleaned-dups.html` next to `cleaned.html`.*

**Export cleaned bookmarks to JSON:**
```bash
chrome-bookmark-cleanup bookmarks.html -o cleaned.json -f json
```
*Note: This will also create `cleaned-dups.json` next to `cleaned.json`.*

**Clean bookmarks and write output to stdout, saving duplicates next to input:**
```bash
chrome-bookmark-cleanup bookmarks.html -f csv > cleaned.csv
```
*Note: This will output CSV content to stdout and write the duplicates to `bookmarks-dups.csv` next to `bookmarks.html`.*

**Clean, restructure, and sort bookmarks in a specific folder:**
```bash
chrome-bookmark-cleanup bookmarks.html -o cleaned.html --sort "Bookmarks bar/Folder A"
```
*Note: This will restructure all bookmarks inside "Folder A" recursively into "yyyy/yymmdd" subfolders and sort them alphabetically with Chinese text in Pinyin order.*

### Statistics Output Example

The following execution statistics are printed to `stderr` upon success:
```text
=== Chrome Bookmark Cleanup Statistics ===
Total Bookmarks Input:       452
Total Bookmarks Output:      412
Duplicate Bookmarks Removed: 40
Same-URL Bookmarks Merged:   15
Empty Folders Removed:       8
==========================================
```

## Running Tests

To run the unit and CLI integration test suite:

```bash
pytest -v
```

## References

- [Bookmarks clean up Chrome extension][Bookmarks clean up Chrome extension]

[Bookmarks clean up Chrome extension]: https://chromewebstore.google.com/detail/bookmarks-clean-up/oncbjlgldmiagjophlhobkogeladjijl
