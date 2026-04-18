#!/bin/bash
# ==============================================================================
# Project Aegis: Air-Gapped Hardware Provisioning Script
# ==============================================================================

set -e

echo "🛡️ Initiating Project Aegis Hardware Setup..."

echo "📦 1/4: Installing Python dependencies..."
pip install -r requirements.txt

echo "🧠 2/4: Pre-caching spaCy multilingual model for offline use..."
python -m spacy download xx_ent_wiki_sm

echo "⚙️ 3/4: Cloning and Compiling llama.cpp (Metal API)..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    cmake -B build -DGGML_METAL=ON
    cmake --build build --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
    cd ..
else
    echo "llama.cpp already exists. Skipping clone/build."
fi

echo "🤖 4/4: Downloading Gemma 4 E2B-IT Quantized Edge Model..."
cd llama.cpp

if [ ! -f "gemma-4-E2B-it-Q4_K_M.gguf" ]; then
    echo "Downloading ungated Gemma 4 E2B weights from Unsloth..."
    curl -L --max-redirs 5 -o gemma-4-E2B-it-Q4_K_M.gguf \
      "https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf?download=true"
else
    echo "Gemma 4 E2B weights already downloaded. Skipping."
fi
cd ..

echo "✅ Setup Complete. Aegis is ready for air-gapped deployment."