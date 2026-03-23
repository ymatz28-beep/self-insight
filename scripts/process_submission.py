#!/usr/bin/env python3
"""
Process a single Self-Insight form submission.

Usage:
  # From JSON file (e.g., clipboard paste saved to file)
  python3 scripts/process_submission.py --json submission.json

  # With explicit UUID (e.g., from Google Sheet)
  python3 scripts/process_submission.py --json submission.json --uuid abc12345

Pipeline:
  submission JSON → generate_profile.py → profile.yaml → generate_dashboard.py → HTML
"""

import argparse
import json
import subprocess
import sys
import uuid as uuid_mod
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python3"
GENERATE_PROFILE = PROJECT_ROOT / "generate_profile.py"
GENERATE_DASHBOARD = PROJECT_ROOT / "generate_dashboard.py"
USERS_DIR = PROJECT_ROOT / "users"


def process_submission(data: dict, user_uuid: str = None) -> dict:
    """Process a single submission JSON through the full pipeline."""

    if not user_uuid:
        user_uuid = str(uuid_mod.uuid4())[:8]

    identity = data.get("identity", {})
    display_name = identity.get("display_name", "unknown")
    birth_date = identity.get("birth_date", "")
    blood_type = identity.get("blood_type", "")
    tier = data.get("tier", 1)

    if not birth_date or not blood_type:
        return {"success": False, "error": "Missing birth_date or blood_type"}

    # Create user directory
    user_dir = USERS_DIR / user_uuid
    user_dir.mkdir(parents=True, exist_ok=True)

    # Save raw submission
    raw_path = user_dir / "submission.json"
    raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Build generate_profile.py args (matches actual CLI: --tier2-answers JSON, --tier3-answers JSON, --existing JSON)
    profile_path = user_dir / "profile.yaml"
    profile_cmd = [
        str(VENV_PYTHON), str(GENERATE_PROFILE),
        "--name", display_name,
        "--birth-date", birth_date,
        "--blood-type", blood_type,
        "--output", str(profile_path),
    ]

    # Optional identity fields
    sex = identity.get("sex")
    if sex and sex != "other":
        profile_cmd.extend(["--sex", sex])
    birth_time = identity.get("birth_time")
    if birth_time:
        profile_cmd.extend(["--birth-time", birth_time])
    birth_place = identity.get("birth_place")
    if birth_place:
        profile_cmd.extend(["--birth-place", birth_place])

    # Tier 2: enneagram + hsp + adhd as single JSON
    if tier >= 2:
        tier2 = {}
        ennea = data.get("enneagram", {})
        if ennea.get("top3"):
            tier2["enneagram"] = [
                ennea["top3"][0] if ennea["top3"] else None,
                ennea.get("wing"),
                str(ennea.get("stress")) if ennea.get("stress") is not None else None,
            ]
        hsp = data.get("hsp", [])
        if hsp and all(v is not None for v in hsp):
            tier2["hsp"] = hsp
        adhd = data.get("adhd", [])
        if adhd and all(v is not None for v in adhd):
            tier2["adhd"] = adhd
        if tier2:
            profile_cmd.extend(["--tier2-answers", json.dumps(tier2)])

    # Tier 3: Big Five 20-item as JSON array
    if tier >= 3:
        bf = data.get("big_five", [])
        if bf and all(v is not None for v in bf):
            profile_cmd.extend(["--tier3-answers", json.dumps(bf)])

        existing = data.get("existing", {})
        if existing and any(existing.get(k) for k in ("mbti", "clifton_top5", "enneagram_known")):
            profile_cmd.extend(["--existing", json.dumps(existing)])

    # Step 1: Generate profile
    print(f"[1/2] Generating profile for {display_name} (Tier {tier})...")
    result = subprocess.run(profile_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        return {"success": False, "error": f"generate_profile failed: {result.stderr}"}

    # Step 2: Generate dashboard
    output_path = user_dir / "index.html"
    dashboard_cmd = [
        str(VENV_PYTHON), str(GENERATE_DASHBOARD),
        "--profile", str(profile_path),
        "--output", str(output_path),
        "--tier", str(tier),
    ]

    print(f"[2/2] Generating dashboard...")
    result = subprocess.run(dashboard_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        return {"success": False, "error": f"generate_dashboard failed: {result.stderr}"}

    # Build result URL
    url = f"https://ymatz28-beep.github.io/self-insight/users/{user_uuid}/"

    return {
        "success": True,
        "uuid": user_uuid,
        "display_name": display_name,
        "tier": tier,
        "profile_path": str(profile_path),
        "output_path": str(output_path),
        "url": url,
    }


def main():
    parser = argparse.ArgumentParser(description="Process Self-Insight form submissions")
    parser.add_argument("--json", type=str, help="Path to submission JSON file")
    parser.add_argument("--uuid", type=str, help="User UUID (auto-generated if omitted)")
    args = parser.parse_args()

    if args.json:
        data = json.loads(Path(args.json).read_text())
        result = process_submission(data, args.uuid)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["success"]:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
