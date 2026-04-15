#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🛡️ Initiating Project Aegis Hardware Setup..."

echo "📦 1/4: Installing Python dependencies..."
pip install -r requirements.txt

echo "🧠 2/4: Pre-caching spaCy multilingual model for offline use..."
# This prevents the application from trying to download the model while air-gapped
python -m spacy download xx_ent_wiki_sm

echo "⚙️ 3/4: Cloning and Compiling llama.cpp (Metal API)..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    # Compile with Apple Silicon GPU acceleration
    make LLAMA_METAL=1
    cd ..
else
    echo "llama.cpp already exists. Skipping clone."
fi

echo "🤖 4/4: Downloading Gemma-2-2B-IT Quantized Edge Model..."
cd llama.cpp
if [ ! -f "gemma-2-2b-it-Q4_K_M.gguf" ]; then
    # Downloading the specific quantized weights expected by backend/utils/llama_runner.py
    curl -L -o gemma-2-2b-it-Q4_K_M.gguf "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
else
    echo "Model weights already downloaded. Skipping."
fi
cd ..

echo "✅ Setup Complete. Aegis is ready for air-gapped deployment."
echo "⚠️ REMINDER: You MUST disable your Wi-Fi/Ethernet before running the application, or the Layer 0 Network Guard will terminate the session."