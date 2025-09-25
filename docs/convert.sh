#!/bin/bash

# Verityn AI Presentation - PDF Conversion Script
# This script converts the markdown presentation to PDF using pandoc

echo "🔍 Verityn AI - Converting Presentation to PDF..."
echo "=================================================="

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ Pandoc is not installed."
    echo ""
    echo "Please install pandoc first:"
    echo "  macOS: brew install pandoc"
    echo "  Ubuntu/Debian: sudo apt-get install pandoc"
    echo "  Windows: choco install pandoc"
    echo ""
    echo "Visit: https://pandoc.org/installing.html"
    exit 1
fi

echo "✅ Pandoc found: $(pandoc --version | head -n1)"
echo ""

# Check if required files exist
if [ ! -f "verityn_ai_presentation.md" ]; then
    echo "❌ verityn_ai_presentation.md not found in current directory"
    echo "Please run this script from the docs/ directory"
    exit 1
fi

if [ ! -f "style.css" ]; then
    echo "❌ style.css not found in current directory"
    echo "Please run this script from the docs/ directory"
    exit 1
fi

echo "📁 Files found:"
echo "  - verityn_ai_presentation.md"
echo "  - style.css"
echo ""

# Create output directory
mkdir -p output
echo "📂 Created output directory"

# Method 1: Basic PDF conversion
echo ""
echo "🔄 Method 1: Basic PDF conversion..."
pandoc verityn_ai_presentation.md \
  --toc \
  --pdf-engine=xelatex \
  --variable geometry:margin=1in \
  --variable fontsize=11pt \
  --variable mainfont="DejaVu Sans" \
  --variable monofont="DejaVu Sans Mono" \
  -o output/verityn_ai_presentation_basic.pdf

if [ $? -eq 0 ]; then
    echo "✅ Basic PDF created: output/verityn_ai_presentation_basic.pdf"
else
    echo "❌ Basic PDF creation failed"
fi

# Method 2: Styled PDF with CSS
echo ""
echo "🔄 Method 2: Styled PDF with CSS..."
pandoc verityn_ai_presentation.md \
  --css=style.css \
  --pdf-engine=wkhtmltopdf \
  --variable geometry:margin=1.5in \
  -o output/verityn_ai_presentation_styled.pdf

if [ $? -eq 0 ]; then
    echo "✅ Styled PDF created: output/verityn_ai_presentation_styled.pdf"
else
    echo "❌ Styled PDF creation failed (wkhtmltopdf may not be installed)"
fi

# Method 3: HTML conversion
echo ""
echo "🔄 Method 3: HTML conversion..."
pandoc verityn_ai_presentation.md \
  --standalone \
  --css=style.css \
  --metadata title="Verityn AI - Intelligent Document Chat for Audit & Compliance" \
  --metadata author="Vidhu C" \
  --metadata date="$(date +%Y-%m-%d)" \
  -o output/verityn_ai_presentation.html

if [ $? -eq 0 ]; then
    echo "✅ HTML created: output/verityn_ai_presentation.html"
else
    echo "❌ HTML creation failed"
fi

# Method 4: Professional PDF with LaTeX
echo ""
echo "🔄 Method 4: Professional PDF with LaTeX..."
pandoc verityn_ai_presentation.md \
  --pdf-engine=xelatex \
  --variable geometry:margin=1in \
  --variable fontsize=11pt \
  --variable mainfont="DejaVu Sans" \
  --variable monofont="DejaVu Sans Mono" \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --top-level-division=chapter \
  --variable documentclass=report \
  -o output/verityn_ai_presentation_professional.pdf

if [ $? -eq 0 ]; then
    echo "✅ Professional PDF created: output/verityn_ai_presentation_professional.pdf"
else
    echo "❌ Professional PDF creation failed"
fi

# Summary
echo ""
echo "🎯 Conversion Summary:"
echo "======================"

# Count successful conversions
success_count=0
total_count=0

if [ -f "output/verityn_ai_presentation_basic.pdf" ]; then
    echo "✅ Basic PDF: output/verityn_ai_presentation_basic.pdf"
    success_count=$((success_count + 1))
fi
total_count=$((total_count + 1))

if [ -f "output/verityn_ai_presentation_styled.pdf" ]; then
    echo "✅ Styled PDF: output/verityn_ai_presentation_styled.pdf"
    success_count=$((success_count + 1))
fi
total_count=$((total_count + 1))

if [ -f "output/verityn_ai_presentation.html" ]; then
    echo "✅ HTML: output/verityn_ai_presentation.html"
    success_count=$((success_count + 1))
fi
total_count=$((total_count + 1))

if [ -f "output/verityn_ai_presentation_professional.pdf" ]; then
    echo "✅ Professional PDF: output/verityn_ai_presentation_professional.pdf"
    success_count=$((success_count + 1))
fi
total_count=$((total_count + 1))

echo ""
echo "📊 Results: $success_count/$total_count conversions successful"

if [ $success_count -gt 0 ]; then
    echo ""
    echo "🎉 Conversion completed successfully!"
    echo "📁 Check the 'output/' directory for your files"
    echo ""
    echo "💡 Tips:"
    echo "  - Basic PDF: Good for quick sharing"
    echo "  - Styled PDF: Best visual appearance"
    echo "  - HTML: Easy to view in any browser"
    echo "  - Professional PDF: Best for printing and formal use"
else
    echo ""
    echo "❌ No conversions were successful"
    echo "Please check the error messages above and ensure all dependencies are installed"
fi

echo ""
echo "🔍 For more conversion options, see: convert_to_pdf.md"
