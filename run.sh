#!/bin/bash
# Example run script for VibeSliding
# Output will be saved to output_YYYYMMDD_HHMMSS/ by default
# Use --output my_dir to specify a custom directory

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🎨 VibeSliding - AI Presentation Generator"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    exit 1
fi

# Show Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "📍 Using: $PYTHON_VERSION"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if python -c "import httpx, tenacity, click, PIL, img2pdf, dotenv, tqdm" 2>/dev/null; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies missing. Installing...${NC}"
    echo ""
    
    if [ -f "requirements.txt" ]; then
        python -m pip install -q -r requirements.txt
        echo ""
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}Error: requirements.txt not found${NC}"
        exit 1
    fi
fi

echo ""
echo "🚀 Generating slides..."
echo ""

# Article references and slide-specific image references are declared in examples/outline.md.
# Run the CLI with all arguments passed to this script.
python -m src.cli \
  --outline examples/outline.md \
  --style "examples/style_*.png" \
  --copy 4 \
  "$@"
