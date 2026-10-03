import os
import tempfile
from app import config
from app.common.fileutil import _is_perf_file


def test_is_perf_file_unreadable_bytes():
    # Create a temporary file in PROFILE_DIR containing invalid UTF-8 bytes
    with tempfile.NamedTemporaryFile(dir=config.PROFILE_DIR, mode="wb", delete=False) as f:
        f.write(b"\xff\xfe\xfd\x00\x98\xa1\xb2\xc3")
        temp_path = f.name

    try:
        # Should return False without raising UnicodeDecodeError
        assert _is_perf_file(temp_path) is False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
