#!/usr/bin/env python3
"""Check for broken internal links and unused images in the docs."""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

DOCS_DIR = Path(__file__).parent / "Docs"

# Image extensions to track
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}

def find_all_images(root: Path) -> set[Path]:
    """Return all image files under root."""
    images = set()
    for ext in IMG_EXTS:
        for f in root.rglob(f"*{ext}"):
            images.add(f.resolve())
    return images

def find_all_yml_files(root: Path) -> list[Path]:
    """Return all .yml/.yaml files under root."""
    return list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))

def extract_yml_image_refs(yml_path: Path, base: Path = None) -> set[str]:
    """Extract image paths referenced in yml config files (e.g. logo, favicon)."""
    if base is None:
        base = yml_path.parent
    text = yml_path.read_text(encoding="utf-8")
    images = set()
    for m in re.finditer(r'(?:logo|favicon|icon|image|src)\s*:\s*(.+)', text):
        val = m.group(1).strip().strip('"').strip("'")
        if val and not val.startswith(("http://", "https://")):
            target = (base / val).resolve()
            images.add(str(target))
    return images

def find_all_md_files(root: Path) -> list[Path]:
    """Return all .md files under root."""
    return list(root.rglob("*.md"))

def extract_references(md_path: Path) -> tuple[set[str], set[str]]:
    """
    Parse a markdown file and return:
      - local_links: set of local paths referenced in []() or []() links
      - local_images: set of local image paths referenced in ![]() or <img src="">
    Excludes external URLs (http/https).
    """
    text = md_path.read_text(encoding="utf-8")
    base = md_path.parent

    local_links = set()
    local_images = set()

    # Pattern 1: [text](url)  and  ![alt](url)
    for m in re.finditer(r'!?\[.*?\]\(([^\)]+)\)', text):
        url = m.group(1).strip()
        # Skip external URLs
        if url.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Strip anchor and query
        url = url.split("#")[0].split("?")[0]
        if not url:
            continue
        target = (base / url).resolve()
        if m.group(0).startswith("!"):
            local_images.add(str(target))
        else:
            local_links.add(str(target))

    # Pattern 2: <img src="...">
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.IGNORECASE):
        url = m.group(1).strip()
        if url.startswith(("http://", "https://")):
            continue
        url = url.split("?")[0]
        if not url:
            continue
        target = (base / url).resolve()
        local_images.add(str(target))

    return local_links, local_images

def main():
    md_files = find_all_md_files(DOCS_DIR)
    all_images_on_disk = find_all_images(DOCS_DIR)

    all_refd_links: dict[str, list[str]] = defaultdict(list)   # target → [source files]
    all_refd_images: dict[str, list[str]] = defaultdict(list)

    print(f"Scanning {len(md_files)} .md files and {len(all_images_on_disk)} images...\n")

    # Scan .md files
    for md in md_files:
        local_links, local_images = extract_references(md)
        rel_md = str(md.relative_to(DOCS_DIR))
        for link in local_links:
            all_refd_links[link].append(rel_md)
        for img in local_images:
            all_refd_images[img].append(rel_md)

    # Scan .yml config files (for logo, favicon, etc.)
    # Include both Docs/ subdir and repo root (properdocs.yml lives there)
    yml_files = find_all_yml_files(DOCS_DIR) + find_all_yml_files(DOCS_DIR.parent)
    for yml in yml_files:
        # For yml at repo root, paths are relative to DOCS_DIR (mkdocs docs_dir)
        base = DOCS_DIR if yml.parent == DOCS_DIR.parent else yml.parent
        imgs = extract_yml_image_refs(yml, base)
        rel = str(yml.relative_to(DOCS_DIR.parent)) if DOCS_DIR.parent in yml.parents else str(yml.relative_to(DOCS_DIR))
        for img in imgs:
            all_refd_images[img].append(rel)

    # --- Broken internal links ---
    broken = 0
    print("=" * 60)
    print("BROKEN INTERNAL LINKS")
    print("=" * 60)
    for target, sources in sorted(all_refd_links.items()):
        tpath = Path(target)
        # Check if the target file exists
        if not tpath.exists():
            # Could be a .md file missing the extension — try appending .md
            if not Path(target + ".md").exists():
                print(f"\n  ✗ {Path(target).name}")
                print(f"    Referenced by:")
                for s in sources:
                    print(f"      - {s}")
                broken += 1
    if broken == 0:
        print("  ✓ No broken internal links found.")
    else:
        print(f"\n  Total: {broken} broken link(s)")

    # --- Unused images ---
    unused = 0
    print("\n" + "=" * 60)
    print("UNUSED IMAGES")
    print("=" * 60)
    all_refd_image_paths = {Path(p) for p in all_refd_images}
    for img in sorted(all_images_on_disk):
        if img not in all_refd_image_paths:
            rel = img.relative_to(DOCS_DIR)
            print(f"  ✗ {rel} ({img.stat().st_size / 1024:.1f} KB)")
            unused += 1
    if unused == 0:
        print("  ✓ No unused images found.")
    else:
        print(f"\n  Total: {unused} unused image(s)")

    # --- Links that reference directories (ambiguous) ---
    # (Skipping for brevity — mkdocs resolves /index.md, etc.)

    print()
    return 0 if (broken + unused) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
