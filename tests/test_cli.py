import json
import os
import pytest
from chrome_bookmark_cleanup.main import main

def test_cli_html_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    # Run main with input file (default format: html, output to stdout)
    exit_code = main([str(input_file)])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    stdout = captured.out
    stderr = captured.err
    
    # Verify cleaning took place in main output
    assert "<TITLE>Bookmarks</TITLE>" in stdout
    assert "Google Search" in stdout
    assert "Google" in stdout
    assert "Empty Folder" not in stdout
    assert "Nested Empty Folder" not in stdout
    
    # Verify stats in stderr
    assert "=== Chrome Bookmark Cleanup Statistics ===" in stderr
    assert "Total Bookmarks Input:       4" in stderr
    assert "Total Bookmarks Output:      3" in stderr
    assert "Duplicate Bookmarks Removed: 1" in stderr
    assert "Same-URL Bookmarks Merged:   1" in stderr
    assert "Duplicate Folders Merged:    0" in stderr
    assert "Empty Folders Removed:       2" in stderr
    
    # Verify duplicates file next to input file
    dups_file = tmp_path / "bookmarks-dups.html"
    assert dups_file.exists()
    dups_content = dups_file.read_text(encoding="utf-8")
    assert "<TITLE>Bookmarks</TITLE>" in dups_content
    assert "Removed Duplicates" in dups_content
    assert "Google" in dups_content
    assert "1610000001" in dups_content


def test_cli_json_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "json"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    stderr = captured.err
    
    # After cleanup, we expect 3 bookmarks: Google Search, Google, Yahoo
    assert len(data) == 3
    
    # Verify stats
    assert "Duplicate Bookmarks Removed: 1" in stderr
    
    # Verify duplicates file
    dups_file = tmp_path / "bookmarks-dups.json"
    assert dups_file.exists()
    dups_data = json.loads(dups_file.read_text(encoding="utf-8"))
    assert len(dups_data) == 1
    assert dups_data[0]["folder"] == "Bookmarks bar/Folder A"
    assert dups_data[0]["name"] == "Google"
    assert dups_data[0]["url"] == "https://google.com"
    assert dups_data[0]["add_date"] == 1610000001


def test_cli_csv_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "csv"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    stderr = captured.err
    
    assert lines[0] == "folder,name,url,add_date"
    assert lines[1] == "Bookmarks bar/Folder A,Google Search,https://google.com,1610000000"
    
    # Verify stats
    assert "Duplicate Bookmarks Removed: 1" in stderr
    
    # Verify duplicates CSV
    dups_file = tmp_path / "bookmarks-dups.csv"
    assert dups_file.exists()
    dups_lines = dups_file.read_text(encoding="utf-8").strip().split("\n")
    assert dups_lines[0] == "folder,name,url,add_date"
    assert dups_lines[1] == "Bookmarks bar/Folder A,Google,https://google.com,1610000001"


def test_cli_tsv_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "tsv"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    stderr = captured.err
    
    assert lines[0] == "folder\tname\turl\tadd_date"
    assert lines[1] == "Bookmarks bar/Folder A\tGoogle Search\thttps://google.com\t1610000000"
    
    # Verify stats
    assert "Duplicate Bookmarks Removed: 1" in stderr
    
    # Verify duplicates TSV
    dups_file = tmp_path / "bookmarks-dups.tsv"
    assert dups_file.exists()
    dups_lines = dups_file.read_text(encoding="utf-8").strip().split("\n")
    assert dups_lines[0] == "folder\tname\turl\tadd_date"
    assert dups_lines[1] == "Bookmarks bar/Folder A\tGoogle\thttps://google.com\t1610000001"


def test_cli_output_file(tmp_path, sample_bookmarks_html):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    output_file = tmp_path / "output.json"
    
    exit_code = main([str(input_file), "-o", str(output_file), "-f", "json"])
    assert exit_code == 0
    
    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(data) == 3
    
    # Verify duplicates file is named output-dups.json
    dups_file = tmp_path / "output-dups.json"
    assert dups_file.exists()
    dups_data = json.loads(dups_file.read_text(encoding="utf-8"))
    assert len(dups_data) == 1


def test_cli_invalid_input(tmp_path, capsys):
    exit_code = main(["non_existent_file.html"])
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Error: Input file 'non_existent_file.html' does not exist." in captured.err


def test_cli_sort_option(tmp_path, capsys):
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Folder A</H3>
    <DL><p>
        <DT><A HREF="https://google.com" ADD_DATE="1610000000">谷歌</A>
        <DT><A HREF="https://baidu.com" ADD_DATE="1610000000">百度</A>
    </DL><p>
</DL><p>
"""
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(html, encoding="utf-8")
    
    exit_code = main([str(input_file), "--sort", "Folder A"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    stdout = captured.out
    
    assert "<H3>Folder A</H3>" in stdout
    assert "2021" not in stdout
    # "百度" should come before "谷歌" in the output HTML string
    assert stdout.find("百度") < stdout.find("谷歌")


def test_cli_sort_all_folders(tmp_path, capsys):
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Folder A</H3>
    <DL><p>
        <DT><A HREF="https://google.com" ADD_DATE="1610000000">谷歌</A>
    </DL><p>
    <DT><H3>Folder B</H3>
    <DL><p>
        <DT><A HREF="https://baidu.com" ADD_DATE="1610000000">百度</A>
    </DL><p>
</DL><p>
"""
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(html, encoding="utf-8")
    
    exit_code = main([str(input_file), "--sort"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    stdout = captured.out
    
    assert "<H3>Folder A</H3>" in stdout
    assert "<H3>Folder B</H3>" in stdout
    assert "2021" not in stdout
