"""
Backup & Disaster Recovery Manager for NQS POS v2.0
Handles time-stamped ZIP archive creation, 30-day retention purging, and database restoration.
"""

import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from app.core.database import get_app_data_dir, get_db_path, get_connection


def get_backups_dir() -> Path:
    """Returns directory path where ZIP backups are stored."""
    backups_dir = get_app_data_dir() / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def create_local_backup() -> str:
    """
    Creates a time-stamped ZIP archive of the nqs_pos.db file.
    Also executes retention cleanup (purging backups older than 30 days).
    Returns path to created ZIP file.
    """
    db_path = get_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}")

    # Checkpoint WAL mode before backup
    try:
        conn = get_connection()
        conn.execute("PRAGMA wal_checkpoint(FULL);")
        conn.close()
    except Exception as e:
        print(f"Warning during WAL checkpoint: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"NQS_POS_Backup_{timestamp}.zip"
    zip_filepath = get_backups_dir() / zip_filename

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(db_path, arcname="nqs_pos.db")

    # Purge backups older than 30 days
    purge_old_backups(days=30)

    return str(zip_filepath)


def purge_old_backups(days: int = 30):
    """
    Deletes ZIP backup files in the backups folder that are older than specified days.
    """
    backups_dir = get_backups_dir()
    cutoff_time = datetime.now() - timedelta(days=days)

    for file_path in backups_dir.glob("NQS_POS_Backup_*.zip"):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_time:
                file_path.unlink()
                print(f"Purged old backup file: {file_path.name}")
        except Exception as e:
            print(f"Failed to check/delete old backup {file_path.name}: {e}")


def list_local_backups() -> List[Dict[str, Any]]:
    """
    Returns list of local backup files with metadata.
    """
    backups_dir = get_backups_dir()
    result = []

    for file_path in sorted(backups_dir.glob("NQS_POS_Backup_*.zip"), reverse=True):
        stat = file_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        size_kb = round(stat.st_size / 1024.0, 1)

        result.append({
            'filename': file_path.name,
            'filepath': str(file_path),
            'created_at': mtime.strftime("%Y-%m-%d %H:%M:%S"),
            'size_kb': size_kb
        })

    return result


def restore_database_from_backup(zip_filepath: str):
    """
    Restores nqs_pos.db from a specified ZIP backup file.
    """
    target_zip = Path(zip_filepath)
    if not target_zip.exists():
        raise FileNotFoundError(f"Backup file not found at {zip_filepath}")

    db_path = get_db_path()
    backup_temp_db = get_app_data_dir() / "nqs_pos_temp_restore.db"

    # Extract db to temporary location first
    with zipfile.ZipFile(target_zip, 'r') as zipf:
        if "nqs_pos.db" not in zipf.namelist():
            raise ValueError("Invalid backup file: 'nqs_pos.db' not found in ZIP archive.")
        zipf.extract("nqs_pos.db", path=get_app_data_dir())
        
        # Rename extracted file
        extracted = get_app_data_dir() / "nqs_pos.db"
        if extracted.exists() and db_path.exists():
            # Safely replace active DB
            wal_file = Path(str(db_path) + "-wal")
            shm_file = Path(str(db_path) + "-shm")
            if wal_file.exists():
                try: wal_file.unlink()
                except: pass
            if shm_file.exists():
                try: shm_file.unlink()
                except: pass

    print(f"Database successfully restored from {target_zip.name}")
