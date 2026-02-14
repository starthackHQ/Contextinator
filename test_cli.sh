#!/bin/bash
# Quick test script for Contextinator v2.0

CLI=".venv/bin/python -m contextinator.cli"

echo "🧪 Testing Contextinator v2.0"
echo "=============================="
echo ""

echo "📄 Test 1: Read entire file"
$CLI read --path test_file.txt --mode Line
echo ""

echo "📄 Test 2: Read lines 2-5"
$CLI read --path test_file.txt --mode Line --start-line 2 --end-line 5
echo ""

echo "📄 Test 3: Read last 3 lines"
$CLI read --path test_file.txt --mode Line --start-line -3 --end-line -1
echo ""

echo "📁 Test 4: List directory"
$CLI read --path . --mode Directory --depth 0
echo ""

echo "🔍 Test 5: Search for TODO"
$CLI read --path . --mode Search --pattern "TODO"
echo ""

echo "✅ All tests complete!"
