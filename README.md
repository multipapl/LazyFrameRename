# Lazy Rename

**Lazy Rename** is a minimal Python tool for batch-renaming rendered frames by trimming suffixes and applying clean sequential numbering.

## Purpose

- Clean up inconsistent or broken frame filenames  
- Remove suffixes like `_0005`, `0012`, etc.  
- Rename files to a consistent `.0001`, `.0002`, … format  
- Process multiple folders quickly before editing or postproduction

## How it works

1. **Select mode**:
   - `Select folders manually`: add individual folders
   - `Process all subfolders`: choose one parent folder, process all its immediate subfolders
2. **Set number of characters to trim** (from the end of the filename before extension)
3. **Click Rename files** — filenames will be updated in alphabetical order

## Requirements

- Python 3
- No external libraries neede
