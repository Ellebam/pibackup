#!/bin/bash

mkdir -p backups
cd backups

# Date format: YYYYMMDD-HHMMSS
for i in {1..730}; do
  touch -t $(date -v-${i}d -u "+%Y%m%d%H%M.%S") "backup_$(date -v-${i}d -u "+%Y%m%d-%H%M%S").zip"
done