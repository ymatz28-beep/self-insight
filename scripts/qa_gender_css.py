#!/usr/bin/env python3
"""
QA: 性別CSS注入の整合性チェック

- 男性ユーザーのHTMLに女性CSS(f5eff2)が混入していないか確認
- 女性ユーザーのHTMLに女性CSSが正しく注入されているか確認
"""
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).parent.parent
MAPPING_FILE = BASE / "data/user_mapping.yaml"
FEMALE_MARKER = "f5eff2"
FEMALE_USERS = {"shizuka", "ayako"}

def main():
    mapping = yaml.safe_load(MAPPING_FILE.read_text())["users"]
    errors = []
    ok_count = 0

    for name, meta in mapping.items():
        pub_id = meta["public_id"]
        html_path = BASE / "users" / pub_id / "index.html"

        if not html_path.exists():
            print(f"  SKIP {name} ({pub_id}) — not generated yet")
            continue

        content = html_path.read_text()
        has_female_css = FEMALE_MARKER in content
        is_female = name in FEMALE_USERS

        if is_female and not has_female_css:
            errors.append(f"  FAIL {name} ({pub_id}): 女性ユーザーなのに女性CSSなし")
        elif not is_female and has_female_css:
            errors.append(f"  FAIL {name} ({pub_id}): 男性ユーザーに女性CSSが混入")
        else:
            label = "female-css ✓" if is_female else "male-theme ✓"
            print(f"  OK   {name} ({pub_id}): {label}")
            ok_count += 1

    print()
    if errors:
        for e in errors:
            print(e)
        print(f"\n[FAIL] {len(errors)} error(s), {ok_count} passed")
        sys.exit(1)
    else:
        print(f"[PASS] 全{ok_count}ユーザー 性別CSS整合性OK")

if __name__ == "__main__":
    main()
