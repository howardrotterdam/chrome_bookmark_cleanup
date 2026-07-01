import pytest

@pytest.fixture
def sample_bookmarks_html():
    return """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and written.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1610000000" LAST_MODIFIED="1610000000">Bookmarks bar</H3>
    <DL><p>
        <DT><H3 ADD_DATE="1610000001" LAST_MODIFIED="1610000001">Empty Folder</H3>
        <DL><p>
        </DL><p>
        <DT><H3 ADD_DATE="1610000002" LAST_MODIFIED="1610000002">Folder A</H3>
        <DL><p>
            <DT><A HREF="https://google.com" ADD_DATE="1610000003">Google</A>
            <DT><A HREF="https://google.com" ADD_DATE="1610000001">Google</A>
            <DT><H3 ADD_DATE="1610000004" LAST_MODIFIED="1610000004">Nested Empty Folder</H3>
            <DL><p>
            </DL><p>
        </DL><p>
        <DT><H3 ADD_DATE="1610000005" LAST_MODIFIED="1610000005">Folder B</H3>
        <DL><p>
            <DT><A HREF="https://google.com" ADD_DATE="1610000000">Google Search</A>
            <DT><A HREF="https://yahoo.com" ADD_DATE="1610000006">Yahoo</A>
        </DL><p>
    </DL><p>
</DL><p>
"""
