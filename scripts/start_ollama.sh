#!/bin/sh
# Run in a separate terminal; Ctrl+C stops this server.
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_NO_CLOUD=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
exec ollama serve
