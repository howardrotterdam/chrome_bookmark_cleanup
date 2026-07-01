from collections import defaultdict
from chrome_bookmark_cleanup.parser import BookmarkNode

def get_add_date(node):
    """Safely gets the ADD_DATE attribute of a node as an integer."""
    val = node.attrs.get('add_date') or node.attrs.get('ADD_DATE')
    if val is None:
        return 0
    try:
        # Some export files might store timestamp in microseconds, some in seconds.
        # We can just convert to integer for comparison.
        return int(val)
    except ValueError:
        return 0


def get_url(node):
    """Gets the URL of a bookmark node."""
    return node.attrs.get('href') or node.attrs.get('HREF') or ""


def collect_bookmarks_with_parents(node):
    """Traverses the tree to collect all bookmarks and their parents.
    Returns a list of tuples: (bookmark_node, parent_node).
    """
    bookmarks = []
    if node.is_folder:
        for child in node.children:
            if child.is_folder:
                bookmarks.extend(collect_bookmarks_with_parents(child))
            else:
                bookmarks.append((child, node))
    return bookmarks


def remove_duplicates(root):
    """1. Removes exact duplicate bookmarks (same URL and name, keeping the newest)."""
    bookmarks = collect_bookmarks_with_parents(root)
    
    # Group by (url, name)
    groups = defaultdict(list)
    for b, parent in bookmarks:
        url = get_url(b)
        groups[(url, b.title)].append((b, parent))
        
    for (url, name), items in groups.items():
        if len(items) > 1:
            # Sort by add_date descending
            items.sort(key=lambda x: get_add_date(x[0]), reverse=True)
            # Keep the newest one (index 0) and remove all others
            for dup_b, parent in items[1:]:
                if dup_b in parent.children:
                    parent.children.remove(dup_b)


def merge_same_urls(root):
    """2. If URLs are the same but names are different, move both to the same folder
    where the newer bookmark is located, and store them next to each other.
    """
    bookmarks = collect_bookmarks_with_parents(root)
    
    # Group by url
    groups = defaultdict(list)
    for b, parent in bookmarks:
        url = get_url(b)
        if url: # Only process valid URLs
            groups[url].append((b, parent))
            
    for url, items in groups.items():
        if len(items) > 1:
            # Find the newest bookmark in the group based on add_date
            # Sort by add_date descending
            items.sort(key=lambda x: get_add_date(x[0]), reverse=True)
            
            newest_b, target_folder = items[0]
            
            # The other bookmarks to move
            others_to_move = items[1:]
            
            # Remove all other bookmarks in the group from their original parents
            for other_b, parent in others_to_move:
                if other_b in parent.children:
                    parent.children.remove(other_b)
            
            # Collect the nodes of other bookmarks and sort them by add_date ascending
            other_nodes = [x[0] for x in others_to_move]
            other_nodes.sort(key=get_add_date)
            
            # Find the index of the newest bookmark in the target folder's children
            if newest_b in target_folder.children:
                idx = target_folder.children.index(newest_b)
                # Insert them right before the newest bookmark
                target_folder.children[idx:idx] = other_nodes


def remove_empty_folders(node):
    """3. Recursively removes empty folders from the tree.
    Returns True if the folder is empty and should be removed by its parent.
    """
    if not node.is_folder:
        return False
        
    # Recursively clean and filter child folders
    node.children = [
        child for child in node.children 
        if not (child.is_folder and remove_empty_folders(child))
    ]
    
    # Return True if folder has no children remaining
    return len(node.children) == 0


def cleanup_bookmarks(root):
    """Executes the entire cleanup pipeline on the bookmark tree."""
    remove_duplicates(root)
    merge_same_urls(root)
    remove_empty_folders(root)
    return root
