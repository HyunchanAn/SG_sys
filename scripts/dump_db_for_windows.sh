#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Backing up Postgres database..."
mkdir -p "$BASE_DIR/SG_DB/init_scripts"
docker exec sg_proj_004_db pg_dump -U sg_user sg_proj_004 > "$BASE_DIR/SG_DB/init_scripts/init.sql"
echo "Postgres backup complete: SG_DB/init_scripts/init.sql"

echo "Backing up SQLite databases to temp/..."
mkdir -p "$BASE_DIR/temp"
cp "$BASE_DIR/SG_DB/test.db" "$BASE_DIR/temp/test_SG_DB.db" 2>/dev/null || true
cp "$BASE_DIR/SG_proj_004/test.db" "$BASE_DIR/temp/test_004.db" 2>/dev/null || true
cp "$BASE_DIR/SG_proj_009/qc_cache.db" "$BASE_DIR/temp/qc_cache_009.db" 2>/dev/null || true
cp "$BASE_DIR/SG_DB/init_scripts/init.sql" "$BASE_DIR/temp/init.sql" 2>/dev/null || true
echo "Backup to temp/ completed."
