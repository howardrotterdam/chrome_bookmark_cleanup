from chrome_bookmark_cleanup.parser import parse_bookmarks_html, serialize_to_html

def test_parse_simple_structure(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    assert root.is_folder
    assert len(root.children) == 1
    
    bookmarks_bar = root.children[0]
    assert bookmarks_bar.is_folder
    assert bookmarks_bar.title == "Bookmarks bar"
    assert bookmarks_bar.attrs.get("add_date") == "1610000000"
    
    children = bookmarks_bar.children
    assert len(children) == 3
    
    empty_folder = children[0]
    assert empty_folder.is_folder
    assert empty_folder.title == "Empty Folder"
    assert len(empty_folder.children) == 0
    
    folder_a = children[1]
    assert folder_a.is_folder
    assert folder_a.title == "Folder A"
    assert len(folder_a.children) == 3
    
    google1 = folder_a.children[0]
    assert not google1.is_folder
    assert google1.title == "Google"
    assert google1.attrs.get("href") == "https://google.com"
    assert google1.attrs.get("add_date") == "1610000003"


def test_serialization(sample_bookmarks_html):
    root = parse_bookmarks_html(sample_bookmarks_html)
    serialized = serialize_to_html(root)
    
    # Reparse to ensure structural equality
    root2 = parse_bookmarks_html(serialized)
    assert len(root2.children) == 1
    
    bookmarks_bar = root2.children[0]
    assert bookmarks_bar.title == "Bookmarks bar"
    assert len(bookmarks_bar.children) == 3
    
    # Verify entity escaping
    from chrome_bookmark_cleanup.parser import BookmarkNode
    root_custom = BookmarkNode(is_folder=True, title="Root")
    custom_folder = BookmarkNode(is_folder=True, title="A & B <Folder>", attrs={"add_date": "100"})
    custom_bookmark = BookmarkNode(is_folder=False, title='Google "Search"', attrs={"href": "https://google.com?q=a&b", "add_date": "200"})
    custom_folder.children.append(custom_bookmark)
    root_custom.children.append(custom_folder)
    
    serialized_custom = serialize_to_html(root_custom)
    
    assert "A &amp; B &lt;Folder&gt;" in serialized_custom
    assert "Google &quot;Search&quot;" in serialized_custom
    assert "https://google.com?q=a&amp;b" in serialized_custom
