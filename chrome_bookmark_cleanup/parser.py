import html
from html.parser import HTMLParser

class BookmarkNode:
    """Represents a node in the bookmark tree structure (either a folder or a bookmark)."""
    def __init__(self, is_folder, title="", attrs=None):
        self.is_folder = is_folder
        self.title = title
        self.attrs = attrs or {}
        self.children = [] if is_folder else None

    def __repr__(self):
        if self.is_folder:
            return f"Folder(title={repr(self.title)}, children_count={len(self.children)})"
        else:
            return f"Bookmark(title={repr(self.title)}, href={repr(self.attrs.get('href'))})"


class BookmarkParser(HTMLParser):
    """Parses Netscape HTML bookmark exports into a tree of BookmarkNode objects."""
    def __init__(self):
        super().__init__()
        self.root = BookmarkNode(is_folder=True, title="Root")
        self.stack = [self.root]
        self.last_folder = None
        self.current_node_attrs = {}
        self.text_buffer = []
        self.in_h3 = False
        self.in_a = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'h3':
            self.in_h3 = True
            self.text_buffer = []
            self.current_node_attrs = attrs_dict
            self.last_folder = None
        elif tag == 'a':
            self.in_a = True
            self.text_buffer = []
            self.current_node_attrs = attrs_dict
            self.last_folder = None
        elif tag == 'dl':
            if self.last_folder:
                self.stack.append(self.last_folder)
                self.last_folder = None

    def handle_data(self, data):
        if self.in_h3 or self.in_a:
            self.text_buffer.append(data)

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_h3 = False
            title = "".join(self.text_buffer).strip()
            folder = BookmarkNode(is_folder=True, title=title, attrs=self.current_node_attrs)
            self.stack[-1].children.append(folder)
            self.last_folder = folder
        elif tag == 'a':
            self.in_a = False
            title = "".join(self.text_buffer).strip()
            bookmark = BookmarkNode(is_folder=False, title=title, attrs=self.current_node_attrs)
            self.stack[-1].children.append(bookmark)
        elif tag == 'dl':
            if len(self.stack) > 1:
                self.stack.pop()


def parse_bookmarks_html(html_content):
    """Parses an HTML bookmark string and returns the root BookmarkNode."""
    parser = BookmarkParser()
    parser.feed(html_content)
    return parser.root


def serialize_to_html(node):
    """Serializes a BookmarkNode tree back into Netscape HTML format."""
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file.",
        "     It will be read and written.",
        "     DO NOT EDIT! -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>"
    ]
    
    # Root level children
    for child in node.children:
        lines.extend(_serialize_node(child, indent_level=1))
        
    lines.append("</DL><p>")
    return "\n".join(lines) + "\n"


def _serialize_node(node, indent_level):
    indent = "    " * indent_level
    lines = []
    if node.is_folder:
        attrs_str = ""
        for k, v in node.attrs.items():
            escaped_val = html.escape(str(v), quote=True)
            attrs_str += f' {k.upper()}="{escaped_val}"'
        escaped_title = html.escape(node.title)
        lines.append(f'{indent}<DT><H3{attrs_str}>{escaped_title}</H3>')
        lines.append(f'{indent}<DL><p>')
        for child in node.children:
            lines.extend(_serialize_node(child, indent_level + 1))
        lines.append(f'{indent}</DL><p>')
    else:
        attrs_str = ""
        for k, v in node.attrs.items():
            escaped_val = html.escape(str(v), quote=True)
            attrs_str += f' {k.upper()}="{escaped_val}"'
        escaped_title = html.escape(node.title)
        lines.append(f'{indent}<DT><A{attrs_str}>{escaped_title}</A>')
    return lines
