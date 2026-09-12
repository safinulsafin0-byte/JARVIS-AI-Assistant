from pathlib import Path
import shutil
from config import ALLOWED_ROOT_DIRS

def _allowed(path):
    p = Path(path).expanduser().resolve()
    for root in ALLOWED_ROOT_DIRS:
        try:
            p.relative_to(root.resolve())
            return p
        except ValueError:
            continue
    raise PermissionError(f"Path is outside allowed roots: {p}")

def list_dir(path):
    p = _allowed(path)
    return "\n".join(f"{x.name}\t{'DIR' if x.is_dir() else 'FILE'}" for x in p.iterdir())

def read_file(path):
    p = _allowed(path)
    return p.read_text(encoding="utf-8", errors="replace")

def create_file(path, content=""):
    p = _allowed(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Created file: {p}"

def create_folder(path):
    p = _allowed(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Created folder: {p}"

def write_file(path, content):
    p = _allowed(path)
    p.write_text(content, encoding="utf-8")
    return f"Written: {p}"

def rename(path, new_name):
    p = _allowed(path)
    target = _allowed(p.parent / new_name)
    p.rename(target)
    return f"Renamed to: {target}"

def move(path, destination):
    p = _allowed(path)
    d = _allowed(destination)
    d.mkdir(parents=True, exist_ok=True)
    target = d / p.name
    shutil.move(str(p), str(target))
    return f"Moved to: {target}"

def copy(path, destination):
    p = _allowed(path)
    d = _allowed(destination)
    d.mkdir(parents=True, exist_ok=True)
    target = d / p.name
    if p.is_dir():
        shutil.copytree(p, target, dirs_exist_ok=True)
    else:
        shutil.copy2(p, target)
    return f"Copied to: {target}"

def delete_file(path):
    p = _allowed(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    p.unlink()
    return f"Deleted file: {p}"

def delete_folder(path):
    p = _allowed(path)
    if not p.is_dir():
        raise FileNotFoundError(path)
    shutil.rmtree(p)
    return f"Deleted folder: {p}"

def search_files(root, pattern="*"):
    p = _allowed(root)
    matches = list(p.rglob(pattern))
    return "\n".join(str(x) for x in matches[:500])
