#!/bin/bash -e

# Threaded workers are required for metrics to work.
celery \
    -A farm.celery \
    worker \
    -Q flag_submition \
    --pool threads \
    -E --beat \
    --loglevel INFO \
    --concurrency=1