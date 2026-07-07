#!/bin/sh
# Build the converter module. Requires the Rust wasm target:
#   rustup target add wasm32-unknown-unknown
set -e
cd "$(dirname "$0")"
rustc --target wasm32-unknown-unknown --crate-type cdylib \
  -C opt-level=s -C lto=fat -C target-feature=-bulk-memory \
  src/lib.rs -o convert.wasm
echo "built convert.wasm ($(wc -c < convert.wasm) bytes)"
