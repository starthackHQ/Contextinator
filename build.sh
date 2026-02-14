#!/bin/bash
# Build script for Contextinator v2.0

set -e

echo "🔨 Building Contextinator v2.0..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not found. Install from: https://rustup.rs/"
    exit 1
fi

# Check if maturin is installed
if ! command -v maturin &> /dev/null; then
    echo "📦 Installing maturin..."
    pip install maturin
fi

# Build Rust core
echo "🦀 Building Rust core..."
cd core
cargo build --release
cd ..

# Build Python package with maturin
echo "🐍 Building Python package..."
maturin develop --release

echo "✅ Build complete!"
echo ""
echo "Test with:"
echo "  contextinator read --path README.md --mode Line --start-line 1 --end-line 10"
