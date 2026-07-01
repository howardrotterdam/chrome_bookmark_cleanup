from collections import defaultdict
from chrome_bookmark_cleanup.parser import BookmarkNode

def get_add_date(node):
    """Safely gets the ADD_DATE attribute of a node as an integer."""
    val = node.attrs.get('add_date') or node.attrs.get('ADD_DATE')
    if val is None:
        return 0
    try:
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


def build_parent_map(node, parent_map=None):
    """Builds a map from nodes to their parent folders."""
    if parent_map is None:
        parent_map = {}
    if node.is_folder:
        for child in node.children:
            parent_map[child] = node
            build_parent_map(child, parent_map)
    return parent_map


def get_folder_path(parent_node, parent_map):
    """Reconstructs the folder path list from a parent map (excluding the dummy Root)."""
    path = []
    curr = parent_node
    while curr and curr.title != "Root":
        path.append(curr.title)
        curr = parent_map.get(curr)
    return list(reversed(path))


def count_folders(node):
    """Counts the total number of folders in the tree (excluding Root)."""
    count = 0
    if node.is_folder:
        if node.title != "Root":
            count += 1
        for child in node.children:
            count += count_folders(child)
    return count


def count_bookmarks(node):
    """Counts the total number of bookmarks in the tree."""
    count = 0
    if node.is_folder:
        for child in node.children:
            count += count_bookmarks(child)
    else:
        count += 1
    return count


def remove_duplicates(root, parent_map):
    """1. Removes exact duplicate bookmarks (same URL and name, keeping the newest).
    Returns a list of tuples (removed_bookmark_node, original_folder_path_list).
    """
    bookmarks = collect_bookmarks_with_parents(root)
    
    # Group by (url, name)
    groups = defaultdict(list)
    for b, parent in bookmarks:
        url = get_url(b)
        groups[(url, b.title)].append((b, parent))
        
    removed_duplicates = []
    for (url, name), items in groups.items():
        if len(items) > 1:
            # Sort by add_date descending
            items.sort(key=lambda x: get_add_date(x[0]), reverse=True)
            # Keep the newest one (index 0) and remove all others
            for dup_b, parent in items[1:]:
                if dup_b in parent.children:
                    parent.children.remove(dup_b)
                    folder_path = get_folder_path(parent, parent_map)
                    removed_duplicates.append((dup_b, folder_path))
    return removed_duplicates


def merge_same_urls(root):
    """2. If URLs are the same but names are different, move both to the same folder
    where the newer bookmark is located, and store them next to each other.
    Returns the number of same-URL bookmarks merged (moved).
    """
    bookmarks = collect_bookmarks_with_parents(root)
    
    # Group by url
    groups = defaultdict(list)
    for b, parent in bookmarks:
        url = get_url(b)
        if url: # Only process valid URLs
            groups[url].append((b, parent))
            
    merged_count = 0
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
                merged_count += len(others_to_move)
                
    return merged_count


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


def merge_duplicate_folders(node):
    """Recursively merges subfolders with the same title under the same parent node.
    Returns the number of duplicate folders merged.
    """
    if not node.is_folder:
        return 0
        
    merged_count = 0
    # First, recursively merge subfolders in each child folder
    for child in node.children:
        if child.is_folder:
            merged_count += merge_duplicate_folders(child)
            
    # Find duplicate folders under the current node
    merged_children = []
    folder_map = {}
    
    for child in node.children:
        if child.is_folder:
            title = child.title
            if title in folder_map:
                target_folder = folder_map[title]
                target_folder.children.extend(child.children)
                merged_count += 1
            else:
                folder_map[title] = child
                merged_children.append(child)
        else:
            merged_children.append(child)
            
    node.children = merged_children
    
    # Recursively merge any newly combined subfolders
    for child in node.children:
        if child.is_folder:
            merged_count += merge_duplicate_folders(child)
            
    return merged_count


def cleanup_bookmarks(root):
    """Executes the entire cleanup pipeline on the bookmark tree.
    Returns (cleaned_root, removed_duplicates, stats).
    """
    # Build parent map and count metrics before cleanup
    folders_before = count_folders(root)
    bookmarks_before = count_bookmarks(root)
    
    # Merge duplicate folders first
    folders_merged = merge_duplicate_folders(root)
    
    # Build parent map after folder merging (since structure changed)
    parent_map = build_parent_map(root)
    
    # Run other cleanup steps
    removed_duplicates = remove_duplicates(root, parent_map)
    same_url_merged = merge_same_urls(root)
    remove_empty_folders(root)
    
    # Count metrics after cleanup
    folders_after = count_folders(root)
    bookmarks_after = count_bookmarks(root)
    empty_folders_removed = folders_before - folders_after - folders_merged
    
    stats = {
        "input_bookmarks": bookmarks_before,
        "output_bookmarks": bookmarks_after,
        "duplicates_removed": len(removed_duplicates),
        "same_url_merged": same_url_merged,
        "empty_folders_removed": empty_folders_removed,
        "folders_merged": folders_merged
    }
    
    return root, removed_duplicates, stats


def find_folder(node, target_path, current_path=None):
    """Recursively finds a folder by its exact path (joined by '/') or its folder title.
    Returns the BookmarkNode if found, or None.
    """
    if current_path is None:
        current_path = []
        
    if not node.is_folder:
        return None
        
    path_str = "/".join(current_path)
    if node.title != "Root":
        if path_str == target_path or node.title == target_path:
            return node
            
    for child in node.children:
        if child.is_folder:
            res = find_folder(child, target_path, current_path + [child.title])
            if res is not None:
                return res
    return None


def collect_bookmarks_recursive(node):
    """Collects all bookmarks (non-folder nodes) recursively under a given node."""
    bookmarks = []
    if node.is_folder:
        for child in node.children:
            bookmarks.extend(collect_bookmarks_recursive(child))
    else:
        bookmarks.append(node)
    return bookmarks


def sort_and_restructure_folder(root, target_path):
    """Finds the folder by target_path under root, and restructures/sorts it."""
    target_folder = find_folder(root, target_path)
    if not target_folder:
        raise ValueError(f"Bookmark folder '{target_path}' not found.")
    sort_and_restructure_node(target_folder)


def sort_all_folders(root):
    """Restructures and sorts all top-level folders (direct children of the Root node)."""
    for child in root.children:
        if child.is_folder:
            sort_and_restructure_node(child)


def get_pinyin_sort_key(b):
    """Sort key for case-insensitive alphabetical and Chinese Pinyin sorting."""
    title_str = str(b.title or "")
    try:
        from pypinyin import lazy_pinyin
        pinyin_list = lazy_pinyin(title_str)
        key = [p.lower() for p in pinyin_list]
        return (key, title_str.lower())
    except ImportError:
        return (title_str.lower(), title_str)


def sort_and_restructure_node(target_folder):
    """Restructures direct bookmarks in target_folder into yyyy/yymmdd folders
    if their count >= 400. Otherwise, sorts them alphabetically in-place.
    Recursively applies this behavior to all of target_folder's subfolders.
    """
    from datetime import datetime, timezone
    
    # 1. Separate direct bookmarks and subfolders
    direct_bookmarks = [c for c in target_folder.children if not c.is_folder]
    direct_folders = [c for c in target_folder.children if c.is_folder]
    
    if len(direct_bookmarks) >= 400:
        # Reorganize direct bookmarks into yyyy/yymmdd subfolders
        new_year_folders = []
        for b in direct_bookmarks:
            ts = get_add_date(b)
            # Normalize timestamp
            if ts > 100000000000:
                if ts > 100000000000000:
                    ts = ts // 1000000
                elif ts > 100000000000:
                    ts = ts // 1000
            try:
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                dt = datetime.fromtimestamp(0, tz=timezone.utc)
                
            yyyy = dt.strftime('%Y')
            yymmdd = dt.strftime('%y%m%d')
            
            # Find or create year folder in new_year_folders
            year_folder = None
            for yf in new_year_folders:
                if yf.title == yyyy:
                    year_folder = yf
                    break
            if year_folder is None:
                year_folder = BookmarkNode(is_folder=True, title=yyyy, attrs={"add_date": str(ts)})
                new_year_folders.append(year_folder)
                
            # Find or create date folder in year_folder
            date_folder = None
            for df in year_folder.children:
                if df.title == yymmdd:
                    date_folder = df
                    break
            if date_folder is None:
                date_folder = BookmarkNode(is_folder=True, title=yymmdd, attrs={"add_date": str(ts)})
                year_folder.children.append(date_folder)
                
            date_folder.children.append(b)
            
        # Sort year folders and date folders, and sort bookmarks in date folders
        new_year_folders.sort(key=lambda x: x.title)
        for yf in new_year_folders:
            yf.children.sort(key=lambda x: x.title)
            for df in yf.children:
                df.children.sort(key=get_pinyin_sort_key)
                
        # Target folder's children are the original subfolders plus the new year folders
        target_folder.children = direct_folders + new_year_folders
    else:
        # Just sort direct bookmarks alphabetically/Pinyin in-place
        direct_bookmarks.sort(key=get_pinyin_sort_key)
        target_folder.children = direct_folders + direct_bookmarks
        
    # 2. Recursively apply to all subfolders of target_folder
    # We only recurse on the original subfolders (excluding the new year folders)
    for subfolder in direct_folders:
        sort_and_restructure_node(subfolder)
