import argparse
import csv
import io
import json
import os
import sys

from chrome_bookmark_cleanup.parser import parse_bookmarks_html, serialize_to_html
from chrome_bookmark_cleanup.cleanup import cleanup_bookmarks, get_add_date, get_url

# Helper to flatten the bookmarks list (redefined here for convenience if needed,
# or we can define it in cleanup.py and import it).
# Let's import it from cleanup.py, but since it wasn't defined there yet, let's write it in cleanup.py
# or define it here. Defining it in cleanup.py is cleaner, but let's double check.
# Actually, let's look at cleanup.py: it doesn't have flatten_bookmarks yet. Let's define it here
# or append/modify cleanup.py. Let's define it here to keep things simple, or in cleanup.py.
# Actually, let's write it here, or modify cleanup.py to include it.
# Defining it in main.py is perfectly fine since it's formatting-related.
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

    # Execute cleanup pipeline
    cleanup_bookmarks(root)

    # Format output
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

    # Write output
    if parsed_args.output:
        try:
            with open(parsed_args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(output_content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
