#!/usr/bin/env python3
"""
Self-Insight LLM Narrative Generator
Cowork mode voice × Extended Thinking for self-insight persona capture.

- Reads: data/users/{name}/profile.yaml + data/persona_voice.yaml
- Outputs: data/users/{name}/insights_llm.json

Extended Thinking:
  With ANTHROPIC_API_KEY set: uses claude-sonnet-4-6 with thinking enabled (budget=8000)
  Without ANTHROPIC_API_KEY: uses lib/ai_router.route() via Claude CLI subprocess

Usage:
    python3 scripts/generate_insight_llm.py --user yuma
    python3 scripts/generate_insight_llm.py --user shizuka --voice data/persona_voice.yaml
    python3 scripts/generate_insight_llm.py --user yuma --dry-run  # show prompt only
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import date

import yaml

# lib/ import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "users"
DEFAULT_VOICE = ROOT / "data" / "persona_voice.yaml"

INSIGHT_SECTIONS = [
    "monthly_theme",
    "strength_activation",
    "challenge_and_reframe",
    "second_quadrant_focus",
]


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_system_prompt(voice: dict) -> str:
    samples = voice.get("authentic_samples", [])
    sample_text = "\n".join(
        f'  [{s["context"]}] {s["text"]}' for s in samples
    )
    forbidden = "\n".join(
        f'  - 「{f["pattern"]}」（{f["reason"]}）'
        for f in voice.get("forbidden_patterns", [])
    )
    models = ", ".join(
        m["name"] for m in voice.get("mental_models", [])
    )
    guidelines = "\n".join(
        f"  - {g}" for g in voice.get("guidelines", [])
    )
    name = voice.get("identity", {}).get("name", "本人")
    strengths = ", ".join(voice.get("strengths_in_voice", []))

    return f"""\
あなたは {name} 自身の視点でセルフインサイトを生成するナレーター。
{name} の声と思考パターンを忠実に再現し、本人が読んで「自分のことだ」と感じるインサイトを出す。

## 思考モデル（自動発火）
{models}

## StrengthsFinder 上位資質
{strengths}

## 禁止パターン
{forbidden}

## 本人の生の語り口（参照）
{sample_text}

## 生成ルール
{guidelines}

## 出力形式
JSON のみ。前置きや解説は不要。以下の構造で返す:
{{
  "monthly_theme": "string — 今月のテーマ（2〜3文）",
  "strength_activation": "string — 今月特に発動する資質とアクション（2文）",
  "challenge_and_reframe": "string — 低調点があれば影響の輪フレームで再解釈（2文）",
  "second_quadrant_focus": "string — 今月の第二領域タスク提案（1文）",
  "generated_at": "YYYY-MM-DD"
}}
"""


def build_analysis_prompt(profile: dict, voice: dict, target_month: int) -> str:
    name = profile.get("identity", {}).get("name", "本人")
    birth_date = profile.get("identity", {}).get("birth_date", "")
    blood_type = profile.get("identity", {}).get("blood_type", "")
    top5 = [s["name"] for s in profile.get("strengths_finder", {}).get("top5", [])]
    mbti = profile.get("personality", {}).get("mbti") or "未計測"
    enneagram = profile.get("personality", {}).get("enneagram", {})
    ennea_type = enneagram.get("type") or enneagram.get("primary") or "未計測"

    fp = profile.get("four_pillars", {})
    dm = fp.get("day_master", {})
    day_master = f"{dm.get('element', '')} {dm.get('yin_yang', '')} ({dm.get('description', '')})"
    missing = fp.get("missing_elements", [])

    nine_star = profile.get("nine_star_ki", {})
    year_star = nine_star.get("year_star", {}).get("name", "")
    month_star = nine_star.get("month_star", {}).get("name", "")

    voice_models = [m["name"] for m in voice.get("mental_models", [])[:3]]

    return f"""\
以下のデータを深く分析して、{name}（{target_month}月）のセルフインサイトを生成してください。

## プロフィール
- 生年月日: {birth_date}  血液型: {blood_type}
- CliftonStrengths Top5: {", ".join(top5)}
- MBTI: {mbti}  エニアグラム: {ennea_type}
- 四柱推命 日主: {day_master}
- 欠如五行: {missing}
- 九星気学 年星: {year_star} / 月星: {month_star}

## 対象月: {target_month}月 ({date.today().year}年)

## 思考モデル（{name}が使う枠組み）
{", ".join(voice_models)}

**タスク**:
上記の占術データと資質を統合し、{target_month}月の行動指針として機能するインサイトを JSON で返してください。
占術データは統計的傾向として扱い、{name}の視点（1人称 or 直接語りかけ）で書く。
"""


def generate_via_api(system: str, prompt: str) -> dict:
    """Uses Anthropic SDK with Extended Thinking if ANTHROPIC_API_KEY is set."""
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        thinking={"type": "enabled", "budget_tokens": 8000},
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end]) if start >= 0 else {}


def generate_via_router(system: str, prompt: str) -> dict:
    """Uses lib/ai_router (Claude CLI subprocess, Max/Pro plan)."""
    from lib.ai_router import route
    full_prompt = f"{system}\n\n---\n\n{prompt}"
    response = route(full_prompt, project="self-insight", task="insight", prefer="claude")
    start = response.find("{")
    end = response.rfind("}") + 1
    if start < 0:
        print(f"[warn] No JSON in response:\n{response[:200]}")
        return {}
    return json.loads(response[start:end])


def generate_insight(user: str, voice_path: Path, dry_run: bool, month: int) -> dict:
    profile_path = DATA_DIR / user / "profile.yaml"
    if not profile_path.exists():
        print(f"[error] profile not found: {profile_path}")
        sys.exit(1)

    profile = load_yaml(profile_path)
    voice = load_yaml(voice_path) if voice_path.exists() else {}

    system = build_system_prompt(voice)
    prompt = build_analysis_prompt(profile, voice, month)

    if dry_run:
        print("=== SYSTEM ===")
        print(system)
        print("\n=== PROMPT ===")
        print(prompt)
        return {}

    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    method = "extended_thinking (API)" if has_api_key else "claude CLI (ai_router)"
    print(f"[generate_insight_llm] user={user} month={month} method={method}")

    if has_api_key:
        try:
            result = generate_via_api(system, prompt)
        except ImportError:
            print("[warn] anthropic SDK not installed, falling back to ai_router")
            result = generate_via_router(system, prompt)
    else:
        result = generate_via_router(system, prompt)

    result["generated_at"] = str(date.today())
    result["method"] = method
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate LLM-powered self-insight narratives")
    parser.add_argument("--user", required=True, help="User name (e.g. yuma, shizuka)")
    parser.add_argument("--voice", default=str(DEFAULT_VOICE), help="persona_voice.yaml path")
    parser.add_argument("--month", type=int, default=date.today().month, help="Target month (1-12)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt only, no API call")
    parser.add_argument("--out", help="Output JSON path (default: data/users/{user}/insights_llm.json)")
    args = parser.parse_args()

    voice_path = Path(args.voice)
    result = generate_insight(args.user, voice_path, args.dry_run, args.month)

    if args.dry_run or not result:
        return

    out_path = Path(args.out) if args.out else DATA_DIR / args.user / "insights_llm.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[done] {out_path}")
    for key, val in result.items():
        if key not in ("generated_at", "method"):
            print(f"\n[{key}]\n{val}")


if __name__ == "__main__":
    main()
