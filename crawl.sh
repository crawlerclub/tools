#!/bin/bash

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 <config_file> <urls_file> [workers]"
    echo ""
    echo "Arguments:"
    echo "  config_file    Path to the JSON config file"
    echo "  urls_file      File containing URLs to process, one per line" 
    echo "  workers        Number of concurrent workers (default: 100)"
    echo ""
    echo "Example:"
    echo "  $0 config.json urls.txt 50"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: Config file '$1' does not exist"
    exit 1
fi

if [ ! -f "$2" ]; then
    echo "Error: URLs file '$2' does not exist"
    exit 1
fi

workers=${3:-100}

# Check if rabbitcrawler is installed
if ! command -v rabbitcrawler &> /dev/null; then
    echo "Installing rabbitcrawler..."
    
    # Check if Go is installed (only needed for installation)
    if ! command -v go &> /dev/null; then
        echo "Error: Go is required to install rabbitcrawler"
        echo "Please install Go first: https://golang.org/doc/install"
        exit 1
    fi
    
    # Try to install rabbitcrawler
    if ! go install github.com/crawlerclub/extractor/cmd/rabbitcrawler@latest; then
        echo "Error: Failed to install rabbitcrawler"
        exit 1
    fi
    
    # Verify installation was successful
    if ! command -v rabbitcrawler &> /dev/null; then
        echo "Error: Failed to install rabbitcrawler"
        exit 1
    fi
fi

# Get just the filename without path
config_basename=$(basename "$1")

# Create rawdata directory if it doesn't exist
mkdir -p rawdata

# Modified rabbitcrawler command with output path in rawdata directory
rabbitcrawler -config "$1" -output "rawdata/${config_basename%.*}_$(date +%Y%m%d_%H%M%S).jsonl" -urls "$2" -workers $workers
