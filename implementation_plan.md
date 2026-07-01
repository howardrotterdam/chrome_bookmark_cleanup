# Implementation Plan - Folder Sorting with Pinyin Order

We will add a CLI option `--sort <folder_path_or_name>` to restructure and sort a specific folder's bookmarks.

## User Review Required

> [!IMPORTANT]
> **External Dependency**:
> We will add `pypinyin` to our package dependencies. This is the industry-standard library in Python for converting Chinese text to Pinyin to enable accurate sorting.
>
> **Folder RESTructure ('yyyy/yymmdd')**:
> For the target folder:
> 1. All bookmarks inside the target folder (including subfolders) will be extracted.
> 2. They will be regrouped into nested folders `yyyy` (e.g. `2026`) and `yymmdd` (e.g. `260701`) based on their `ADD_DATE` (UTC).
> 3. Old empty subfolders under the target folder will be pruned.
> 4. In each `yymmdd` folder, bookmarks will be sorted alphabetically. Chinese titles will be sorted by Pinyin using case-insensitive comparison.

## Proposed Changes

### Configuration and Packaging

#### [MODIFY] [pyproject.toml](file:///Users/hwang/github/ChromeBookmarkCleanup/pyproject.toml)
Add `pypinyin` to package dependencies:
```toml
dependencies = [
    "pypinyin>=0.40.0",
]
```

---

### Core Module

#### [MODIFY] [cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/cleanup.py)
Add:
- `find_folder(node, target_path)`: Find a folder by name or path.
- `collect_bookmarks_recursive(node)`: Extract all bookmark nodes under a given folder recursively.
- `sort_and_restructure_folder(root, target_path)`:
  - Find the folder.
  - Gather and extract all bookmarks.
  - Create the new `yyyy/yymmdd` structure.
  - Sort bookmarks alphabetically (supporting Pinyin for Chinese text).
  - Sort the year and date folders chronologically.

#### [MODIFY] [main.py](file:///Users/hwang/github/ChromeBookmarkCleanup/chrome_bookmark_cleanup/main.py)
- Add `--sort` option to `argparse`.
- Invoke the sorting/restructuring function before running the cleanup pipeline.

---

### Tests

#### [MODIFY] [test_cleanup.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cleanup.py)
Add tests to verify:
- Sorting by Pinyin of mixed English/Chinese text.
- Restructuring folders under `--sort`.

#### [MODIFY] [test_cli.py](file:///Users/hwang/github/ChromeBookmarkCleanup/tests/test_cli.py)
Add a test running the CLI with `--sort` on a sample bookmarks file and verifying the output structure.

## Verification Plan

### Automated Tests
Run:
```bash
pytest -v
```

### Manual Verification
Create a bookmark file with a folder containing mixed English/Chinese bookmarks with different dates, sort it using `chrome-bookmark-cleanup --sort "Folder A"`, and verify that the HTML output has the correct `yyyy/yymmdd` folder nesting and correct sorting.
