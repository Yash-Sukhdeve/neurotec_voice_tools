#!/bin/bash
#
# Neurotec Voice Tools Installation Script
# 
# This script sets up the Neurotec Voice Verification Python wrapper
# for easy system-wide access.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/bin"
SCRIPT_NAME="neurotec-voice-verifier"

echo "🔧 Installing Neurotec Voice Tools..."
echo "   Source: $SCRIPT_DIR"
echo "   Target: $INSTALL_DIR"

# Create bin directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Create wrapper script that can be run from anywhere
cat > "$INSTALL_DIR/$SCRIPT_NAME" << EOF
#!/bin/bash
#
# Neurotec Voice Verification Wrapper
# Auto-generated installation script
#
python3 "$SCRIPT_DIR/neurotec_voice_verifier.py" "\$@"
EOF

# Make it executable
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

echo "✅ Installation complete!"
echo ""
echo "🚀 Usage:"
echo "   $SCRIPT_NAME audio1.wav audio2.wav"
echo "   $SCRIPT_NAME --help"
echo "   $SCRIPT_NAME --info"
echo ""

# Check if ~/bin is in PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "⚠️  Note: $HOME/bin is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/bin:\$PATH\""
    echo ""
    echo "   Or run with full path: $INSTALL_DIR/$SCRIPT_NAME"
else
    echo "✅ $HOME/bin is in your PATH - you can run '$SCRIPT_NAME' from anywhere!"
fi

echo ""
echo "📁 Files in $SCRIPT_DIR:"
ls -la "$SCRIPT_DIR"