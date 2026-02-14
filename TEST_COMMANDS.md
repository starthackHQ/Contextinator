# Contextinator v2.0 - Quick Test Commands

## Setup
```bash
cd /mnt/d/coding/freelance/uval.ai/SemanticSage
CLI=".venv/bin/python -m contextinator.cli"
```

## 1. Read Entire File
```bash
$CLI read --path test_file.txt --mode Line
```

## 2. Read Specific Lines (10-20)
```bash
$CLI read --path src/contextinator/cli.py --mode Line --start-line 10 --end-line 20
```

## 3. Read Last 5 Lines
```bash
$CLI read --path test_file.txt --mode Line --start-line -5 --end-line -1
```

## 4. Read First 10 Lines
```bash
$CLI read --path README.md --mode Line --start-line 1 --end-line 10
```

## 5. List Directory (Non-Recursive)
```bash
$CLI read --path src/contextinator --mode Directory --depth 0
```

## 6. List Directory (Recursive, Depth 2)
```bash
$CLI read --path src/contextinator/chunking --mode Directory --depth 2
```

## 7. Search for Pattern
```bash
$CLI read --path src/contextinator --mode Search --pattern "def fs_read"
```

## 8. Search with More Context (5 lines)
```bash
$CLI read --path src/contextinator --mode Search --pattern "TODO" --context-lines 5
```

## 9. Search in Single File
```bash
$CLI read --path src/contextinator/tools.py --mode Search --pattern "import"
```

## 10. JSON Output
```bash
$CLI read --path test_file.txt --mode Line --start-line 1 --end-line 3 --format json
```

## 11. Read Function Definition
```bash
$CLI read --path src/contextinator/chunking/ast_parser.py --mode Line --start-line 678 --end-line 734
```

## 12. Search for Class Definitions
```bash
$CLI read --path src/contextinator --mode Search --pattern "^class "
```
