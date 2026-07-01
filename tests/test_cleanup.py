from chrome_bookmark_cleanup.parser import parse_bookmarks_html
from chrome_bookmark_cleanup.cleanup import (
    remove_duplicates,
    merge_same_urls,
    remove_empty_folders,
    cleanup_bookmarks,
    collect_bookmarks_with_parents,
    get_url
)

def test_remove_duplicates(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    remove_duplicates(root)
    
    # Verify duplicates are removed
    bookmarks = collect_bookmarks_with_parents(root)
    # Total bookmarks in sample is 4: Google (1610000003), Google (1610000001), Google Search (1610000000), Yahoo (1610000006)
    # The duplicate (Google at 1610000001) should be removed.
    assert len(bookmarks) == 3
    
    # Check that Google (1610000003) is kept, not Google (1610000001)
    google_bookmarks = [b for b, p in bookmarks if b.title == "Google"]
    assert len(google_bookmarks) == 1
    assert google_bookmarks[0].attrs.get("add_date") == "1610000003"


def test_merge_same_urls(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    # Remove duplicates first to get clean state
    remove_duplicates(root)
    merge_same_urls(root)
    
    bookmarks = collect_bookmarks_with_parents(root)
    # Google Search (1610000000) and Google (1610000003) share the same URL.
    # The newer one is Google (1610000003) in Folder A.
    # Both should be in Folder A, next to each other.
    # Google Search (1610000000) is older, Google (1610000003) is newer.
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
    
    # Check that the folder structures are correct
    assert folder_a.children[0].title == "Google Search"
    assert folder_a.children[1].title == "Google"


def test_remove_empty_folders(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    # Perform full cleanup to make sure some folders empty out or start empty
    remove_duplicates(root)
    merge_same_urls(root)
    
    # Remove empty folders recursively
    remove_empty_folders(root)
    
    bookmarks_bar = root.children[0]
    folder_titles = [c.title for c in bookmarks_bar.children if c.is_folder]
    
    # "Empty Folder" should be gone
    assert "Empty Folder" not in folder_titles
    
    # "Folder A" should still be there (contains bookmarks)
    assert "Folder A" in folder_titles
    folder_a = [c for c in bookmarks_bar.children if c.title == "Folder A"][0]
    # "Nested Empty Folder" inside Folder A should be gone
    assert "Nested Empty Folder" not in [c.title for c in folder_a.children if c.is_folder]
    
    # "Folder B" should still be there (contains Yahoo)
    assert "Folder B" in folder_titles


def test_full_cleanup_pipeline(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    cleanup_bookmarks(root)
    
    bookmarks_bar = root.children[0]
    folder_titles = [c.title for c in bookmarks_bar.children if c.is_folder]
    
    # Assert folder structure
    assert "Empty Folder" not in folder_titles
    assert "Folder A" in folder_titles
    assert "Folder B" in folder_titles
    
    folder_a = [c for c in bookmarks_bar.children if c.title == "Folder A"][0]
    assert len(folder_a.children) == 2  # Google Search, Google (nested empty folder removed)
    assert folder_a.children[0].title == "Google Search"
    assert folder_a.children[1].title == "Google"
    
    folder_b = [c for c in bookmarks_bar.children if c.title == "Folder B"][0]
    assert len(folder_b.children) == 1
    assert folder_b.children[0].title == "Yahoo"
