#!/usr/bin/env python3
"""
Self-Insight Profile Generator
Calculates personality + divination profile from birth data + questionnaire answers.
Output: profile.yaml

Usage:
    python3 generate_profile.py --name "タロウ" --birth-date "1990-05-15" --blood-type A \
      [--birth-time "14:30"] [--sex male] [--birth-place "東京都"] \
      [--tier2-answers '{"enneagram":[4,"3w4","1"],"hsp":[4,3,5,2,4,3],"adhd":[2,3,1,2,4,1]}'] \
      [--tier3-answers '[3,4,2,5,1,4,3,2,5,1,3,4,2,5,1,4,3,2,5,1]'] \
      [--existing '{"mbti":"INTJ"}'] \
      --output data/users/tarou/profile.yaml
"""

import argparse
import datetime
import json
import math
import os
import sys

import yaml


# ============================================================
# Constants
# ============================================================

HEAVENLY_STEMS = list("甲乙丙丁戊己庚辛壬癸")
EARTHLY_BRANCHES = list("子丑寅卯辰巳午未申酉戌亥")

STEM_READINGS = [
    "きのえ", "きのと", "ひのえ", "ひのと", "つちのえ",
    "つちのと", "かのえ", "かのと", "みずのえ", "みずのと",
]
BRANCH_READINGS = [
    "ね", "うし", "とら", "う", "たつ", "み",
    "うま", "ひつじ", "さる", "とり", "いぬ", "い",
]
BRANCH_ANIMALS = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
]

STEM_ELEMENTS = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth",
                 "Metal", "Metal", "Water", "Water"]
STEM_YINYANG = ["Yang", "Yin", "Yang", "Yin", "Yang", "Yin",
                "Yang", "Yin", "Yang", "Yin"]
BRANCH_ELEMENTS = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire",
                   "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]

ELEMENT_JP = {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"}
ELEMENT_EN = {v: k for k, v in ELEMENT_JP.items()}

# Solar month -> branch index (寅=Feb...丑=Jan)
SOLAR_MONTH_BRANCH = {
    2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
    8: 8, 9: 9, 10: 10, 11: 11, 12: 0, 1: 1,
}

NINE_STAR_NAMES = {
    1: "一白水星", 2: "二黒土星", 3: "三碧木星", 4: "四緑木星",
    5: "五黄土星", 6: "六白金星", 7: "七赤金星", 8: "八白土星",
    9: "九紫火星",
}
NINE_STAR_ELEMENTS = {
    1: "Water", 2: "Earth", 3: "Wood", 4: "Wood", 5: "Earth",
    6: "Metal", 7: "Metal", 8: "Earth", 9: "Fire",
}
NINE_STAR_DIRECTIONS = {
    1: "N", 2: "SW", 3: "E", 4: "SE", 5: "C",
    6: "NW", 7: "W", 8: "NE", 9: "S",
}

# Nine Star Ki month star lookup tables
# Group A = year stars [1,4,7], Group B = [2,5,8], Group C = [3,6,9]
# Index by month: Feb=0, Mar=1, Apr=2, ... Jan=11
MONTH_STAR_TABLE = {
    "A": [8, 7, 6, 5, 4, 3, 2, 1, 9, 8, 7, 6],
    "B": [2, 1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 9],
    "C": [5, 4, 3, 2, 1, 9, 8, 7, 6, 5, 4, 3],
}

# Palace names for nine-star cycle positions
PALACE_NAMES = {
    1: "坎宮", 2: "坤宮", 3: "震宮", 4: "巽宮", 5: "中宮",
    6: "乾宮", 7: "兌宮", 8: "艮宮", 9: "離宮",
}
PALACE_DIRECTIONS = {
    1: "N", 2: "SW", 3: "E", 4: "SE", 5: "C",
    6: "NW", 7: "W", 8: "NE", 9: "S",
}
PALACE_THEMES = {
    1: "厄・試練", 2: "変化・準備", 3: "発展・始動",
    4: "整備・信用", 5: "絶頂・転機", 6: "充実・実り",
    7: "悦び・収穫", 8: "停滞・自己改革", 9: "注目・離別",
}
PALACE_ENERGY = {1: 30, 2: 45, 3: 65, 4: 75, 5: 100, 6: 90, 7: 80, 8: 40, 9: 70}

# Rokusei star types
ROKUSEI_STARS = {
    1: "土星人", 2: "金星人", 3: "火星人",
    4: "天王星人", 5: "木星人", 6: "水星人",
}
ROKUSEI_SUB_MAP = {
    "土星人": "天王星人", "金星人": "木星人", "火星人": "水星人",
    "天王星人": "土星人", "木星人": "金星人", "水星人": "火星人",
}
ROKUSEI_REIGOU_BRANCH = {
    "土星人": {"+": "戌", "-": "亥"},
    "金星人": {"+": "申", "-": "酉"},
    "火星人": {"+": "午", "-": "未"},
    "天王星人": {"+": "辰", "-": "巳"},
    "木星人": {"+": "寅", "-": "卯"},
    "水星人": {"+": "子", "-": "丑"},
}

# Rokusei 12-phase cycle
ROKUSEI_PHASES = [
    "種子", "緑生", "立花", "健弱", "達成", "乱気",
    "再会", "財成", "安定", "陰影", "停止", "減退",
]
ROKUSEI_PHASE_SATSUKAI = {
    "陰影": "大殺界", "停止": "大殺界", "減退": "大殺界",
    "健弱": "小殺界", "乱気": "中殺界",
}
ROKUSEI_PHASE_ENERGY = {
    "種子": 50, "緑生": 65, "立花": 80, "健弱": 35,
    "達成": 90, "乱気": 25, "再会": 70, "財成": 85,
    "安定": 95, "陰影": 15, "停止": 10, "減退": 20,
}

# Rokusei base year for each star type (the year when the cycle starts at 種子)
ROKUSEI_SEED_YEARS = {
    "土星人": {"+": 2018, "-": 2019},
    "金星人": {"+": 2020, "-": 2019},
    "火星人": {"+": 2022, "-": 2023},
    "天王星人": {"+": 2016, "-": 2017},
    "木星人": {"+": 2014, "-": 2025},
    "水星人": {"+": 2016, "-": 2015},
}

# Western astrology sign data
WESTERN_SIGNS = [
    {"sign": "Aries", "symbol": "♈", "element": "Fire", "quality": "Cardinal",
     "ruler": "Mars", "start": (3, 21), "end": (4, 19)},
    {"sign": "Taurus", "symbol": "♉", "element": "Earth", "quality": "Fixed",
     "ruler": "Venus", "start": (4, 20), "end": (5, 20)},
    {"sign": "Gemini", "symbol": "♊", "element": "Air", "quality": "Mutable",
     "ruler": "Mercury", "start": (5, 21), "end": (6, 20)},
    {"sign": "Cancer", "symbol": "♋", "element": "Water", "quality": "Cardinal",
     "ruler": "Moon", "start": (6, 21), "end": (7, 22)},
    {"sign": "Leo", "symbol": "♌", "element": "Fire", "quality": "Fixed",
     "ruler": "Sun", "start": (7, 23), "end": (8, 22)},
    {"sign": "Virgo", "symbol": "♍", "element": "Earth", "quality": "Mutable",
     "ruler": "Mercury", "start": (8, 23), "end": (9, 22)},
    {"sign": "Libra", "symbol": "♎", "element": "Air", "quality": "Cardinal",
     "ruler": "Venus", "start": (9, 23), "end": (10, 22)},
    {"sign": "Scorpio", "symbol": "♏", "element": "Water", "quality": "Fixed",
     "ruler": "Pluto", "start": (10, 23), "end": (11, 21)},
    {"sign": "Sagittarius", "symbol": "♐", "element": "Fire", "quality": "Mutable",
     "ruler": "Jupiter", "start": (11, 22), "end": (12, 21)},
    {"sign": "Capricorn", "symbol": "♑", "element": "Earth", "quality": "Cardinal",
     "ruler": "Saturn", "start": (12, 22), "end": (1, 19)},
    {"sign": "Aquarius", "symbol": "♒", "element": "Air", "quality": "Fixed",
     "ruler": "Uranus", "start": (1, 20), "end": (2, 18)},
    {"sign": "Pisces", "symbol": "♓", "element": "Water", "quality": "Mutable",
     "ruler": "Neptune", "start": (2, 19), "end": (3, 20)},
]

BLOOD_TYPE_DATA = {
    "A": {
        "population_pct": 40,
        "strengths": ["真面目で責任感が強い", "計画性がある", "協調性が高い", "几帳面"],
        "challenges": ["心配性", "融通が利かない", "ストレスを溜めやすい"],
    },
    "B": {
        "population_pct": 20,
        "strengths": ["マイペース", "好奇心旺盛", "柔軟な発想", "行動力がある"],
        "challenges": ["飽きっぽい", "集中にムラがある", "周囲と歩調を合わせにくい"],
    },
    "O": {
        "population_pct": 30,
        "strengths": ["おおらか", "リーダーシップ", "社交的", "大胆な決断力"],
        "challenges": ["大雑把", "頑固", "感情的になりやすい"],
    },
    "AB": {
        "population_pct": 10,
        "strengths": ["合理的思考と感性の共存", "冷静な分析力", "多角的視点", "適応力"],
        "challenges": ["二面性による迷い", "感情の複雑さ", "他者から理解されにくい"],
    },
}

# Enneagram type names
ENNEAGRAM_NAMES = {
    1: "The Reformer", 2: "The Helper", 3: "The Achiever",
    4: "The Individualist", 5: "The Investigator", 6: "The Loyalist",
    7: "The Enthusiast", 8: "The Challenger", 9: "The Peacemaker",
}
ENNEAGRAM_DESCRIPTIONS = {
    1: "原則と改善への情熱。正しさと秩序を求める",
    2: "人への奉仕と愛情。他者のニーズを察知する",
    3: "達成と成功への邁進。効率と実績を重視",
    4: "自己表現とアイデンティティの探求。深い感情と独自性",
    5: "知識と理解への探求。観察と分析を重視",
    6: "安全と所属への希求。忠誠心と慎重さ",
    7: "自由と楽しさの追求。可能性と多様な体験",
    8: "力と自律への追求。正義感と決断力",
    9: "平和と調和の希求。包容力と安定",
}
ENNEAGRAM_GROWTH = {1: 7, 2: 4, 3: 6, 4: 1, 5: 8, 6: 9, 7: 5, 8: 2, 9: 3}
ENNEAGRAM_STRESS = {1: 4, 2: 8, 3: 9, 4: 2, 5: 7, 6: 3, 7: 1, 8: 5, 9: 6}

# Mini-IPIP Big Five: 20 items, 4 per factor
# Items are 1-indexed. R = reverse scored (6 - answer)
BIG_FIVE_ITEMS = {
    "Extraversion": [(1, False), (6, True), (11, False), (16, True)],
    "Agreeableness": [(2, True), (7, False), (12, True), (17, False)],
    "Conscientiousness": [(3, False), (8, True), (13, False), (18, True)],
    "Neuroticism": [(4, False), (9, True), (14, False), (19, True)],
    "Openness": [(5, False), (10, True), (15, False), (20, True)],
}

# ASRS thresholds per question (0-4 scale, threshold for "above")
ASRS_THRESHOLDS = [2, 2, 2, 2, 3, 3]


# ============================================================
# Date Utilities
# ============================================================

def julian_day_number(year, month, day):
    """Compute Julian Day Number for a Gregorian date."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (day + (153 * m + 2) // 5 + 365 * y
            + y // 4 - y // 100 + y // 400 - 32045)


def is_before_risshun(month, day):
    """Check if date is before 立春 (Feb 4)."""
    return month < 2 or (month == 2 and day < 4)


def solar_year(year, month, day):
    """Return the solar year for East Asian calendar purposes."""
    return year - 1 if is_before_risshun(month, day) else year


def solar_month_index(month, day):
    """Return the solar month branch index."""
    return SOLAR_MONTH_BRANCH[month]


# ============================================================
# Four Pillars (四柱推命)
# ============================================================

def calc_year_pillar(year, month, day):
    """Calculate year pillar (年柱)."""
    sy = solar_year(year, month, day)
    stem_idx = (sy - 4) % 10
    branch_idx = (sy - 4) % 12
    return _make_pillar(stem_idx, branch_idx)


def calc_month_pillar(year, month, day):
    """Calculate month pillar (月柱)."""
    sy = solar_year(year, month, day)
    year_stem_idx = (sy - 4) % 10
    month_branch_idx = solar_month_index(month, day)
    month_stem_idx = (year_stem_idx * 2 + month_branch_idx) % 10
    return _make_pillar(month_stem_idx, month_branch_idx)


def calc_day_pillar(year, month, day):
    """Calculate day pillar (日柱). Formula: (JDN + 49) % 60."""
    jdn = julian_day_number(year, month, day)
    cycle_idx = (jdn + 49) % 60
    stem_idx = cycle_idx % 10
    branch_idx = cycle_idx % 12
    return _make_pillar(stem_idx, branch_idx)


def _make_pillar(stem_idx, branch_idx):
    """Build a pillar dict from stem and branch indices."""
    stem_char = HEAVENLY_STEMS[stem_idx]
    branch_char = EARTHLY_BRANCHES[branch_idx]
    return {
        "stem": {
            "char": stem_char,
            "element": STEM_ELEMENTS[stem_idx],
            "yin_yang": STEM_YINYANG[stem_idx],
            "reading": STEM_READINGS[stem_idx],
        },
        "branch": {
            "char": branch_char,
            "animal": BRANCH_ANIMALS[branch_idx],
            "element": BRANCH_ELEMENTS[branch_idx],
            "reading": BRANCH_READINGS[branch_idx],
        },
        "full": f"{stem_char}{branch_char}",
    }


def calc_five_elements(pillars):
    """Calculate five elements balance from pillars."""
    element_sources = {"木": [], "火": [], "土": [], "金": [], "水": []}
    pillar_labels = ["年", "月", "日"]

    for i, p in enumerate(pillars):
        label = pillar_labels[i]
        stem_el = ELEMENT_JP[p["stem"]["element"]]
        branch_el = ELEMENT_JP[p["branch"]["element"]]
        element_sources[stem_el].append(f"{p['stem']['char']}({label}干)")
        element_sources[branch_el].append(f"{p['branch']['char']}({label}支)")

    total = sum(len(v) for v in element_sources.values())
    balance = {}
    missing = []
    for el in ["木", "火", "土", "金", "水"]:
        count = len(element_sources[el])
        source_str = "+".join(element_sources[el]) if count > 0 else "なし（時柱で補完の可能性）"
        balance[el] = {
            "count": count,
            "pct": round(count / total * 100) if total > 0 else 0,
            "source": source_str,
        }
        if count == 0:
            missing.append(el)

    return balance, missing


def calc_four_pillars(year, month, day, birth_time=None):
    """Complete four pillars calculation."""
    yp = calc_year_pillar(year, month, day)
    mp = calc_month_pillar(year, month, day)
    dp = calc_day_pillar(year, month, day)

    balance, missing = calc_five_elements([yp, mp, dp])

    day_master_element = dp["stem"]["element"]
    day_master_yy = dp["stem"]["yin_yang"]

    dm_descriptions = {
        ("Wood", "Yang"): "陽木 — 大樹。真っ直ぐに伸びる力強さ",
        ("Wood", "Yin"): "陰木 — 草花。柔軟でしなやか",
        ("Fire", "Yang"): "陽火 — 太陽。明るく力強い照射",
        ("Fire", "Yin"): "陰火 — ロウソクの炎。静かで温かく、人を照らす",
        ("Earth", "Yang"): "陽土 — 山。安定感と包容力",
        ("Earth", "Yin"): "陰土 — 田畑。育て受け入れる力",
        ("Metal", "Yang"): "陽金 — 刀剣。鋭い決断力",
        ("Metal", "Yin"): "陰金 — 宝石。洗練された美しさ",
        ("Water", "Yang"): "陽水 — 大海。広大な知恵と包容力",
        ("Water", "Yin"): "陰水 — 雨露。繊細で浸透する力",
    }

    element_meanings = {
        "木": "成長力・発展", "火": "情熱・行動力", "土": "安定・信頼",
        "金": "決断力・収穫", "水": "知恵・柔軟性",
    }
    if missing:
        missing_desc = "と".join(f"{el}({element_meanings[el]})" for el in missing)
        insight = f"{missing_desc}が欠如。意識的にこれらの要素を補う行動が有効"
    else:
        insight = "五行がバランス良く分布。総合力が高い"

    return {
        "year_pillar": yp,
        "month_pillar": mp,
        "day_pillar": dp,
        "hour_pillar": None,
        "day_master": {
            "char": dp["stem"]["char"],
            "element": day_master_element,
            "yin_yang": day_master_yy,
            "description": dm_descriptions.get((day_master_element, day_master_yy), ""),
        },
        "five_elements_balance": balance,
        "missing_elements": missing,
        "element_insight": insight,
    }


# ============================================================
# Nine Star Ki (九星気学)
# ============================================================

def _digit_sum_reduce(n):
    """Sum digits until single digit."""
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


def calc_nine_star_year(year, month, day):
    """Calculate year star number (1-9). Before Feb 4 = previous year."""
    sy = solar_year(year, month, day)
    ds = _digit_sum_reduce(sy)
    star = 11 - ds
    if star <= 0:
        star += 9
    if star > 9:
        star -= 9
    return star


def calc_nine_star_month(year, month, day):
    """Calculate month star number (1-9)."""
    year_star = calc_nine_star_year(year, month, day)

    if year_star in (1, 4, 7):
        group = "A"
    elif year_star in (2, 5, 8):
        group = "B"
    else:
        group = "C"

    if is_before_risshun(month, day):
        month_idx = 11  # Jan before Feb 4
    else:
        month_idx = (month - 2) % 12

    return MONTH_STAR_TABLE[group][month_idx]


def _calc_palace_position(person_star, center_star):
    """Calculate which palace a person's star occupies."""
    offset = center_star - 5
    palace = ((person_star - offset - 1) % 9) + 1
    return palace


def calc_nine_star_ki(year, month, day, forecast_year=None):
    """Complete nine star ki calculation."""
    year_star = calc_nine_star_year(year, month, day)
    month_star = calc_nine_star_month(year, month, day)

    result = {
        "year_star": {
            "number": year_star,
            "name": NINE_STAR_NAMES[year_star],
            "element": NINE_STAR_ELEMENTS[year_star],
            "direction": NINE_STAR_DIRECTIONS[year_star],
        },
        "month_star": {
            "number": month_star,
            "name": NINE_STAR_NAMES[month_star],
            "element": NINE_STAR_ELEMENTS[month_star],
            "direction": NINE_STAR_DIRECTIONS[month_star],
        },
    }

    if forecast_year:
        center_star = calc_nine_star_year(forecast_year, 6, 1)
        palace_num = _calc_palace_position(year_star, center_star)
        result["year_cycle"] = {
            "center_star": {
                "number": center_star,
                "name": NINE_STAR_NAMES[center_star],
            },
            "position": {
                "palace": PALACE_NAMES[palace_num],
                "direction": PALACE_DIRECTIONS[palace_num],
                "meaning": PALACE_THEMES[palace_num],
            },
        }

        nine_year = []
        for offset in range(-2, 7):
            yr = forecast_year + offset
            cs = calc_nine_star_year(yr, 6, 1)
            pn = _calc_palace_position(year_star, cs)
            entry = {
                "year": yr,
                "palace": PALACE_NAMES[pn],
                "theme": PALACE_THEMES[pn],
                "energy": PALACE_ENERGY[pn],
            }
            if yr == forecast_year:
                entry["current"] = True
            nine_year.append(entry)
        result["nine_year_cycle"] = nine_year

    return result


# ============================================================
# Rokusei Senjutsu (六星占術)
# ============================================================

def _rokusei_fate_number(year, month):
    """
    Calculate 運命数 (fate number).
    Equals the 1-based sexagenary day index for the 1st of the birth month.
    """
    jdn = julian_day_number(year, month, 1)
    return (jdn + 49) % 60 + 1


def _rokusei_star_number(year, month, day):
    """Calculate 星数 = (運命数 - 1) + birth_day. If >= 61, subtract 60."""
    fn = _rokusei_fate_number(year, month)
    sn = (fn - 1) + day
    if sn >= 61:
        sn -= 60
    return sn


def _rokusei_star_type(star_number):
    """Map star number to star type name."""
    idx = (star_number - 1) // 10 + 1
    return ROKUSEI_STARS[idx]


def _rokusei_polarity(year):
    """Determine +/- polarity from earthly branch of birth year."""
    branch_idx = (year - 4) % 12
    return "+" if branch_idx % 2 == 0 else "-"


def _rokusei_check_reigou(star, polarity, year):
    """Check if the person is a 霊合星人."""
    branch_idx = (year - 4) % 12
    branch_char = EARTHLY_BRANCHES[branch_idx]
    return branch_char == ROKUSEI_REIGOU_BRANCH[star][polarity]


def _rokusei_find_seed_year(star, polarity, reference_year):
    """Find the nearest 種子 year for the star type near reference_year."""
    base = ROKUSEI_SEED_YEARS.get(star, {}).get(polarity)
    if base is None:
        star_idx = list(ROKUSEI_STARS.values()).index(star)
        base = 2013 + star_idx * 2
    diff = (reference_year - base) % 12
    return reference_year - diff


def _rokusei_phase_for_year(seed_year, target_year):
    """Get the 12-phase position for a given year."""
    idx = (target_year - seed_year) % 12
    return ROKUSEI_PHASES[idx]


def _build_rokusei_cycle(star, polarity, forecast_year,
                         years_before=2, years_after=7):
    """Build the 12-year cycle centered on forecast_year."""
    seed = _rokusei_find_seed_year(star, polarity, forecast_year)
    cycle = []
    for offset in range(-years_before, years_after + 1):
        yr = forecast_year + offset
        phase = _rokusei_phase_for_year(seed, yr)
        satsukai = ROKUSEI_PHASE_SATSUKAI.get(phase)
        entry = {
            "year": yr,
            "phase": phase,
            "殺界": satsukai,
            "energy": ROKUSEI_PHASE_ENERGY[phase],
        }
        if yr == forecast_year:
            entry["current"] = True
        cycle.append(entry)
    return cycle


def calc_rokusei(year, month, day, forecast_year=None):
    """Complete rokusei calculation."""
    sn = _rokusei_star_number(year, month, day)
    star = _rokusei_star_type(sn)
    pol = _rokusei_polarity(year)
    is_reigou = _rokusei_check_reigou(star, pol, year)

    reading_map = {
        "土星人": "どせいじん", "金星人": "きんせいじん",
        "火星人": "かせいじん", "天王星人": "てんのうせいじん",
        "木星人": "もくせいじん", "水星人": "すいせいじん",
    }

    result = {
        "main_star": {
            "name": star,
            "polarity": pol,
            "reading": f"{reading_map[star]} {'プラス' if pol == '+' else 'マイナス'}",
        },
        "reigou": is_reigou,
    }

    if is_reigou:
        sub = ROKUSEI_SUB_MAP[star]
        result["sub_star"] = {
            "name": sub,
            "polarity": pol,
            "reading": f"{reading_map[sub]} {'プラス' if pol == '+' else 'マイナス'}",
        }

    if forecast_year:
        main_cycle = _build_rokusei_cycle(star, pol, forecast_year)
        result["twelve_year_cycle"] = main_cycle

        if is_reigou:
            sub = ROKUSEI_SUB_MAP[star]
            sub_cycle = _build_rokusei_cycle(sub, pol, forecast_year)
            result["sub_star_cycle"] = sub_cycle

            combined = []
            for mc, sc in zip(main_cycle, sub_cycle):
                score = round(mc["energy"] * 0.7 + sc["energy"] * 0.3)
                labels = {
                    range(0, 20): "最悪期", range(20, 35): "危険期",
                    range(35, 50): "要注意", range(50, 65): "回復開始",
                    range(65, 78): "好調", range(78, 90): "絶好調",
                    range(90, 101): "最高潮",
                }
                label = "好調"
                for r, l in labels.items():
                    if score in r:
                        label = l
                        break
                if mc["energy"] >= 70 and sc["energy"] <= 25:
                    label = "矛盾期"
                elif mc["energy"] <= 25 and sc["energy"] >= 70:
                    label = "矛盾期"
                combined.append({"year": mc["year"], "score": score, "label": label})
            result["reigou_combined"] = combined

    return result


# ============================================================
# Western Astrology
# ============================================================

def calc_western_astrology(month, day):
    """Calculate western astrology sun sign."""
    for sign_data in WESTERN_SIGNS:
        sm, sd = sign_data["start"]
        em, ed = sign_data["end"]
        if sm == em:
            if month == sm and sd <= day <= ed:
                break
        elif sm > em:
            if (month == sm and day >= sd) or (month == em and day <= ed):
                break
        else:
            if (month == sm and day >= sd) or (month == em and day <= ed):
                break
    else:
        sign_data = WESTERN_SIGNS[0]

    return {
        "sun_sign": {
            "sign": sign_data["sign"],
            "symbol": sign_data["symbol"],
            "element": sign_data["element"],
            "quality": sign_data["quality"],
        },
        "ruling_planet": sign_data["ruler"],
        "ascendant": None,
        "moon_sign": None,
    }


# ============================================================
# Blood Type
# ============================================================

def calc_blood_type(bt):
    """Build blood type section."""
    bt = bt.upper().strip()
    data = BLOOD_TYPE_DATA.get(bt)
    if not data:
        return {"type": bt, "population_pct": None, "traits": {}}
    return {
        "type": bt,
        "population_pct": data["population_pct"],
        "traits": {
            "strengths": data["strengths"],
            "challenges": data["challenges"],
        },
    }


# ============================================================
# Personality Scoring (Tier 2 & 3)
# ============================================================

def calc_enneagram(answers):
    """
    Process enneagram answers.
    Input: [primary_type, wing_notation, third_type] e.g. [4, "3w4", "1"]
    """
    if not answers or len(answers) < 1:
        return None

    primary = int(answers[0])
    wing = None
    if len(answers) >= 2 and answers[1]:
        wing_str = str(answers[1])
        if "w" in wing_str.lower():
            parts = wing_str.lower().split("w")
            wing = int(parts[1]) if len(parts) > 1 else None
        else:
            wing = int(wing_str) if wing_str.isdigit() else None

    return {
        "type": primary,
        "name": ENNEAGRAM_NAMES.get(primary, ""),
        "description": ENNEAGRAM_DESCRIPTIONS.get(primary, ""),
        "wing": wing,
        "growth_direction": ENNEAGRAM_GROWTH.get(primary),
        "stress_direction": ENNEAGRAM_STRESS.get(primary),
    }


def calc_hsp(answers):
    """
    HSP-6 scoring. 6 items, each 1-5 Likert.
    Subscales: Sensory (0,1), Emotional (2,3), Social (4,5).
    Total /30. <=12=low, 13-20=medium, 21+=high.
    """
    if not answers or len(answers) != 6:
        return None

    scores = [int(a) for a in answers]
    total = sum(scores)

    if total <= 12:
        level = "low"
    elif total <= 20:
        level = "medium"
    else:
        level = "high"

    return {
        "score": level,
        "total": total,
        "max": 30,
        "subscales": {
            "sensory": sum(scores[0:2]),
            "emotional": sum(scores[2:4]),
            "social": sum(scores[4:6]),
        },
    }


def calc_adhd(answers):
    """
    ADHD ASRS-6 screening. 6 items, each 0-4.
    Thresholds: [2,2,2,2,3,3].
    4+ above = significant, 2-3 = leaning, 0-1 = minimal.
    """
    if not answers or len(answers) != 6:
        return None

    scores = [int(a) for a in answers]
    above_count = sum(1 for s, t in zip(scores, ASRS_THRESHOLDS) if s >= t)

    if above_count >= 4:
        tendency = "significant"
    elif above_count >= 2:
        tendency = "leaning"
    else:
        tendency = "minimal"

    return {
        "tendency": tendency,
        "above_threshold_count": above_count,
        "total_items": 6,
    }


def calc_big_five(answers):
    """
    Mini-IPIP Big Five. 20 items, each 1-5 Likert.
    Reverse-scored items use (6 - answer).
    Returns OCEAN scores and MBTI-equivalent mapping.
    """
    if not answers or len(answers) != 20:
        return None

    scores = [int(a) for a in answers]
    factors = {}

    for factor_name, items in BIG_FIVE_ITEMS.items():
        factor_total = 0
        for item_num, is_reverse in items:
            raw = scores[item_num - 1]
            factor_total += (6 - raw) if is_reverse else raw
        factors[factor_name] = factor_total

    ei = "E" if factors["Extraversion"] >= 12 else "I"
    sn = "N" if factors["Openness"] >= 12 else "S"
    tf = "F" if factors["Agreeableness"] >= 12 else "T"
    jp = "J" if factors["Conscientiousness"] >= 12 else "P"

    return {
        "ocean": factors,
        "mbti_equivalent": f"{ei}{sn}{tf}{jp}",
    }


# ============================================================
# Monthly Fortune (月運計算)
# ============================================================

# Note mapping for nine star energy levels
NINE_STAR_NOTE_MAP = [
    (90, "大吉・最盛"),
    (80, "大吉・好調"),
    (70, "上昇運"),
    (60, "中吉・回復"),
    (50, "小吉・転換"),
    (40, "吉凶混合"),
    (25, "中凶・注意"),
    (0, "大凶"),
]

# Rokusei phase type mapping
ROKUSEI_PHASE_TYPE = {
    "立花": "great", "達成": "great", "安定": "great", "財成": "great",
    "種子": "good", "緑生": "good", "再会": "good",
    "健弱": "caution", "乱気": "caution",
    "陰影": "danger", "停止": "danger", "減退": "danger",
}


def _nine_star_note(energy):
    """Map nine star energy to descriptive note."""
    for threshold, note in NINE_STAR_NOTE_MAP:
        if energy >= threshold:
            return note
    return "大凶"


def _year_star_group(star_number):
    """Determine which month-star group a year star belongs to."""
    if star_number in (1, 4, 7):
        return "A"
    elif star_number in (2, 5, 8):
        return "B"
    else:
        return "C"


def _domain_stars(combined, rokusei_phase, rokusei_satsukai):
    """Calculate domain star ratings (1-5) from combined energy."""
    # Work stars: direct mapping from combined
    if combined >= 81:
        work = 5
    elif combined >= 61:
        work = 4
    elif combined >= 41:
        work = 3
    elif combined >= 21:
        work = 2
    else:
        work = 1

    # Money stars: slightly lower when rokusei has 殺界
    money = work
    if rokusei_satsukai:
        money = max(1, money - 1)

    # Health stars: lower when rokusei phase is 健弱 or combined is low
    health = work
    if rokusei_phase == "健弱":
        health = max(1, health - 1)
    if combined < 30:
        health = max(1, health - 1)

    # Romance stars: similar to work but slightly offset
    if combined >= 85:
        romance = 5
    elif combined >= 65:
        romance = 4
    elif combined >= 45:
        romance = 3
    elif combined >= 25:
        romance = 2
    else:
        romance = 1

    return {"work": work, "money": money, "health": health, "romance": romance}


def calc_monthly_fortune(person_year_star, rokusei_data, forecast_year):
    """
    Calculate monthly fortune for each month (1-12) of the forecast year.

    Args:
        person_year_star: The person's nine star ki year star number (1-9)
        rokusei_data: The rokusei calculation result (contains twelve_year_cycle)
        forecast_year: The year to forecast

    Returns:
        List of 12 monthly fortune dicts
    """
    # Determine forecast year's center star
    forecast_center_star = calc_nine_star_year(forecast_year, 6, 1)
    # Previous year's center star (for January)
    prev_center_star = calc_nine_star_year(forecast_year - 1, 6, 1)

    # Year star groups for monthly star lookup
    forecast_group = _year_star_group(forecast_center_star)
    prev_group = _year_star_group(prev_center_star)

    # Find yearly phase index from twelve_year_cycle
    yearly_phase_index = 0
    twelve_year_cycle = rokusei_data.get("twelve_year_cycle", [])
    for entry in twelve_year_cycle:
        if entry.get("current"):
            phase_name = entry["phase"]
            yearly_phase_index = ROKUSEI_PHASES.index(phase_name)
            break

    monthly_fortune = []

    for month_number in range(1, 13):
        # --- Nine Star Ki monthly palace ---
        if month_number == 1:
            # January is before risshun, use previous year's center star
            month_idx = 11  # Jan = index 11
            group = prev_group
            center_star = prev_center_star
        else:
            month_idx = (month_number - 2) % 12  # Feb=0, Mar=1, ..., Dec=10
            group = forecast_group
            center_star = forecast_center_star

        monthly_center_star = MONTH_STAR_TABLE[group][month_idx]
        palace_num = _calc_palace_position(person_year_star, monthly_center_star)
        nine_star_energy = PALACE_ENERGY[palace_num]
        nine_star_note = _nine_star_note(nine_star_energy)

        # --- Rokusei monthly phase ---
        rokusei_monthly_idx = (yearly_phase_index + 6 + month_number) % 12
        rokusei_phase = ROKUSEI_PHASES[rokusei_monthly_idx]
        rokusei_satsukai = ROKUSEI_PHASE_SATSUKAI.get(rokusei_phase)
        rokusei_energy = ROKUSEI_PHASE_ENERGY[rokusei_phase]
        rokusei_type = ROKUSEI_PHASE_TYPE[rokusei_phase]

        # --- Domain star ratings ---
        combined = (nine_star_energy + rokusei_energy) / 2
        domains = _domain_stars(combined, rokusei_phase, rokusei_satsukai)

        monthly_fortune.append({
            "month": month_number,
            "nine_star": {
                "palace": PALACE_NAMES[palace_num],
                "energy": nine_star_energy,
                "note": nine_star_note,
            },
            "rokusei": {
                "phase": rokusei_phase,
                "satsukai": rokusei_satsukai,
                "energy": rokusei_energy,
                "type": rokusei_type,
            },
            "domains": domains,
        })

    return monthly_fortune


# ============================================================
# Profile Assembly
# ============================================================

def generate_profile(name, birth_date, blood_type,
                     birth_time=None, sex=None, birth_place=None,
                     tier2_answers=None, tier3_answers=None,
                     existing=None, forecast_year=None):
    """Generate a complete profile."""
    bd = datetime.date.fromisoformat(birth_date)
    year, month, day = bd.year, bd.month, bd.day

    if forecast_year is None:
        forecast_year = datetime.date.today().year

    today = datetime.date.today()
    age = forecast_year - year
    if (month, day) > (today.month, today.day):
        age -= 1

    identity = {
        "name": name,
        "birth_date": birth_date,
        "birth_time": birth_time,
        "birth_place": birth_place,
        "blood_type": blood_type.upper(),
        "age": age,
    }
    if sex:
        identity["sex"] = sex

    personality = {}
    if tier2_answers:
        if "enneagram" in tier2_answers:
            enneagram = calc_enneagram(tier2_answers["enneagram"])
            if enneagram:
                personality["enneagram"] = enneagram
        if "hsp" in tier2_answers:
            hsp = calc_hsp(tier2_answers["hsp"])
            if hsp:
                personality["hsp"] = hsp
        if "adhd" in tier2_answers:
            adhd = calc_adhd(tier2_answers["adhd"])
            if adhd:
                personality["adhd"] = adhd

    if tier3_answers:
        big5 = calc_big_five(tier3_answers)
        if big5:
            personality["big_five"] = big5["ocean"]
            personality["mbti"] = big5["mbti_equivalent"]

    if existing:
        if "mbti" in existing and existing["mbti"]:
            personality["mbti"] = existing["mbti"]

    if not personality.get("mbti"):
        personality["mbti"] = None

    four_pillars = calc_four_pillars(year, month, day, birth_time)
    nine_star = calc_nine_star_ki(year, month, day, forecast_year)
    rokusei = calc_rokusei(year, month, day, forecast_year)
    western = calc_western_astrology(month, day)
    bt = calc_blood_type(blood_type)

    person_year_star = nine_star["year_star"]["number"]
    monthly_fortune = calc_monthly_fortune(person_year_star, rokusei, forecast_year)

    return {
        "identity": identity,
        "personality": personality,
        "four_pillars": four_pillars,
        "nine_star_ki": nine_star,
        "rokusei": rokusei,
        "western_astrology": western,
        "blood_type": bt,
        "monthly_fortune": monthly_fortune,
    }


# ============================================================
# YAML Output
# ============================================================

class ProfileDumper(yaml.Dumper):
    """Custom YAML dumper for readable output."""
    pass


def _str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _none_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "null")


ProfileDumper.add_representer(str, _str_representer)
ProfileDumper.add_representer(type(None), _none_representer)


def write_profile(profile, output_path):
    """Write profile dict to YAML file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Self-Insight Profile — {profile['identity']['name']}\n")
        f.write(f"# Generated: {datetime.date.today().isoformat()}\n\n")
        yaml.dump(
            profile, f,
            Dumper=ProfileDumper,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Self-Insight Profile Generator")
    parser.add_argument("--name", required=True)
    parser.add_argument("--birth-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--blood-type", required=True, help="A/B/O/AB")
    parser.add_argument("--birth-time", help="HH:MM (optional)")
    parser.add_argument("--sex", help="male/female (optional)")
    parser.add_argument("--birth-place", help="Place of birth (optional)")
    parser.add_argument("--tier2-answers", help="JSON: enneagram/hsp/adhd")
    parser.add_argument("--tier3-answers", help="JSON: 20-item Mini-IPIP")
    parser.add_argument("--existing", help="JSON: pre-existing assessments")
    parser.add_argument("--forecast-year", type=int,
                        default=datetime.date.today().year)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    tier2 = json.loads(args.tier2_answers) if args.tier2_answers else None
    tier3 = json.loads(args.tier3_answers) if args.tier3_answers else None
    existing = json.loads(args.existing) if args.existing else None

    profile = generate_profile(
        name=args.name,
        birth_date=args.birth_date,
        blood_type=args.blood_type,
        birth_time=args.birth_time,
        sex=args.sex,
        birth_place=args.birth_place,
        tier2_answers=tier2,
        tier3_answers=tier3,
        existing=existing,
        forecast_year=args.forecast_year,
    )

    write_profile(profile, args.output)
    print(f"Profile written to {args.output}")


if __name__ == "__main__":
    main()
