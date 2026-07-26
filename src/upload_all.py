import shutil
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from .state import load
from .upload import upload_video, get_service
from .config import STATE_FILE, CONFIG

QUOTA_MAX = 6
MAX_RETRIES = 3
RETRY_BACKOFF = [10, 30, 60]  # seconds between retries

def _is_retryable_error(e: Exception) -> bool:
    msg = str(e).lower()
    retryable = ['timeout', 'connection', '500', '502', '503', '429',
                 'ratelimit', 'rate limit', 'temporary', 'ssl']
    return any(r in msg for r in retryable)

def _is_quota_error(e: Exception) -> bool:
    msg = str(e).lower()
    return 'quota' in msg or 'dailylimitexceeded' in msg

def _refresh_token_if_needed():
    """Try to refresh YouTube token proactively to avoid mid-upload failures."""
    try:
        get_service()
        return True
    except Exception as e:
        print(f"  [WARN] Token refresh check failed: {e}")
        return False

def main():
    state = load()
    unpublished = [e for e in state["published"] if e.get("video_id") is None]

    if not unpublished:
        print("Semua video sudah terupload. Tidak ada yang perlu diupload.")
        return

    print(f"Ditemukan {len(unpublished)} video pending.")
    print(f"Kuota API: max {QUOTA_MAX} upload hari ini.\n")

    _refresh_token_if_needed()

    uploaded = 0
    for i, entry in enumerate(unpublished):
        if uploaded >= QUOTA_MAX:
            print(f"\nSudah mencapai batas {QUOTA_MAX} upload hari ini. Lanjutkan besok.")
            break

        path = Path(entry["path"])
        if not path.exists():
            print(f"[SKIP] File tidak ditemukan: {path}")
            continue

        safe_title = entry['title'].encode('ascii', errors='replace').decode('ascii')
        print(f"[{uploaded+1}/{min(len(unpublished), QUOTA_MAX)}] Uploading: {safe_title}")
        print(f"  path: {entry['path']}")

        success = False
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                tags = CONFIG["upload"]["default_tags"]
                desc = f"{entry['title']}\n\n{CONFIG['niche']}\n\n#shorts #{entry['topic'].replace('-', ' ')}"

                video_id = upload_video(
                    video_path=path,
                    title=entry["title"],
                    description=desc,
                    tags=tags,
                    publish_at=None,
                )
                print(f"  OK! Video ID: {video_id}")
                print(f"  https://youtube.com/shorts/{video_id}")

                for e in state["published"]:
                    if e["ts"] == entry["ts"] and e["title"] == entry["title"]:
                        e["video_id"] = video_id
                        break

                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)

                video_dir = path.parent
                if video_dir.exists():
                    shutil.rmtree(video_dir)
                    print(f"  Cleanup: {video_dir} deleted.")

                uploaded += 1
                success = True
                break

            except Exception as e:
                last_error = e
                if _is_quota_error(e):
                    print(f"  Kuota API habis. Hentikan upload.")
                    break
                if attempt < MAX_RETRIES - 1 and _is_retryable_error(e):
                    wait = RETRY_BACKOFF[attempt]
                    print(f"  Retryable error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                    print(f"  Waiting {wait}s before retry...")
                    time.sleep(wait)
                    # Try to refresh token before retry
                    _refresh_token_if_needed()
                else:
                    print(f"  GAGAL (attempt {attempt+1}/{MAX_RETRIES}): {e}")

        if not success and last_error and not _is_quota_error(last_error):
            print(f"  Skipping after {MAX_RETRIES} failed attempts.")

        time.sleep(5)

    print(f"\nSelesai. {uploaded} video berhasil diupload hari ini.")
    remaining = len([e for e in state["published"] if e.get("video_id") is None])
    if remaining > 0:
        print(f"Sisa {remaining} video pending. Akan terupload sesuai jadwal.")

if __name__ == "__main__":
    main()
