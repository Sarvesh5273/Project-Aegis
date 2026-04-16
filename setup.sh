#!/bin/bash
# ==============================================================================
# Project Aegis: Air-Gapped Hardware Provisioning Script
# ==============================================================================
# This script provisions a clean machine for local, offline AI inference.
# It prioritizes cross-platform reproducibility using modern CMake build chains.

set -e

echo "🛡️ Initiating Project Aegis Hardware Setup..."

echo "📦 1/4: Installing Python dependencies..."
pip install -r requirements.txt

echo "🧠 2/4: Pre-caching spaCy multilingual model for offline use..."
# CRITICAL PRE-CACHE: Prevents application crash during air-gapped deployment
python -m spacy download xx_ent_wiki_sm

echo "⚙️ 3/4: Cloning and Compiling llama.cpp (Metal API)..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    
    # Modern CMake build chain.
    # Replaces deprecated Makefile flags to ensure robust compilation on clean machines.
    cmake -B build -DGGML_METAL=ON
    cmake --build build --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
    cd ..
else
    echo "llama.cpp already exists. Skipping clone/build."
fi

echo "🤖 4/4: Downloading Gemma 4 2B-IT Quantized Edge Model..."
cd llama.cpp
# HACKATHON TARGET: Google's official Gemma 4 (2B) Q4 GGUF for edge hardware.
if [ ! -f "gemma-4-2b-it-Q4_K_M.gguf" ]; then
    curl -L -o gemma-4-2b-it-Q4_K_M.gguf \
      "https://huggingface.co/google/gemma-4-2b-it-GGUF/resolve/main/gemma-4-2b-it-Q4_K_M.gguf"
else
    echo "Gemma 4 weights already downloaded. Skipping."
fi
cd ..

echo "✅ Setup Complete. Aegis is ready for air-gapped deployment."