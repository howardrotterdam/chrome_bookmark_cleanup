import argparse
import csv
import io
import json
import os
import sys

from chrome_bookmark_cleanup.parser import parse_bookmarks_html, serialize_to_html, BookmarkNode
from chrome_bookmark_cleanup.cleanup import cleanup_bookmarks, get_add_date, get_url, sort_and_restructure_folder, sort_all_folders

def flatten_bookmarks(node, current_path=None):
    """Recursively flattens a BookmarkNode tree into a list of bookmark dictionaries."""
    if current_path is None:
        current_path = []
    
    bookmarks = []
    if node.is_folder:
        for child in node.children:
            if child.is_folder:
                bookmarks.extend(flatten_bookmarks(child, current_path + [child.title]))
            else:
                folder_str = "/".join(current_path)
                bookmarks.append({
                    "folder": folder_str,
                    "name": child.title,
                    "url": get_url(child),
                    "add_date": get_add_date(child)
                })
    return bookmarks


def serialize_to_csv(bookmarks, delimiter=','):
    """Serializes a flat list of bookmarks into CSV/TSV format."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter, lineterminator='\n')
    writer.writerow(['folder', 'name', 'url', 'add_date'])
    for b in bookmarks:
        writer.writerow([
            b['folder'],
            b['name'],
            b['url'],
            b['add_date']
        ])
    return output.getvalue()


def serialize_to_json(bookmarks):
    """Serializes a flat list of bookmarks into JSON format."""
    return json.dumps(bookmarks, indent=2, ensure_ascii=False) + '\n'


def serialize_duplicates(removed_duplicates, output_format):
    """Serializes the removed duplicates list according to the specified output format."""
    if output_format == "html":
        root = BookmarkNode(is_folder=True, title="Root")
        dups_folder = BookmarkNode(is_folder=True, title="Removed Duplicates")
        dups_folder.children = [b for b, path in removed_duplicates]
        root.children = [dups_folder]
        return serialize_to_html(root)
    else:
        flat_dups = []
        for b, path in removed_duplicates:
            folder_str = "/".join(path)
            flat_dups.append({
                "folder": folder_str,
                "name": b.title,
                "url": get_url(b),
                "add_date": get_add_date(b)
            })
        if output_format == "json":
            return serialize_to_json(flat_dups)
        elif output_format == "csv":
            return serialize_to_csv(flat_dups, delimiter=',')
        elif output_format == "tsv":
            return serialize_to_csv(flat_dups, delimiter='\t')
    return ""


def get_dups_output_path(output_path, input_path, output_format):
    """Determines the duplicates output file path based on suffix rules."""
    if output_path:
        base, ext = os.path.splitext(output_path)
        return f"{base}-dups{ext}"
    else:
        base, _ = os.path.splitext(input_path)
        ext = f".{output_format}"
        return f"{base}-dups{ext}"


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Clean up Chrome bookmark export HTML files by removing duplicates and empty folders."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input Chrome bookmarks export HTML file."
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file. If not specified, writes to standard output."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["html", "json", "csv", "tsv"],
        default="html",
        help="Output format (default: html)."
    )
    parser.add_argument(
        "-s", "--sort",
        nargs="?",
        const=True,
        help="Specify a bookmark folder name or path to restructure and sort. If no folder is specified, sorts all folders."
    )

    parsed_args = parser.parse_args(args)

    if not os.path.exists(parsed_args.input_file):
        print(f"Error: Input file '{parsed_args.input_file}' does not exist.", file=sys.stderr)
        return 1

    try:
        with open(parsed_args.input_file, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return 1

    try:
        root = parse_bookmarks_html(html_content)
    except Exception as e:
        print(f"Error parsing bookmarks: {e}", file=sys.stderr)
        return 1

    if parsed_args.sort:
        try:
            if parsed_args.sort is True:
                sort_all_folders(root)
            else:
                sort_and_restructure_folder(root, parsed_args.sort)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Execute cleanup pipeline
    root, removed_duplicates, stats = cleanup_bookmarks(root)

    # Format main output
    if parsed_args.format == "html":
        output_content = serialize_to_html(root)
    else:
        flat_bookmarks = flatten_bookmarks(root)
        if parsed_args.format == "json":
            output_content = serialize_to_json(flat_bookmarks)
        elif parsed_args.format == "csv":
            output_content = serialize_to_csv(flat_bookmarks, delimiter=',')
        elif parsed_args.format == "tsv":
            output_content = serialize_to_csv(flat_bookmarks, delimiter='\t')
        else:
            print(f"Error: Unknown format '{parsed_args.format}'", file=sys.stderr)
            return 1

    # Format and serialize duplicates output
    dups_content = serialize_duplicates(removed_duplicates, parsed_args.format)
    dups_path = get_dups_output_path(parsed_args.output, parsed_args.input_file, parsed_args.format)

    # Write main output
    if parsed_args.output:
        try:
            with open(parsed_args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(output_content)

    # Write duplicates output
    try:
        with open(dups_path, 'w', encoding='utf-8') as f:
            f.write(dups_content)
    except Exception as e:
        print(f"Error writing duplicates file: {e}", file=sys.stderr)
        return 1

    # Log statistics to stderr
    sys.stderr.write("=== Chrome Bookmark Cleanup Statistics ===\n")
    sys.stderr.write(f"Total Bookmarks Input:       {stats['input_bookmarks']}\n")
    sys.stderr.write(f"Total Bookmarks Output:      {stats['output_bookmarks']}\n")
    sys.stderr.write(f"Duplicate Bookmarks Removed: {stats['duplicates_removed']}\n")
    sys.stderr.write(f"Same-URL Bookmarks Merged:   {stats['same_url_merged']}\n")
    sys.stderr.write(f"Empty Folders Removed:       {stats['empty_folders_removed']}\n")
    sys.stderr.write("==========================================\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
