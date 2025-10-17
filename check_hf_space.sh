#!/bin/bash
# Quick script to check if HF Space is ready

echo "Checking Hugging Face Space health..."
curl -s https://mathcsai-llm-code-deployment.hf.space/health | jq '.'

echo ""
echo "If you see 'status: healthy' above, the Space is ready!"
echo "If you get connection errors, the Space is still rebuilding."
