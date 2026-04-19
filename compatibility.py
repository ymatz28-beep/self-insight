#!/usr/bin/env python3
"""
Self-Insight Compatibility Engine
Calculates compatibility between two profiles using 5 divination/psychology axes.

Usage:
    python3 compatibility.py --profile1 data/users/yuma/profile.yaml \
                             --profile2 data/users/other/profile.yaml \
                             --output result.yaml

    # Or from birth dates directly (no profile files needed):
    python3 compatibility.py \
        --person1-name "Yuma" --person1-birth "1975-10-28" --person1-blood AB \
        --person2-name "Hana" --person2-birth "1990-05-15" --person2-blood A \
        --output result.yaml
"""

import argparse
import datetime
import json
import math
import os
import sys

import yaml


# ============================================================
# Constants — Five Elements Relationships
# ============================================================

ELEMENT_JP = {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"}
ELEMENT_EN = {v: k for k, v in ELEMENT_JP.items()}

# 相生 (Sōsei / Nurturing cycle): Wood→Fire→Earth→Metal→Water→Wood
# Each element nurtures the next one in this cycle.
SOSEI_CYCLE = ["Wood", "Fire", "Earth", "Metal", "Water"]  # each nurtures the next

# 相剋 (Sōkoku / Controlling cycle): Wood→Earth→Water→Fire→Metal→Wood
SOKOKU_CYCLE = ["Wood", "Earth", "Water", "Fire", "Metal"]  # each controls the next

def _five_element_relationship(a: str, b: str) -> str:
    """
    Returns the relationship FROM a TO b:
      'nurtures'   — a generates b (相生, forward)
      'nurtured'   — b generates a (相生, reverse)
      'controls'   — a controls b (相剋, forward)
      'controlled' — b controls a (相剋, reverse)
      'same'       — identical element
    """
    if a == b:
        return "same"
    ai = SOSEI_CYCLE.index(a)
    # Check 相生 forward: a nurtures b
    if SOSEI_CYCLE[(ai + 1) % 5] == b:
        return "nurtures"
    # Check 相生 reverse: b nurtures a
    if SOSEI_CYCLE[(ai - 1) % 5] == b:
        return "nurtured"
    # Check 相剋 forward: a controls b
    ki = SOKOKU_CYCLE.index(a)
    if SOKOKU_CYCLE[(ki + 1) % 5] == b:
        return "controls"
    # Check 相剋 reverse: b controls a
    if SOKOKU_CYCLE[(ki - 1) % 5] == b:
        return "controlled"
    return "neutral"


# ============================================================
# Constants — Nine Star Ki
# ============================================================

NINE_STAR_NAMES = {
    1: "一白水星", 2: "二黒土星", 3: "三碧木星", 4: "四緑木星",
    5: "五黄土星", 6: "六白金星", 7: "七赤金星", 8: "八白土星", 9: "九紫火星",
}
NINE_STAR_ELEMENTS = {
    1: "Water", 2: "Earth", 3: "Wood", 4: "Wood", 5: "Earth",
    6: "Metal", 7: "Metal", 8: "Earth", 9: "Fire",
}

# Star number groups for nine star ki compatibility
# Stars of the same element group have natural affinity
NINE_STAR_GROUPS = {
    "Water": [1],
    "Earth": [2, 5, 8],
    "Wood": [3, 4],
    "Metal": [6, 7],
    "Fire": [9],
}


# ============================================================
# Constants — Rokusei
# ============================================================

ROKUSEI_STARS = {
    1: "土星人", 2: "金星人", 3: "火星人",
    4: "天王星人", 5: "木星人", 6: "水星人",
}
ROKUSEI_SUB_MAP = {
    "土星人": "天王星人", "金星人": "木星人", "火星人": "水星人",
    "天王星人": "土星人", "木星人": "金星人", "水星人": "火星人",
}

# Complementary star pairs (balanced chemistry)
ROKUSEI_COMPLEMENTARY = [
    {"土星人", "木星人"},
    {"金星人", "火星人"},
    {"天王星人", "水星人"},
]

# Enneagram compatibility matrix — known well-aligned pairs
# (type_a, type_b): compatibility_modifier (-20 to +20)
ENNEAGRAM_COMPAT = {
    (1, 7): 15,  (1, 2): 10, (1, 9): 10, (1, 4): -5,
    (2, 8): 15,  (2, 4): 10, (2, 6): 10,
    (3, 9): 10,  (3, 6): 5,
    (4, 9): 15,  (4, 5): 10, (4, 1): -5,
    (5, 9): 15,  (5, 8): 10, (5, 4): 10,
    (6, 9): 15,  (6, 2): 10, (6, 3): 5,
    (7, 2): 10,  (7, 9): 10, (7, 1): 15,
    (8, 2): 15,  (8, 4): -5, (8, 9): 10,
    (9, 4): 15,  (9, 5): 15, (9, 6): 15, (9, 7): 10,
}


# ============================================================
# Profile Loading
# ============================================================

def load_profile(path: str) -> dict:
    """Load a profile.yaml file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def profile_from_birth(name: str, birth_date: str, blood_type: str) -> dict:
    """
    Build a minimal profile dict from birth date only (no YAML file needed).
    Imports and reuses generate_profile.py calculations.
    """
    # Add self-insight directory to path so we can import generate_profile
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    import generate_profile as gp

    bd = datetime.date.fromisoformat(birth_date)
    y, m, d = bd.year, bd.month, bd.day
    forecast_year = datetime.date.today().year

    return {
        "identity": {
            "name": name,
            "birth_date": birth_date,
            "blood_type": blood_type.upper(),
        },
        "personality": {},
        "four_pillars": gp.calc_four_pillars(y, m, d),
        "nine_star_ki": gp.calc_nine_star_ki(y, m, d, forecast_year),
        "rokusei": gp.calc_rokusei(y, m, d, forecast_year),
        "western_astrology": gp.calc_western_astrology(m, d),
        "blood_type": gp.calc_blood_type(blood_type),
    }


# ============================================================
# Axis A: 五行相性 (Five Elements Compatibility) — Weight 30%
# ============================================================

def score_five_elements(p1: dict, p2: dict) -> dict:
    """
    Five Elements compatibility (五行相性).

    Two sub-scores:
    1. Day master relationship — the core identity element pairing.
       相生 (nurture): +25 pts | Same: +15 | 相剋 (control): -5 | Neutral: +10
    2. Overall element balance cosine similarity (0-100).
       Compare the percentage distributions of all 5 elements.

    Final = 0.6 * day_master_score + 0.4 * balance_similarity
    """
    fp1 = p1.get("four_pillars", {})
    fp2 = p2.get("four_pillars", {})

    dm1 = fp1.get("day_master", {}).get("element", "Fire")
    dm2 = fp2.get("day_master", {}).get("element", "Fire")

    # --- Day master score (0-100) ---
    rel = _five_element_relationship(dm1, dm2)
    dm_score_map = {
        "nurtures": 85,    # A generates B — supportive, energising
        "nurtured": 80,    # B generates A — feels supported
        "same": 65,        # Same element — deep understanding, possible ego clash
        "controls": 40,    # A dominates B — strong but potentially oppressive
        "controlled": 50,  # B dominates A — challenging dynamic
        "neutral": 60,     # Opposite across the cycle
    }
    dm_score = dm_score_map[rel]

    # Narrative for day master
    rel_descriptions = {
        "nurtures": f"{ELEMENT_JP[dm1]}があなたを育てます。一方的ではなく、活力を与え合う相生の関係",
        "nurtured": f"相手の{ELEMENT_JP[dm2]}があなたの{ELEMENT_JP[dm1]}を育てます。包まれるような安心感",
        "same": f"同じ{ELEMENT_JP[dm1]}の日主。深い共感と価値観の一致。競争・嫉妬に注意",
        "controls": f"あなたの{ELEMENT_JP[dm1]}が相手の{ELEMENT_JP[dm2]}を制御。リーダーシップと摩擦が共存",
        "controlled": f"相手の{ELEMENT_JP[dm2]}があなたの{ELEMENT_JP[dm1]}を抑制。刺激的だが長期的な抑圧に注意",
        "neutral": f"{ELEMENT_JP[dm1]}と{ELEMENT_JP[dm2]}の中立的関係。安定しているが劇的な化学反応は少ない",
    }

    # --- Five element balance cosine similarity ---
    elements_order = ["木", "火", "土", "金", "水"]
    bal1 = fp1.get("five_elements_balance", {})
    bal2 = fp2.get("five_elements_balance", {})

    vec1 = [bal1.get(el, {}).get("pct", 0) for el in elements_order]
    vec2 = [bal2.get(el, {}).get("pct", 0) for el in elements_order]

    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a**2 for a in vec1)) or 1
    mag2 = math.sqrt(sum(b**2 for b in vec2)) or 1
    cosine_sim = dot / (mag1 * mag2)  # 0..1
    balance_score = round(cosine_sim * 100)

    # Missing element complement bonus:
    # If one person lacks an element that the other has, they fill each other's gaps
    missing1 = set(fp1.get("missing_elements", []))
    missing2 = set(fp2.get("missing_elements", []))
    balance_bonus = 0
    complement_elements = []

    for el_jp in elements_order:
        el_en = ELEMENT_EN.get(el_jp, el_jp)
        in_1 = el_jp not in missing1
        in_2 = el_jp not in missing2
        if (not in_1 and in_2) or (in_1 and not in_2):
            # One has it, other lacks it → complementary
            balance_bonus += 5
            complement_elements.append(el_jp)

    balance_score = min(100, balance_score + balance_bonus)

    # Weighted final
    final = round(0.6 * dm_score + 0.4 * balance_score)

    return {
        "score": final,
        "day_master_1": dm1,
        "day_master_2": dm2,
        "relationship": rel,
        "day_master_score": dm_score,
        "balance_score": balance_score,
        "complement_elements": complement_elements,
        "narrative": rel_descriptions[rel],
    }


# ============================================================
# Axis B: 九星気学相性 (Nine Star Ki Compatibility) — Weight 25%
# ============================================================

def score_nine_star_ki(p1: dict, p2: dict) -> dict:
    """
    Nine Star Ki compatibility (九星気学相性).

    Factors:
    1. Year star element relationship (relative to 相生 / 相剋)
    2. Same element group = high affinity
    3. Same star number = deep understanding but possible friction

    Score breakdown:
    - Same star: 60 (mutual understanding but mirroring conflicts)
    - Same element group: 80
    - 相生 (nurturing): 85
    - 相剋 (controlling): 40
    - Neutral: 60
    """
    nsk1 = p1.get("nine_star_ki", {})
    nsk2 = p2.get("nine_star_ki", {})

    star1 = nsk1.get("year_star", {}).get("number", 5)
    star2 = nsk2.get("year_star", {}).get("number", 5)
    el1 = NINE_STAR_ELEMENTS.get(star1, "Earth")
    el2 = NINE_STAR_ELEMENTS.get(star2, "Earth")

    name1 = NINE_STAR_NAMES.get(star1, "")
    name2 = NINE_STAR_NAMES.get(star2, "")

    same_star = star1 == star2

    # Find element groups
    group1 = next((g for g, nums in NINE_STAR_GROUPS.items() if star1 in nums), None)
    group2 = next((g for g, nums in NINE_STAR_GROUPS.items() if star2 in nums), None)
    same_group = group1 == group2

    rel = _five_element_relationship(el1, el2)

    if same_star:
        score = 62
        desc = f"同じ{name1}同士。価値観が非常に近く、すぐに理解し合える。一方で同じ弱点を持ち、盲点が生じやすい"
    elif same_group:
        score = 80
        desc = f"{name1}と{name2}は同じ{ELEMENT_JP.get(el1, el1)}グループ。感性と生きるテンポが自然に合う"
    elif rel in ("nurtures", "nurtured"):
        score = 82
        rel_jp = "相生" if rel == "nurtures" else "逆相生"
        desc = f"{rel_jp}の関係。{name1}と{name2}は互いを高め合うエネルギーを持つ"
    elif rel in ("controls", "controlled"):
        score = 42
        rel_jp = "相剋" if rel == "controls" else "逆相剋"
        desc = f"{rel_jp}の関係。{name1}と{name2}の間には緊張感がある。成長の触媒にもなりうるが、長期的な摩擦に注意"
    else:
        score = 60
        desc = f"{name1}と{name2}は中立的な関係。特別な化学反応はないが安定している"

    # Month star as a modifier (softens or amplifies the year star result)
    ms1 = nsk1.get("month_star", {}).get("number", 5)
    ms2 = nsk2.get("month_star", {}).get("number", 5)
    ms_el1 = NINE_STAR_ELEMENTS.get(ms1, "Earth")
    ms_el2 = NINE_STAR_ELEMENTS.get(ms2, "Earth")
    ms_rel = _five_element_relationship(ms_el1, ms_el2)
    month_bonus = 8 if ms_rel in ("nurtures", "nurtured", "same") else (-5 if ms_rel in ("controls", "controlled") else 0)
    score = max(0, min(100, score + month_bonus))

    return {
        "score": score,
        "star_1": {"number": star1, "name": name1, "element": el1},
        "star_2": {"number": star2, "name": name2, "element": el2},
        "relationship": rel,
        "same_group": same_group,
        "same_star": same_star,
        "narrative": desc,
    }


# ============================================================
# Axis C: 六星占術相性 (Rokusei Compatibility) — Weight 15%
# ============================================================

def score_rokusei(p1: dict, p2: dict) -> dict:
    """
    Rokusei Senjutsu compatibility (六星占術相性).

    Factors:
    1. Same main star: deep resonance, but both share identical strengths/blind spots
    2. Complementary stars (known pairs): balanced chemistry
    3. Both reigou (霊合星人): rare, very deep connection with wide energy swings
    4. 殺界 alignment: if both are in 大殺界 simultaneously, very difficult period
    """
    r1 = p1.get("rokusei", {})
    r2 = p2.get("rokusei", {})

    ms1 = r1.get("main_star", {}).get("name", "")
    ms2 = r2.get("main_star", {}).get("name", "")
    reigou1 = r1.get("reigou", False)
    reigou2 = r2.get("reigou", False)

    same_star = ms1 == ms2
    both_reigou = reigou1 and reigou2

    # Check complementary pair
    is_complementary = any(ms1 in pair and ms2 in pair for pair in ROKUSEI_COMPLEMENTARY)

    # Check sub-star match (if either is reigou, check if main matches sub)
    sub_match = False
    if reigou1:
        sub1 = ROKUSEI_SUB_MAP.get(ms1, "")
        if sub1 == ms2:
            sub_match = True
    if reigou2:
        sub2 = ROKUSEI_SUB_MAP.get(ms2, "")
        if sub2 == ms1:
            sub_match = True

    # Check current year 殺界 alignment
    def _current_satsukai(rokusei: dict) -> str | None:
        for entry in rokusei.get("twelve_year_cycle", []):
            if entry.get("current"):
                return entry.get("殺界") or entry.get("satsukai")
        return None

    satsukai1 = _current_satsukai(r1)
    satsukai2 = _current_satsukai(r2)
    both_daisakukai = satsukai1 == "大殺界" and satsukai2 == "大殺界"

    # --- Score ---
    if both_reigou and same_star:
        score = 70  # Extraordinary resonance, but volatility is doubled
        desc = f"両者とも{ms1}の霊合星人。極めて稀な深い共鳴。運気の振れ幅が非常に大きく、好調期は最高潮、不調期は深い影響を受ける"
    elif both_reigou:
        score = 72
        desc = f"二人とも霊合星人。互いの二面性を理解し合える稀有な関係。エネルギーの振れ幅が大きいため、お互いの波をうまく合わせることが重要"
    elif same_star:
        score = 65
        desc = f"同じ{ms1}同士。価値観・行動パターンが非常に似ており、すぐに打ち解ける。同じ弱点を持つため、盲点の補完が課題"
    elif is_complementary:
        score = 80
        desc = f"{ms1}と{ms2}は補完的な星のペア。お互いの違いが強みとなり、バランスのとれた関係を築きやすい"
    elif sub_match:
        score = 78
        desc = f"霊合のサブ星がメイン星と一致。霊合星人の多面的な性質が相手の核と共鳴する特殊な相性"
    else:
        score = 55
        desc = f"{ms1}と{ms2}の組み合わせ。標準的な相性。深い接点を意識的に作ることで関係が深まる"

    # 大殺界ペナルティ: 同時に最悪期なら注意
    satsukai_note = None
    if both_daisakukai:
        score = max(20, score - 20)
        satsukai_note = "現在両者とも大殺界。新しいことを始めるより、互いを支え合う時期。重大な決断は避けること"
    elif satsukai1 == "大殺界":
        score = max(30, score - 8)
        satsukai_note = f"{p1.get('identity', {}).get('name', 'あなた')}が大殺界中。相手からのサポートが特に重要な時期"
    elif satsukai2 == "大殺界":
        score = max(30, score - 8)
        satsukai_note = f"{p2.get('identity', {}).get('name', '相手')}が大殺界中。相手を支えることに集中する時期"

    return {
        "score": score,
        "star_1": {"name": ms1, "reigou": reigou1},
        "star_2": {"name": ms2, "reigou": reigou2},
        "same_star": same_star,
        "complementary": is_complementary,
        "both_reigou": both_reigou,
        "satsukai_1": satsukai1,
        "satsukai_2": satsukai2,
        "satsukai_note": satsukai_note,
        "narrative": desc,
    }


# ============================================================
# Axis D: 西洋占星術相性 (Western Astrology) — Weight 15%
# ============================================================

# Astrology sign index (0=Aries ... 11=Pisces)
SIGN_INDEX = {
    "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
    "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
    "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11,
}

SIGN_JP = {
    "Aries": "牡羊座", "Taurus": "牡牛座", "Gemini": "双子座", "Cancer": "蟹座",
    "Leo": "獅子座", "Virgo": "乙女座", "Libra": "天秤座", "Scorpio": "蠍座",
    "Sagittarius": "射手座", "Capricorn": "山羊座", "Aquarius": "水瓶座", "Pisces": "魚座",
}

# Compatible element pairs for western astrology:
# Fire-Air = sextile chemistry | Earth-Water = sextile chemistry
WESTERN_COMPAT_ELEMENTS = {
    frozenset({"Fire", "Air"}): ("sextile", 75),
    frozenset({"Earth", "Water"}): ("sextile", 75),
    frozenset({"Fire", "Fire"}): ("trine", 85),
    frozenset({"Earth", "Earth"}): ("trine", 85),
    frozenset({"Air", "Air"}): ("trine", 85),
    frozenset({"Water", "Water"}): ("trine", 85),
    frozenset({"Fire", "Earth"}): ("square", 35),
    frozenset({"Fire", "Water"}): ("square", 40),
    frozenset({"Air", "Earth"}): ("square", 38),
    frozenset({"Air", "Water"}): ("square", 35),
}


def score_western_astrology(p1: dict, p2: dict) -> dict:
    """
    Western astrology sun sign compatibility.

    Aspect calculation based on sign position:
    - Trine (120°, same element): +30 → score ~85
    - Sextile (60°, compatible elements Fire-Air, Earth-Water): +20 → score ~75
    - Conjunction (0°, same sign): +20 → score ~70 (resonance + friction)
    - Opposition (180°, complementary polarity): +10 → score ~65
    - Square (90°, challenging): -10 → score ~35-40
    """
    wa1 = p1.get("western_astrology", {})
    wa2 = p2.get("western_astrology", {})

    sign1_data = wa1.get("sun_sign", {})
    sign2_data = wa2.get("sun_sign", {})

    sign1 = sign1_data.get("sign", "Aries")
    sign2 = sign2_data.get("sign", "Aries")
    el1 = sign1_data.get("element", "Fire")
    el2 = sign2_data.get("element", "Fire")

    idx1 = SIGN_INDEX.get(sign1, 0)
    idx2 = SIGN_INDEX.get(sign2, 0)
    diff = abs(idx1 - idx2)
    if diff > 6:
        diff = 12 - diff  # use shorter arc

    # Determine aspect
    if diff == 0:
        aspect = "conjunction"
        score = 68
        desc = f"同じ{SIGN_JP.get(sign1, sign1)}同士。強い共感と価値観の一致。鏡のような関係で摩擦も起きやすい"
    elif diff == 4:  # 120°
        aspect = "trine"
        score = 85
        desc = f"{SIGN_JP.get(sign1, sign1)}×{SIGN_JP.get(sign2, sign2)}はトライン（120°）。同じ{el1}エレメントの自然な調和。一緒にいて疲れない"
    elif diff == 2:  # 60°
        aspect = "sextile"
        key = frozenset({el1, el2})
        _, base = WESTERN_COMPAT_ELEMENTS.get(key, ("sextile", 65))
        score = base
        desc = f"{SIGN_JP.get(sign1, sign1)}×{SIGN_JP.get(sign2, sign2)}はセクスタイル（60°）。{el1}と{el2}の相性は良く、互いの違いが刺激になる"
    elif diff == 6:  # 180°
        aspect = "opposition"
        score = 62
        desc = f"{SIGN_JP.get(sign1, sign1)}×{SIGN_JP.get(sign2, sign2)}はオポジション（180°）。引き合う対極同士。強い吸引力があり、学び合いが多い"
    elif diff == 3:  # 90°
        aspect = "square"
        score = 38
        desc = f"{SIGN_JP.get(sign1, sign1)}×{SIGN_JP.get(sign2, sign2)}はスクエア（90°）。緊張感のある組み合わせ。摩擦が成長を促すが消耗しやすい"
    else:
        # Semi-sextile (30°) or quincunx (150°)
        key = frozenset({el1, el2})
        aspect_type, base = WESTERN_COMPAT_ELEMENTS.get(key, ("neutral", 58))
        aspect = aspect_type
        score = max(38, min(80, base - 5))
        desc = f"{SIGN_JP.get(sign1, sign1)}×{SIGN_JP.get(sign2, sign2)}の組み合わせ。{el1}と{el2}の関係性が相性の核"

    return {
        "score": score,
        "sign_1": {"sign": sign1, "element": el1, "jp": SIGN_JP.get(sign1, sign1)},
        "sign_2": {"sign": sign2, "element": el2, "jp": SIGN_JP.get(sign2, sign2)},
        "aspect": aspect,
        "element_1": el1,
        "element_2": el2,
        "narrative": desc,
    }


# ============================================================
# Axis E: 性格相性 (Personality Compatibility) — Weight 15%
# ============================================================

def score_personality(p1: dict, p2: dict) -> dict | None:
    """
    Personality compatibility — only scored if both have Tier 2+ data.

    Sub-axes:
    1. Big Five complementarity — opposite Extraversion/Introversion pairs,
       similar Agreeableness/Openness.
    2. Enneagram compatibility (known pairs from ENNEAGRAM_COMPAT table).
    3. HSP note — if one person is high HSP, communication considerations apply.

    Returns None if neither profile has personality data.
    """
    pers1 = p1.get("personality", {})
    pers2 = p2.get("personality", {})

    has_data = bool(pers1 or pers2)
    if not has_data:
        return None

    scores = []
    notes = []

    # --- Enneagram ---
    enn1 = pers1.get("enneagram", {})
    enn2 = pers2.get("enneagram", {})
    enn_score = None

    if enn1 and enn2:
        t1 = enn1.get("type")
        t2 = enn2.get("type")
        if t1 and t2:
            key = (min(t1, t2), max(t1, t2))
            modifier = ENNEAGRAM_COMPAT.get(key, ENNEAGRAM_COMPAT.get((t2, t1), 0))
            enn_score = min(100, max(0, 60 + modifier))
            t1_name = enn1.get("name", f"タイプ{t1}")
            t2_name = enn2.get("name", f"タイプ{t2}")
            if modifier > 10:
                enn_note = f"エニアグラム{t1}（{t1_name}）×{t2}（{t2_name}）は相性の良いペア"
            elif modifier < -10:
                enn_note = f"エニアグラム{t1}×{t2}は価値観の摩擦が生じやすい組み合わせ"
            else:
                enn_note = f"エニアグラム{t1}×{t2}は標準的な相性"
            notes.append(enn_note)
            scores.append(enn_score)

    # --- Big Five ---
    bf1 = pers1.get("big_five", {})
    bf2 = pers2.get("big_five", {})
    bf_score = None

    if bf1 and bf2:
        # Extraversion complementarity: one high (≥15), one low (≤9) = balanced team
        ext1 = bf1.get("Extraversion", 12)
        ext2 = bf2.get("Extraversion", 12)
        ext_diff = abs(ext1 - ext2)
        if ext_diff >= 6:
            ext_score = 80  # complementary E/I pair
            notes.append("外向性と内向性が補完的なペア。エネルギーのバランスが取れている")
        elif ext_diff <= 2:
            ext_score = 70  # similar level
        else:
            ext_score = 65

        # Agreeableness alignment: similar = harmonious
        ag1 = bf1.get("Agreeableness", 12)
        ag2 = bf2.get("Agreeableness", 12)
        ag_diff = abs(ag1 - ag2)
        ag_score = 80 if ag_diff <= 3 else 60 if ag_diff <= 6 else 40

        # Openness alignment
        op1 = bf1.get("Openness", 12)
        op2 = bf2.get("Openness", 12)
        op_diff = abs(op1 - op2)
        op_score = 80 if op_diff <= 3 else 65 if op_diff <= 6 else 50

        bf_score = round((ext_score * 0.4 + ag_score * 0.3 + op_score * 0.3))
        scores.append(bf_score)

    # --- HSP awareness ---
    hsp1 = pers1.get("hsp", {})
    hsp2 = pers2.get("hsp", {})
    hsp_note = None

    if hsp1 or hsp2:
        h1_level = hsp1.get("score", "medium") if hsp1 else "medium"
        h2_level = hsp2.get("score", "medium") if hsp2 else "medium"
        if h1_level == "high" and h2_level == "high":
            hsp_note = "両者ともHSP傾向が高い。お互いの繊細さを理解できる反面、刺激の多い環境では共に消耗しやすい"
            scores.append(75)  # good mutual understanding
        elif h1_level == "high" or h2_level == "high":
            hsp_note = "一方がHSP傾向。繊細な感受性への理解と配慮が良好な関係の鍵"
            scores.append(65)

    if not scores:
        return None

    final_score = round(sum(scores) / len(scores))

    return {
        "score": final_score,
        "enneagram_score": enn_score,
        "big_five_score": bf_score,
        "notes": notes,
        "hsp_note": hsp_note,
        "narrative": "。".join(notes) if notes else "性格データに基づく相性スコア",
    }


# ============================================================
# Weighted Total & Narrative Generation
# ============================================================

AXIS_WEIGHTS = {
    "five_elements": 0.30,
    "nine_star_ki": 0.25,
    "rokusei": 0.15,
    "western_astrology": 0.15,
    "personality": 0.15,
}

# Weight redistribution when personality data is absent
AXIS_WEIGHTS_NO_PERSONALITY = {
    "five_elements": 0.35,
    "nine_star_ki": 0.30,
    "rokusei": 0.175,
    "western_astrology": 0.175,
}


def _compatibility_label(score: int) -> dict:
    """Return a label and emoji for a given total score."""
    if score >= 85:
        return {"label": "運命的な縁", "level": "exceptional", "color": "#c9a84c"}
    elif score >= 75:
        return {"label": "非常に相性が良い", "level": "high", "color": "var(--accent-green)"}
    elif score >= 60:
        return {"label": "相性は良好", "level": "good", "color": "#6366f1"}
    elif score >= 45:
        return {"label": "補完的な関係", "level": "moderate", "color": "#eab308"}
    elif score >= 30:
        return {"label": "努力が必要な相性", "level": "challenging", "color": "#ff6b35"}
    else:
        return {"label": "成長の機会が多い関係", "level": "difficult", "color": "var(--accent-red)"}


def calculate_compatibility(p1: dict, p2: dict) -> dict:
    """
    Main compatibility calculation. Combines all 5 axes.

    Returns a full compatibility report dict.
    """
    name1 = p1.get("identity", {}).get("name", "Person A")
    name2 = p2.get("identity", {}).get("name", "Person B")

    # Calculate each axis
    axis_fe = score_five_elements(p1, p2)
    axis_nsk = score_nine_star_ki(p1, p2)
    axis_rk = score_rokusei(p1, p2)
    axis_wa = score_western_astrology(p1, p2)
    axis_pers = score_personality(p1, p2)

    # Weighted total
    if axis_pers is not None:
        weights = AXIS_WEIGHTS
        total = (
            axis_fe["score"] * weights["five_elements"] +
            axis_nsk["score"] * weights["nine_star_ki"] +
            axis_rk["score"] * weights["rokusei"] +
            axis_wa["score"] * weights["western_astrology"] +
            axis_pers["score"] * weights["personality"]
        )
    else:
        weights = AXIS_WEIGHTS_NO_PERSONALITY
        total = (
            axis_fe["score"] * weights["five_elements"] +
            axis_nsk["score"] * weights["nine_star_ki"] +
            axis_rk["score"] * weights["rokusei"] +
            axis_wa["score"] * weights["western_astrology"]
        )

    total_score = round(total)

    # Identify best and growth axes
    axes_scored = {
        "five_elements": axis_fe["score"],
        "nine_star_ki": axis_nsk["score"],
        "rokusei": axis_rk["score"],
        "western_astrology": axis_wa["score"],
    }
    if axis_pers:
        axes_scored["personality"] = axis_pers["score"]

    sorted_axes = sorted(axes_scored.items(), key=lambda x: x[1], reverse=True)
    best_axes = [a for a, _ in sorted_axes[:2]]
    growth_axes = [a for a, _ in sorted_axes[-1:]]

    axis_labels = {
        "five_elements": "五行相性",
        "nine_star_ki": "九星気学",
        "rokusei": "六星占術",
        "western_astrology": "西洋占星術",
        "personality": "性格相性",
    }

    label_info = _compatibility_label(total_score)

    return {
        "meta": {
            "generated": datetime.date.today().isoformat(),
            "person_1": name1,
            "person_2": name2,
        },
        "total_score": total_score,
        "label": label_info["label"],
        "level": label_info["level"],
        "best_axes": [axis_labels[a] for a in best_axes],
        "growth_axes": [axis_labels[a] for a in growth_axes],
        "axes": {
            "five_elements": {
                "label": "五行相性",
                "weight_pct": 30,
                "score": axis_fe["score"],
                **axis_fe,
            },
            "nine_star_ki": {
                "label": "九星気学相性",
                "weight_pct": 25,
                "score": axis_nsk["score"],
                **axis_nsk,
            },
            "rokusei": {
                "label": "六星占術相性",
                "weight_pct": 15,
                "score": axis_rk["score"],
                **axis_rk,
            },
            "western_astrology": {
                "label": "西洋占星術相性",
                "weight_pct": 15,
                "score": axis_wa["score"],
                **axis_wa,
            },
            "personality": {
                "label": "性格相性",
                "weight_pct": 15,
                **(axis_pers if axis_pers else {"score": None, "narrative": "Tier 2以上のデータが必要です"}),
            },
        },
    }


# ============================================================
# YAML Output
# ============================================================

class CompatibilityDumper(yaml.Dumper):
    pass


def _str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _none_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "null")


CompatibilityDumper.add_representer(str, _str_representer)
CompatibilityDumper.add_representer(type(None), _none_representer)


def write_result(result: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        n1 = result["meta"]["person_1"]
        n2 = result["meta"]["person_2"]
        f.write(f"# Self-Insight Compatibility Report — {n1} × {n2}\n")
        f.write(f"# Generated: {result['meta']['generated']}\n\n")
        yaml.dump(
            result, f,
            Dumper=CompatibilityDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )
    print(f"Compatibility report written to {output_path}")
    print(f"Total score: {result['total_score']}/100 — {result['label']}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Self-Insight Compatibility Engine")

    # Option A: Profile YAML files
    parser.add_argument("--profile1", help="Path to Person A's profile.yaml")
    parser.add_argument("--profile2", help="Path to Person B's profile.yaml")

    # Option B: Birth dates directly
    parser.add_argument("--person1-name")
    parser.add_argument("--person1-birth", help="YYYY-MM-DD")
    parser.add_argument("--person1-blood", help="A/B/O/AB")
    parser.add_argument("--person2-name")
    parser.add_argument("--person2-birth", help="YYYY-MM-DD")
    parser.add_argument("--person2-blood", help="A/B/O/AB")

    parser.add_argument("--output", required=True, help="Output YAML path")

    args = parser.parse_args()

    # Load profiles
    if args.profile1 and args.profile2:
        p1 = load_profile(args.profile1)
        p2 = load_profile(args.profile2)
    elif all([args.person1_birth, args.person2_birth]):
        p1 = profile_from_birth(
            args.person1_name or "Person A",
            args.person1_birth,
            args.person1_blood or "O",
        )
        p2 = profile_from_birth(
            args.person2_name or "Person B",
            args.person2_birth,
            args.person2_blood or "O",
        )
    else:
        parser.error("Provide either --profile1 + --profile2, or --person1-birth + --person2-birth")

    result = calculate_compatibility(p1, p2)
    write_result(result, args.output)


if __name__ == "__main__":
    main()
