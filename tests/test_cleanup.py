from chrome_bookmark_cleanup.parser import parse_bookmarks_html
from chrome_bookmark_cleanup.cleanup import (
    remove_duplicates,
    merge_same_urls,
    remove_empty_folders,
    cleanup_bookmarks,
    collect_bookmarks_with_parents,
    build_parent_map,
    get_url
)

def test_remove_duplicates(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    parent_map = build_parent_map(root)
    removed = remove_duplicates(root, parent_map)
    
    # Verify duplicates are removed
    bookmarks = collect_bookmarks_with_parents(root)
    assert len(bookmarks) == 3
    
    # Check that Google (1610000003) is kept, not Google (1610000001)
    google_bookmarks = [b for b, p in bookmarks if b.title == "Google"]
    assert len(google_bookmarks) == 1
    assert google_bookmarks[0].attrs.get("add_date") == "1610000003"
    
    # Verify removed details
    assert len(removed) == 1
    dup_b, folder_path = removed[0]
    assert dup_b.title == "Google"
    assert dup_b.attrs.get("add_date") == "1610000001"
    assert folder_path == ["Bookmarks bar", "Folder A"]


def test_merge_same_urls(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    parent_map = build_parent_map(root)
    remove_duplicates(root, parent_map)
    merged_count = merge_same_urls(root)
    
    assert merged_count == 1
    bookmarks = collect_bookmarks_with_parents(root)
    # Google Search (1610000000) and Google (1610000003) share the same URL.
    # Sorted order should be [Google Search, Google] in Folder A.
    bookmarks_bar = root.children[0]
    folder_a = [c for c in bookmarks_bar.children if c.title == "Folder A"][0]
    folder_b = [c for c in bookmarks_bar.children if c.title == "Folder B"][0]
    
    # Google Search should no longer be in Folder B
    b_bookmarks = [c for c in folder_b.children if not c.is_folder]
    assert len(b_bookmarks) == 1
    assert b_bookmarks[0].title == "Yahoo"
    
    # Folder A should contain Google Search and Google next to each other
    a_bookmarks = [c for c in folder_a.children if not c.is_folder]
    assert len(a_bookmarks) == 2
    assert a_bookmarks[0].title == "Google Search"
    assert a_bookmarks[1].title == "Google"


def test_remove_empty_folders(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    parent_map = build_parent_map(root)
    remove_duplicates(root, parent_map)
    merge_same_urls(root)
    remove_empty_folders(root)
    
    bookmarks_bar = root.children[0]
    folder_titles = [c.title for c in bookmarks_bar.children if c.is_folder]
    
    # "Empty Folder" should be gone
    assert "Empty Folder" not in folder_titles
    
    # "Folder A" should still be there
    assert "Folder A" in folder_titles
    folder_a = [c for c in bookmarks_bar.children if c.title == "Folder A"][0]
    # "Nested Empty Folder" inside Folder A should be gone
    assert "Nested Empty Folder" not in [c.title for c in folder_a.children if c.is_folder]
    
    # "Folder B" should still be there
    assert "Folder B" in folder_titles


def test_full_cleanup_pipeline(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    cleaned_root, removed_duplicates, stats = cleanup_bookmarks(root)
    
    # Assert folder structure
    bookmarks_bar = cleaned_root.children[0]
    folder_titles = [c.title for c in bookmarks_bar.children if c.is_folder]
    
    assert "Empty Folder" not in folder_titles
    assert "Folder A" in folder_titles
    assert "Folder B" in folder_titles
    
    folder_a = [c for c in bookmarks_bar.children if c.title == "Folder A"][0]
    assert len(folder_a.children) == 2
    assert folder_a.children[0].title == "Google Search"
    assert folder_a.children[1].title == "Google"
    
    # Assert statistics
    assert stats["input_bookmarks"] == 4
    assert stats["output_bookmarks"] == 3
    assert stats["duplicates_removed"] == 1
    assert stats["same_url_merged"] == 1
    assert stats["empty_folders_removed"] == 2


def test_sort_small_folder_in_place():
    from chrome_bookmark_cleanup.cleanup import sort_and_restructure_folder
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Folder A</H3>
    <DL><p>
        <DT><A HREF="https://google.com" ADD_DATE="1610000000">谷歌</A>
        <DT><A HREF="https://baidu.com" ADD_DATE="1610000000">百度</A>
        <DT><A HREF="https://tencent.com" ADD_DATE="1610000000">腾讯</A>
        <DT><A HREF="https://apple.com" ADD_DATE="1610000000">Apple</A>
        <DT><A HREF="https://yahoo.com" ADD_DATE="1610000000">Yahoo</A>
    </DL><p>
</DL><p>
"""
    root = parse_bookmarks_html(html)
    sort_and_restructure_folder(root, "Folder A")
    
    folder_a = root.children[0]
    assert folder_a.title == "Folder A"
    # Small count (< 400) -> should be sorted in-place, no year folder
    assert len(folder_a.children) == 5
    titles = [b.title for b in folder_a.children]
    assert titles == ["Apple", "百度", "谷歌", "腾讯", "Yahoo"]


def test_sort_large_folder_restructured():
    from chrome_bookmark_cleanup.cleanup import sort_and_restructure_folder, build_parent_map
    from chrome_bookmark_cleanup.parser import BookmarkNode
    
    root = BookmarkNode(is_folder=True, title="Root")
    folder_a = BookmarkNode(is_folder=True, title="Folder A")
    root.children.append(folder_a)
    
    # 400 bookmarks
    for i in range(400):
        b = BookmarkNode(is_folder=False, title=f"Bookmark {i:03d}", attrs={"href": "https://example.com", "add_date": "1610000000"})
        folder_a.children.append(b)
        
    sort_and_restructure_folder(root, "Folder A")
    
    # Large count (>= 400) -> should restructure into yyyy/yymmdd
    assert len(folder_a.children) == 1
    year_folder = folder_a.children[0]
    assert year_folder.title == "2021"
    
    assert len(year_folder.children) == 1
    date_folder = year_folder.children[0]
    assert date_folder.title == "210107"
    assert len(date_folder.children) == 400
    assert date_folder.children[0].title == "Bookmark 000"


def test_sort_subfolders_recursively():
    from chrome_bookmark_cleanup.cleanup import sort_and_restructure_folder
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Parent</H3>
    <DL><p>
        <DT><A HREF="https://z.com" ADD_DATE="1610000000">Z</A>
        <DT><H3>Child</H3>
        <DL><p>
            <DT><A HREF="https://y.com" ADD_DATE="1610000000">Y</A>
            <DT><A HREF="https://x.com" ADD_DATE="1610000000">X</A>
        </DL><p>
    </DL><p>
</DL><p>
"""
    root = parse_bookmarks_html(html)
    sort_and_restructure_folder(root, "Parent")
    
    parent = root.children[0]
    assert parent.title == "Parent"
    
    # Parent should contain Folder "Child" and Bookmark "Z" (folders first, then bookmarks)
    assert len(parent.children) == 2
    assert parent.children[0].title == "Child"
    assert parent.children[1].title == "Z"
    
    # Child should be sorted in-place internally
    child = parent.children[0]
    assert len(child.children) == 2
    assert child.children[0].title == "X"
    assert child.children[1].title == "Y"

