#!/bin/sh
set -eu

mkdir -p /workspace/output/runs
chown appuser:appuser /workspace/output /workspace/output/runs || true
exec runuser -u appuser -- "$@"
