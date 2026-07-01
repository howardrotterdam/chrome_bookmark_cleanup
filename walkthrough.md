# Walkthrough - Chrome Bookmark Cleanup Updates

We have successfully updated the `chrome-bookmark-cleanup` tool so that when a folder name is specified, the sorting and restructuring is applied to **all** folders matching that name in the bookmarks tree, along with all of their subfolders recursively.

## Changes Made

1. **Core Module (`cleanup.py`)**:
   - Implemented `find_all_folders` which recursively retrieves all folders matching a target title or path.
   - Updated `sort_and_restructure_folder` to sort and restructure every matching folder.

2. **Testing Suite**:
   - Added unit test `test_sort_multiple_matching_folders` in `tests/test_cleanup.py`.

## Verification Results

### Automated Tests
Ran `pytest -v` resulting in 19 passing test cases:
```bash
$ pytest -v
============================= test session starts ==============================
collected 19 items

tests/test_cleanup.py::test_remove_duplicates PASSED                     [  5%]
tests/test_cleanup.py::test_merge_same_urls PASSED                       [ 10%]
tests/test_cleanup.py::test_remove_empty_folders PASSED                  [ 15%]
tests/test_cleanup.py::test_full_cleanup_pipeline PASSED                 [ 21%]
tests/test_cleanup.py::test_sort_small_folder_in_place PASSED            [ 26%]
tests/test_cleanup.py::test_sort_large_folder_restructured PASSED        [ 31%]
tests/test_cleanup.py::test_sort_subfolders_recursively PASSED           [ 36%]
tests/test_cleanup.py::test_merge_duplicate_folders PASSED               [ 42%]
tests/test_cleanup.py::test_sort_multiple_matching_folders PASSED        [ 47%]
tests/test_cli.py::test_cli_html_output PASSED                           [ 52%]
tests/test_cli.py::test_cli_json_output PASSED                           [ 57%]
tests/test_cli.py::test_cli_csv_output PASSED                            [ 63%]
tests/test_cli.py::test_cli_tsv_output PASSED                            [ 68%]
tests/test_cli.py::test_cli_output_file PASSED                           [ 73%]
tests/test_cli.py::test_cli_invalid_input PASSED                         [ 78%]
tests/test_cli.py::test_cli_sort_option PASSED                           [ 84%]
tests/test_cli.py::test_cli_sort_all_folders PASSED                      [ 89%]
tests/test_parser.py::test_parse_simple_structure PASSED                 [ 94%]
tests/test_parser.py::test_serialization PASSED                          [100%]

======================== 19 passed, 2 warnings in 0.15s ========================
```
Targeting and sorting all folders matching a specified name and their subfolders recursively works perfectly!
