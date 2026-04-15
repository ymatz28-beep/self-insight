#!/usr/bin/env python3
"""Self-Insight 相性診断 generator.

4体系統合スコア:
- 血液型相性（伝統的マトリクス）
- 西洋占星術相性（元素・アスペクト）
- 四柱推命相性（日主五行・陰陽）
- 干支相性（三合・六合・冲）

Tier 2 (エニアグラム / HSP / ADHD / 24SF / 16A) は未実装・プレースホルダ。

CLI:
  python3 generate_compatibility.py --a data/users/yuma/profile.yaml \\
    --b data/users/shizuka/profile.yaml --output users/compat/yuma-shizuka/index.html
"""
import argparse
import os
import sys
from pathlib import Path

import yaml


def load_profile(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ========================================================================
# 1. 血液型 相性 (日本の伝統的マトリクス・文化的参考値)
# ========================================================================
BT_COMPAT = {
    ('A','A'):   (70, 'お互い真面目で計画的、価値観が似る。争いが少ない代わりに刺激もやや少なめ'),
    ('A','B'):   (50, 'A の計画性と B の自由さが反発しやすい。互いを尊重できれば絶妙な補完関係に'),
    ('A','O'):   (85, 'O の包容力が A の気遣いを受け止める。最も相性が良いとされる組み合わせ'),
    ('A','AB'):  (75, 'A の堅実さを AB が冷静に支える。会話が通じやすいコンビ'),
    ('B','B'):   (65, '自由人同士、楽しい時間を共有できる。ただし生活リズムがズレると衝突'),
    ('B','O'):   (70, 'O の現実主義が B の発想を地に足つかせる。刺激のある組み合わせ'),
    ('B','AB'):  (80, 'AB の合理性が B の衝動性を和らげる。意外と相性が良い'),
    ('O','O'):   (75, '社交的同士、友達のような関係。深さは自分たちで作る必要あり'),
    ('O','AB'):  (70, 'O が主導、AB が調整役。役割分担が自然に決まる'),
    ('AB','AB'): (60, '同類同士の理解。ただし二面性も2倍で、感情の読み合いに疲れることも'),
}

def bt_compat(bt_a, bt_b):
    key = tuple(sorted([bt_a, bt_b]))  # alphabetical canonical
    if key in BT_COMPAT:
        s, n = BT_COMPAT[key]
    elif (key[1], key[0]) in BT_COMPAT:
        s, n = BT_COMPAT[(key[1], key[0])]
    else:
        s, n = 65, 'データ不足'
    return {'score': s, 'narrative': n, 'label_a': f'{bt_a}型', 'label_b': f'{bt_b}型'}


# ========================================================================
# 2. 西洋占星術 相性 (元素 + アスペクト距離)
# ========================================================================
SIGN_ELEMENT = {
    'Aries':'Fire','Leo':'Fire','Sagittarius':'Fire',
    'Taurus':'Earth','Virgo':'Earth','Capricorn':'Earth',
    'Gemini':'Air','Libra':'Air','Aquarius':'Air',
    'Cancer':'Water','Scorpio':'Water','Pisces':'Water',
}
SIGN_JA = {
    'Aries':'牡羊座','Taurus':'牡牛座','Gemini':'双子座','Cancer':'蟹座',
    'Leo':'獅子座','Virgo':'乙女座','Libra':'天秤座','Scorpio':'蠍座',
    'Sagittarius':'射手座','Capricorn':'山羊座','Aquarius':'水瓶座','Pisces':'魚座',
}
SIGN_ORDER = list(SIGN_JA.keys())

ELEMENT_SCORE = {
    frozenset(['Fire','Fire']):   (75, '情熱同士、エネルギーは絶大。燃え尽きに注意'),
    frozenset(['Fire','Air']):    (85, '空気が炎を煽る。話が弾み、刺激し合える最良の組み合わせ'),
    frozenset(['Fire','Earth']):  (55, '火と土は噛み合いにくい。情熱 vs 堅実の温度差'),
    frozenset(['Fire','Water']):  (50, '水は火を消す。価値観の根本が違うので歩み寄りが必須'),
    frozenset(['Earth','Earth']): (80, '堅実同士、安定感抜群。ただし変化に弱い'),
    frozenset(['Earth','Water']): (85, '水が土を潤す。お互いを育て合う深い関係'),
    frozenset(['Earth','Air']):   (60, '現実 vs 観念。地に足をつける派 vs 飛ぶ派'),
    frozenset(['Air','Air']):     (72, '会話が止まらない。知的刺激は無限、実行は弱い'),
    frozenset(['Air','Water']):   (55, '論理 vs 感情。話が噛み合わない時期もある'),
    frozenset(['Water','Water']): (78, '感情の深い共有。閉じすぎに注意'),
}

def sign_aspect_name(a, b):
    ia, ib = SIGN_ORDER.index(a), SIGN_ORDER.index(b)
    diff = abs(ia - ib) % 12
    if diff > 6: diff = 12 - diff
    # 0=合, 1=ノーアスペクト, 2=セクスタイル(60°), 3=スクエア(90°),
    # 4=トライン(120°), 5=クインカンクス(150°), 6=オポジション(180°)
    return {
        0: ('合（同じ星座）', 70, '近すぎて分からなくなる鏡像関係'),
        1: ('セミセクスタイル', 60, '近いが違和感のある距離感'),
        2: ('セクスタイル（60°）', 85, '自然に助け合える友愛関係'),
        3: ('スクエア（90°）', 50, '摩擦と成長。衝突しながら鍛え合う'),
        4: ('トライン（120°）', 95, '元素が同じで最高の調和。楽すぎるほど'),
        5: ('クインカンクス', 55, '違和感の解消に努力が必要'),
        6: ('オポジション（180°）', 75, '正反対だからこそ補い合える磁力'),
    }[diff]

def western_compat(sign_a, sign_b):
    e_a = SIGN_ELEMENT.get(sign_a, 'Fire')
    e_b = SIGN_ELEMENT.get(sign_b, 'Fire')
    elem_score, elem_note = ELEMENT_SCORE.get(frozenset([e_a, e_b]), (60, '要素間の関係'))
    aspect_name, aspect_score, aspect_note = sign_aspect_name(sign_a, sign_b)
    # 50/50 combined
    score = int((elem_score + aspect_score) / 2)
    narrative = f'{SIGN_JA.get(sign_a,sign_a)}（{e_a}）× {SIGN_JA.get(sign_b,sign_b)}（{e_b}）= {aspect_name}。{elem_note}。{aspect_note}'
    return {
        'score': score,
        'narrative': narrative,
        'label_a': SIGN_JA.get(sign_a, sign_a),
        'label_b': SIGN_JA.get(sign_b, sign_b),
        'detail_element_score': elem_score,
        'detail_aspect_score': aspect_score,
        'detail_aspect_name': aspect_name,
    }


# ========================================================================
# 3. 四柱推命 相性 (日主五行 + 陰陽)
# ========================================================================
# 相生サイクル (generating) / 相剋サイクル (controlling)
SHENG = {
    ('Wood','Fire'),('Fire','Earth'),('Earth','Metal'),('Metal','Water'),('Water','Wood'),
}
KE = {
    ('Wood','Earth'),('Earth','Water'),('Water','Fire'),('Fire','Metal'),('Metal','Wood'),
}

def fp_compat(dm_a, dm_b):
    ea = dm_a.get('element', '')
    eb = dm_b.get('element', '')
    ya = dm_a.get('yin_yang', '')
    yb = dm_b.get('yin_yang', '')
    ca = dm_a.get('char', '')
    cb = dm_b.get('char', '')

    # Element relation
    if ea == eb:
        elem_score = 70
        elem_label = '同じ元素（{e}）'.format(e=ea)
        elem_desc = '似た気質で理解し合えるが、違いが少なく刺激も少ない'
    elif (ea, eb) in SHENG or (eb, ea) in SHENG:
        elem_score = 88
        # Determine direction
        if (ea, eb) in SHENG:
            elem_label = f'相生（{ea} → {eb}）'
            elem_desc = f'{ea} が {eb} を育てる関係。流れが自然'
        else:
            elem_label = f'相生（{eb} → {ea}）'
            elem_desc = f'{eb} が {ea} を育てる関係。流れが自然'
    elif (ea, eb) in KE or (eb, ea) in KE:
        elem_score = 52
        elem_label = '相剋'
        elem_desc = 'お互いを抑え合う関係。ぶつかると痛いが、鍛え合える関係でもある'
    else:
        elem_score = 60
        elem_label = '中立'
        elem_desc = '特定の相性関係なし'

    # Yin/Yang complementarity
    if ya == yb:
        yy_score = 68
        yy_desc = f'同じ陰陽（{ya}）。似た温度感で落ち着くが、エネルギーが一方向に偏る'
    else:
        yy_score = 82
        yy_desc = '陰陽が相補的。違いが摩擦と魅力の両方を生む'

    score = int((elem_score * 0.65) + (yy_score * 0.35))
    narrative = f'日主 {ca}（{ea}・{ya}） × {cb}（{eb}・{yb}）: {elem_label}。{elem_desc}。陰陽は{yy_desc}'

    return {
        'score': score,
        'narrative': narrative,
        'label_a': f'{ca}（{ea}）',
        'label_b': f'{cb}（{eb}）',
        'detail_element_label': elem_label,
        'detail_yinyang_label': yy_desc,
    }


# ========================================================================
# 4. 干支 相性 (三合・六合・冲)
# ========================================================================
ANIMAL_JA = {
    'Rat':'子','Ox':'丑','Tiger':'寅','Rabbit':'卯','Dragon':'辰','Snake':'巳',
    'Horse':'午','Goat':'未','Monkey':'申','Rooster':'酉','Dog':'戌','Pig':'亥',
}
# 三合 (strongest positive)
SANGOU_SETS = [
    frozenset(['Tiger','Horse','Dog']),    # 寅午戌 火局
    frozenset(['Snake','Rooster','Ox']),   # 巳酉丑 金局
    frozenset(['Monkey','Rat','Dragon']),  # 申子辰 水局
    frozenset(['Pig','Rabbit','Goat']),    # 亥卯未 木局
]
SANGOU_LABEL = {
    frozenset(['Tiger','Horse','Dog']):    '火局（寅午戌）',
    frozenset(['Snake','Rooster','Ox']):   '金局（巳酉丑）',
    frozenset(['Monkey','Rat','Dragon']):  '水局（申子辰）',
    frozenset(['Pig','Rabbit','Goat']):    '木局（亥卯未）',
}
# 六合 (harmonic pair)
RIKUGOU = [
    frozenset(['Rat','Ox']), frozenset(['Horse','Goat']),
    frozenset(['Tiger','Pig']), frozenset(['Rabbit','Dog']),
    frozenset(['Dragon','Rooster']), frozenset(['Snake','Monkey']),
]
# 冲 (opposing)
CHOU = [
    frozenset(['Rat','Horse']), frozenset(['Ox','Goat']),
    frozenset(['Tiger','Monkey']), frozenset(['Rabbit','Rooster']),
    frozenset(['Dragon','Dog']), frozenset(['Snake','Pig']),
]

def eto_compat(animal_a, animal_b):
    pair = frozenset([animal_a, animal_b])
    if animal_a == animal_b:
        score = 70
        label = '同干支'
        desc = '同じ気質同士、気が楽。ただし新鮮さは減る'
    elif any(pair <= s for s in SANGOU_SETS):
        sangou = next(s for s in SANGOU_SETS if pair <= s)
        score = 92
        label = f'三合の一部（{SANGOU_LABEL[sangou]}）'
        desc = '東洋占術で最も強い良縁とされる組み合わせ。自然と協力できる関係'
    elif pair in [frozenset(r) for r in RIKUGOU]:
        score = 85
        label = '六合'
        desc = '安定した協調関係を築ける組み合わせ'
    elif pair in [frozenset(c) for c in CHOU]:
        score = 48
        label = '冲（対立）'
        desc = '正反対の気質。ぶつかりやすいが、それゆえ強い刺激を与え合える関係'
    else:
        score = 68
        label = '中立'
        desc = '特別な縁の組み合わせではないが、普通に付き合える距離感'

    ja_a = ANIMAL_JA.get(animal_a, animal_a)
    ja_b = ANIMAL_JA.get(animal_b, animal_b)
    narrative = f'{ja_a}年 × {ja_b}年 = {label}。{desc}'
    return {
        'score': score,
        'narrative': narrative,
        'label_a': f'{ja_a}年',
        'label_b': f'{ja_b}年',
        'detail_relation': label,
    }


# ========================================================================
# 統合スコア (重み付き平均)
# ========================================================================
WEIGHTS_TIER1 = {
    'bt':        0.15,
    'western':   0.30,
    'fp':        0.30,
    'eto':       0.25,
}

def integrated_score(scores):
    """scores: dict with keys matching WEIGHTS_TIER1. Returns weighted integer score."""
    total_w = sum(WEIGHTS_TIER1.get(k, 0) for k in scores.keys())
    weighted = sum(scores[k] * WEIGHTS_TIER1.get(k, 0) for k in scores.keys())
    return int(round(weighted / total_w)) if total_w > 0 else 0


def overall_verdict(score):
    if score >= 85:
        return ('★★★★★', '#86efac', '非常に良い相性')
    if score >= 75:
        return ('★★★★☆', '#86efac', '良い相性')
    if score >= 65:
        return ('★★★☆☆', '#fde68a', '普通の相性')
    if score >= 55:
        return ('★★☆☆☆', '#fbbf24', '摩擦が起きやすい相性')
    return ('★☆☆☆☆', '#fca5a5', '注意が必要な相性')


# ========================================================================
# HTML rendering
# ========================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name_a} × {name_b} 相性診断 — Self-Insight</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400..700&family=JetBrains+Mono:wght@500&family=Noto+Sans+JP:wght@400..700&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#242836;
  --border:#2d3348;--border-light:#3d4460;
  --text:#e4e4e7;--text-secondary:#9ca3af;--text-muted:#7c8293;
  --gold:#c9a84c;--accent:#6366f1;
  --green:#22c55e;--red:#ef4444;--yellow:#eab308;--amber:#fbbf24;--blue:#3b82f6;
  --font-body:'Inter','Noto Sans JP',sans-serif;
  --font-mono:'JetBrains Mono',monospace;
  --radius-md:10px;--radius-lg:14px;--radius-xl:16px;
  --gnav-height:52px;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{font-size:16px}}
body{{font-family:var(--font-body);background:var(--bg);color:var(--text);line-height:1.8;padding-bottom:80px;min-height:100vh}}
.container{{max-width:820px;margin:0 auto;padding:0 18px}}
.top-nav{{height:var(--gnav-height);background:rgba(15,17,23,.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;display:flex;align-items:center}}
.top-nav-inner{{max-width:820px;margin:0 auto;padding:0 18px;width:100%;display:flex;align-items:center;justify-content:space-between}}
.brand{{font-weight:700;font-size:14px;color:var(--text);display:flex;align-items:center;gap:8px;text-decoration:none}}
.brand::before{{content:"◆";color:var(--gold);font-size:12px}}

.hero{{background:linear-gradient(135deg,#1e1b4b,#4c1d95,#1e1b4b);border-radius:var(--radius-xl);padding:32px 24px;margin:24px 0;border:1px solid var(--border)}}
.hero-badge{{display:inline-block;font-size:10px;font-weight:700;padding:4px 12px;border-radius:16px;border:1px solid rgba(251,191,36,0.3);background:rgba(251,191,36,0.1);color:#fde68a;letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px}}
.hero h1{{font-size:clamp(22px,3vw,28px);font-weight:700;line-height:1.4;margin-bottom:16px}}
.hero-pair{{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin:18px 0}}
.pair-person{{text-align:center;padding:14px 10px;background:rgba(255,255,255,0.04);border-radius:10px;border:1px solid var(--border)}}
.pair-name{{font-size:17px;font-weight:700;color:#fff;margin-bottom:4px}}
.pair-meta{{font-size:11px;color:var(--text-secondary);line-height:1.5}}
.pair-cross{{font-size:28px;color:var(--gold);font-weight:300}}

.score-gauge{{background:rgba(255,255,255,0.03);border-radius:12px;padding:22px 20px;margin:18px 0;text-align:center;border:1px solid var(--border)}}
.score-gauge-label{{font-size:11px;font-weight:700;color:var(--text-secondary);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}}
.score-gauge-value{{font-size:52px;font-weight:700;font-family:var(--font-mono);line-height:1;margin-bottom:6px}}
.score-gauge-stars{{font-size:18px;color:var(--amber);margin-bottom:6px;letter-spacing:3px}}
.score-gauge-verdict{{font-size:14px;color:var(--text-secondary)}}
.score-bar{{height:8px;border-radius:4px;background:var(--surface2);margin:14px 0 4px;overflow:hidden}}
.score-bar-fill{{height:100%;border-radius:4px;transition:width .6s}}

section.card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:22px;margin-bottom:18px}}
section.card h2{{font-size:19px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border)}}
section.card p{{color:#d1d5db;margin-bottom:12px;font-size:14px;line-height:1.85}}
section.card strong{{color:#fff}}
.intro-p{{font-size:13px;color:var(--text-secondary);line-height:1.85;margin-bottom:14px}}

.breakdown-grid{{display:flex;flex-direction:column;gap:14px;margin:14px 0}}
.bk-item{{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:14px 16px}}
.bk-head{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;flex-wrap:wrap;gap:8px}}
.bk-title{{font-size:15px;font-weight:700;color:#fff}}
.bk-weight{{font-size:10px;color:var(--text-muted);letter-spacing:.05em;text-transform:uppercase}}
.bk-score-row{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.bk-labels{{flex:1;font-size:12px;color:var(--text-secondary)}}
.bk-labels strong{{color:#c7d2fe;font-weight:500}}
.bk-score{{font-size:22px;font-weight:700;font-family:var(--font-mono);letter-spacing:-0.02em}}
.bk-narrative{{font-size:13px;color:#d1d5db;line-height:1.85;padding:10px 12px;background:rgba(99,102,241,0.05);border-left:3px solid rgba(99,102,241,0.3);border-radius:6px;margin-top:8px}}

.tier2-locked{{background:linear-gradient(135deg,rgba(99,102,241,0.05),rgba(255,255,255,0.02));border:1px dashed rgba(99,102,241,0.3);border-radius:10px;padding:16px 18px;margin-top:18px}}
.tier2-label{{font-size:10px;font-weight:700;color:#a5b4fc;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}}
.tier2-title{{font-size:15px;font-weight:700;color:#fff;margin-bottom:8px}}
.tier2-systems{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}}
.tier2-chip{{font-size:11px;padding:3px 10px;border-radius:12px;background:rgba(255,255,255,0.04);border:1px solid var(--border);color:var(--text-secondary)}}
.tier2-note{{font-size:12px;color:var(--text-muted);line-height:1.75}}

.callouts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}}
.callout{{padding:14px 16px;border-radius:10px;border:1px solid;border-left-width:3px}}
.callout-good{{background:rgba(34,197,94,0.06);border-color:rgba(34,197,94,0.25)}}
.callout-watch{{background:rgba(251,191,36,0.06);border-color:rgba(251,191,36,0.25)}}
.callout-title{{font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-bottom:8px}}
.callout-good .callout-title{{color:#86efac}}
.callout-watch .callout-title{{color:#fbbf24}}
.callout-body{{font-size:13px;color:#d1d5db;line-height:1.85}}

.sources-note{{font-size:10px;color:var(--text-muted);margin-top:16px;padding-top:12px;border-top:1px dashed rgba(255,255,255,0.08);line-height:1.7;font-style:italic}}

.signoff{{text-align:center;color:var(--text-muted);font-size:13px;padding:32px 0 0}}

@media(max-width:600px){{
  .hero-pair{{grid-template-columns:1fr}}
  .pair-cross{{text-align:center;padding:6px 0}}
  .callouts-grid{{grid-template-columns:1fr}}
  .score-gauge-value{{font-size:44px}}
}}
</style>
</head>
<body>
<nav class="top-nav"><div class="top-nav-inner"><a href="/insight/" class="brand">iUMA Self-Insight</a><span style="font-size:11px;color:var(--text-muted)">相性診断</span></div></nav>
<main class="container">

<div class="hero">
  <div class="hero-badge">Tier 1 相性診断 — 4体系統合</div>
  <h1>{name_a} × {name_b}</h1>
  <div class="hero-pair">
    <div class="pair-person">
      <div class="pair-name">{name_a}</div>
      <div class="pair-meta">{meta_a}</div>
    </div>
    <div class="pair-cross">×</div>
    <div class="pair-person">
      <div class="pair-name">{name_b}</div>
      <div class="pair-meta">{meta_b}</div>
    </div>
  </div>

  <div class="score-gauge">
    <div class="score-gauge-label">統合相性スコア（4体系加重平均）</div>
    <div class="score-gauge-value" style="color:{verdict_color}">{total}<span style="font-size:20px;color:var(--text-secondary)">/100</span></div>
    <div class="score-gauge-stars">{verdict_stars}</div>
    <div class="score-gauge-verdict">{verdict_label}</div>
    <div class="score-bar"><div class="score-bar-fill" style="width:{total}%;background:linear-gradient(to right,{verdict_color},#a5b4fc)"></div></div>
  </div>
</div>

<section class="card">
  <h2>📊 体系別ブレイクダウン</h2>
  <p class="intro-p">4つの独立した体系が、それぞれ別の角度から {name_a} と {name_b} の相性を読み解いています。重み付きの統合スコアが上の数値です。</p>

  <div class="breakdown-grid">
    {bk_bt}
    {bk_western}
    {bk_fp}
    {bk_eto}
  </div>
</section>

<section class="card">
  <h2>💡 この関係で起きやすいこと</h2>
  <div class="callouts-grid">
    <div class="callout callout-good">
      <div class="callout-title">◎ 噛み合う場面</div>
      <div class="callout-body">{good_insight}</div>
    </div>
    <div class="callout callout-watch">
      <div class="callout-title">⚠ 注意すべき場面</div>
      <div class="callout-body">{watch_insight}</div>
    </div>
  </div>
</section>

<section class="card">
  <h2>🔒 Tier 2 相性（解放予定）</h2>
  <p class="intro-p">4体系に心理学的パラメータを追加すると、相性の精度はさらに上がります。両者ともに性格アンケート（Tier 2）を完了すると、以下 5 体系の相性が解放されます:</p>
  <div class="tier2-locked">
    <div class="tier2-label">未解放（両者のTier 2完了で解放）</div>
    <div class="tier2-title">心理学的相性 5 体系</div>
    <div class="tier2-systems">
      <span class="tier2-chip">エニアグラム相性</span>
      <span class="tier2-chip">HSP 相性</span>
      <span class="tier2-chip">ADHD傾向 相性</span>
      <span class="tier2-chip">24 Strengths 相性（自前開発中）</span>
      <span class="tier2-chip">16 Archetypes 相性（自前開発中）</span>
    </div>
    <div class="tier2-note">4 + 5 = 9 体系統合で精度が桁違いに上がります。現在の Tier 1 スコアが「確度 60-70%」に対し、Tier 2 フル解放で「確度 90% 超」を目指します。</div>
  </div>
</section>

<section class="card">
  <h2>📚 算出根拠</h2>
  <div class="sources-note">
    <p>• 血液型相性: 日本の伝統的組み合わせ表。文化的参考値であり、科学的根拠は限定的（参考: 心理学研究では統計的相関は小さいとされる）</p>
    <p>• 西洋占星術相性: 元素（火/地/風/水）の親和性 + アスペクト（星座間の角度距離）。Astro.com / Cafe Astrology 等で用いられる古典的手法</p>
    <p>• 四柱推命相性: 日主五行の相生（generating）/ 相剋（controlling）/ 同元素関係 + 陰陽の補完性。中国古典《命理》に基づく</p>
    <p>• 干支相性: 三合（最強）/ 六合（調和）/ 冲（対立）の伝統的関係。東洋占術の標準</p>
    <p>• 統合スコア重み: 血液型 15% / 西洋 30% / 四柱推命 30% / 干支 25%</p>
  </div>
</section>

<p class="signoff">iUMA Self-Insight · Compatibility v0.1 · 2026-04-16</p>

</main></body></html>
'''


def render_bk_item(system_name_ja, weight_pct, data, score_color_fn):
    color = score_color_fn(data['score'])
    return f'''
<div class="bk-item">
  <div class="bk-head">
    <div class="bk-title">{system_name_ja}</div>
    <div class="bk-weight">重み {weight_pct}%</div>
  </div>
  <div class="bk-score-row">
    <div class="bk-labels"><strong>{data['label_a']}</strong> × <strong>{data['label_b']}</strong></div>
    <div class="bk-score" style="color:{color}">{data['score']}<span style="font-size:13px;color:var(--text-muted)">/100</span></div>
  </div>
  <div class="score-bar"><div class="score-bar-fill" style="width:{data['score']}%;background:{color}"></div></div>
  <div class="bk-narrative">{data['narrative']}</div>
</div>
'''


def score_color(s):
    if s >= 80: return '#86efac'
    if s >= 65: return '#fde68a'
    if s >= 50: return '#fbbf24'
    return '#fca5a5'


def build_insights(bt_d, west_d, fp_d, eto_d, total):
    """統合スコアと各サブスコアから「噛み合う」「注意」をテキスト生成"""
    scores = {'血液型': bt_d['score'], '西洋占星術': west_d['score'],
              '四柱推命': fp_d['score'], '干支': eto_d['score']}
    sorted_by_score = sorted(scores.items(), key=lambda x: -x[1])
    top_sys = sorted_by_score[0]
    bottom_sys = sorted_by_score[-1]

    if total >= 80:
        good = f'<strong>{top_sys[0]}</strong>で {top_sys[1]}点の強い合意。4体系の合意度が高く、自然に馬が合う関係。会話・価値観・リズムが合いやすい。'
        watch = f'ただし<strong>{bottom_sys[0]}</strong>で {bottom_sys[1]}点と低めの軸があり、ここは意識的にケアが必要。関係が良すぎると相手への甘えが出やすい点も注意。'
    elif total >= 65:
        good = f'<strong>{top_sys[0]}</strong>で {top_sys[1]}点の合意が支え。互いの強みを活かせる場面では相性よく機能する。'
        watch = f'<strong>{bottom_sys[0]}</strong>で {bottom_sys[1]}点と摩擦点あり。価値観のズレがここから起きやすいので、互いの違いを言語化して尊重する運用が鍵。'
    else:
        good = f'体系間で割れる難しい相性。唯一 <strong>{top_sys[0]}</strong>（{top_sys[1]}点）が接点を提供する。共通の関心や場面を意識的に作ると関係が深まる。'
        watch = f'<strong>{bottom_sys[0]}</strong>で {bottom_sys[1]}点と大きな摩擦。物事のペース・距離感・判断軸が根本的に違うので、正面からぶつけず「違う星から来た人」として接するのが正解。'

    return good, watch


def generate(profile_a_path, profile_b_path, output_path):
    A = load_profile(profile_a_path)
    B = load_profile(profile_b_path)

    name_a = A['identity'].get('name') or A['identity'].get('display_name') or 'A'
    name_b = B['identity'].get('name') or B['identity'].get('display_name') or 'B'
    bt_a = A['blood_type'].get('type', 'A')
    bt_b = B['blood_type'].get('type', 'A')
    sign_a = A['western_astrology']['sun_sign'].get('sign', 'Aries')
    sign_b = B['western_astrology']['sun_sign'].get('sign', 'Aries')
    dm_a = A['four_pillars']['day_master']
    dm_b = B['four_pillars']['day_master']
    animal_a = A['four_pillars']['year_pillar']['branch'].get('animal', 'Rat')
    animal_b = B['four_pillars']['year_pillar']['branch'].get('animal', 'Rat')

    # Compatibility calculations
    bt_d = bt_compat(bt_a, bt_b)
    west_d = western_compat(sign_a, sign_b)
    fp_d = fp_compat(dm_a, dm_b)
    eto_d = eto_compat(animal_a, animal_b)

    # Integrated score
    total = integrated_score({'bt': bt_d['score'], 'western': west_d['score'],
                              'fp': fp_d['score'], 'eto': eto_d['score']})
    verdict_stars, verdict_color, verdict_label = overall_verdict(total)

    # Meta lines
    from datetime import date as _date
    def _age(bd):
        try:
            y, m, d = map(int, bd.split('-'))
            today = _date.today()
            return today.year - y - ((today.month, today.day) < (m, d))
        except Exception:
            return ''
    meta_a = f'{bt_a}型 / {ANIMAL_JA.get(animal_a,animal_a)}年 / {dm_a.get("char","")}日主 / {SIGN_JA.get(sign_a,sign_a)}'
    meta_b = f'{bt_b}型 / {ANIMAL_JA.get(animal_b,animal_b)}年 / {dm_b.get("char","")}日主 / {SIGN_JA.get(sign_b,sign_b)}'

    # Breakdown items
    bk_bt      = render_bk_item('血液型 相性', 15, bt_d, score_color)
    bk_western = render_bk_item('西洋占星術 相性（元素 × アスペクト）', 30, west_d, score_color)
    bk_fp      = render_bk_item('四柱推命 相性（日主五行 × 陰陽）', 30, fp_d, score_color)
    bk_eto     = render_bk_item('干支 相性（三合・六合・冲）', 25, eto_d, score_color)

    good_insight, watch_insight = build_insights(bt_d, west_d, fp_d, eto_d, total)

    html = HTML_TEMPLATE.format(
        name_a=name_a, name_b=name_b,
        meta_a=meta_a, meta_b=meta_b,
        total=total,
        verdict_stars=verdict_stars, verdict_color=verdict_color, verdict_label=verdict_label,
        bk_bt=bk_bt, bk_western=bk_western, bk_fp=bk_fp, bk_eto=bk_eto,
        good_insight=good_insight, watch_insight=watch_insight,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Compatibility dashboard written to {output_path}')
    print(f'  {name_a} × {name_b} = {total}/100 ({verdict_label})')
    print(f'  Breakdown: bt={bt_d["score"]} / west={west_d["score"]} / fp={fp_d["score"]} / eto={eto_d["score"]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True, help='Path to profile A yaml')
    ap.add_argument('--b', required=True, help='Path to profile B yaml')
    ap.add_argument('--output', required=True, help='Output HTML path')
    args = ap.parse_args()
    generate(args.a, args.b, args.output)


if __name__ == '__main__':
    main()
