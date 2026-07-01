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
    
    # Verify cleaning took place
    assert "<TITLE>Bookmarks</TITLE>" in stdout
    assert "Google Search" in stdout
    assert "Google" in stdout
    # The duplicate (Google at 1610000001) is removed, but we still have one Google (1610000003)
    # The empty folders should be removed
    assert "Empty Folder" not in stdout
    assert "Nested Empty Folder" not in stdout


def test_cli_json_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "json"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    
    # After cleanup, we expect 3 bookmarks: Google Search, Google, Yahoo
    assert len(data) == 3
    
    # Verify their fields and folders
    assert data[0]["folder"] == "Bookmarks bar/Folder A"
    assert data[0]["name"] == "Google Search"
    assert data[0]["url"] == "https://google.com"
    assert data[0]["add_date"] == 1610000000
    
    assert data[1]["folder"] == "Bookmarks bar/Folder A"
    assert data[1]["name"] == "Google"
    assert data[1]["url"] == "https://google.com"
    assert data[1]["add_date"] == 1610000003
    
    assert data[2]["folder"] == "Bookmarks bar/Folder B"
    assert data[2]["name"] == "Yahoo"
    assert data[2]["url"] == "https://yahoo.com"
    assert data[2]["add_date"] == 1610000006


def test_cli_csv_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "csv"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    
    assert lines[0] == "folder,name,url,add_date"
    assert lines[1] == "Bookmarks bar/Folder A,Google Search,https://google.com,1610000000"
    assert lines[2] == "Bookmarks bar/Folder A,Google,https://google.com,1610000003"
    assert lines[3] == "Bookmarks bar/Folder B,Yahoo,https://yahoo.com,1610000006"


def test_cli_tsv_output(tmp_path, sample_bookmarks_html, capsys):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    
    exit_code = main([str(input_file), "-f", "tsv"])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    
    assert lines[0] == "folder\tname\turl\tadd_date"
    assert lines[1] == "Bookmarks bar/Folder A\tGoogle Search\thttps://google.com\t1610000000"
    assert lines[2] == "Bookmarks bar/Folder A\tGoogle\thttps://google.com\t1610000003"
    assert lines[3] == "Bookmarks bar/Folder B\tYahoo\thttps://yahoo.com\t1610000006"


def test_cli_output_file(tmp_path, sample_bookmarks_html):
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(sample_bookmarks_html, encoding="utf-8")
    output_file = tmp_path / "output.json"
    
    exit_code = main([str(input_file), "-o", str(output_file), "-f", "json"])
    assert exit_code == 0
    
    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(data) == 3


def test_cli_invalid_input(tmp_path, capsys):
    # Pass non-existent file
    exit_code = main(["non_existent_file.html"])
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Error: Input file 'non_existent_file.html' does not exist." in captured.err
