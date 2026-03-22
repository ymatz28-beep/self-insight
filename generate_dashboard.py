#!/usr/bin/env python3
"""Generate Self-Insight dashboard HTML from profile.yaml."""
import argparse, yaml, os, sys
from pathlib import Path

def load_profile(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_narratives(path):
    if not path:
        return {}
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}

def n(narratives, *keys, default=''):
    """Safe nested key access for narratives dict."""
    obj = narratives
    for k in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(k, default)
        if obj is None:
            return default
    return obj if obj is not None else default

def star_rating(val, max_val=5):
    full = int(val)
    return '★' * full + '☆' * (max_val - full)

def energy_bar_color(e):
    if e >= 70: return '#22c55e'
    if e >= 40: return '#eab308'
    return '#ef4444'

def generate_html(p, tier=2, narratives=None):
    from datetime import date as _date
    if narratives is None:
        narratives = {}
    name = p['identity']['name']
    birth = p['identity']['birth_date']
    age = p['identity'].get('age', '')
    blood = p['blood_type']['type']
    sex_label = {'male': '男性', 'female': '女性'}.get(p['identity'].get('sex', ''), '')
    gen_date = _date.today().isoformat()

    # Four Pillars
    fp = p['four_pillars']
    pillars = [fp['year_pillar'], fp['month_pillar'], fp['day_pillar']]
    dm = fp['day_master']
    elements = fp['five_elements_balance']
    missing = fp.get('missing_elements', [])

    # Nine Star Ki
    nsk = p['nine_star_ki']
    ys = nsk['year_star']
    ms = nsk['month_star']
    cycle9 = nsk.get('nine_year_cycle', [])

    # Rokusei
    rok = p['rokusei']
    cycle12 = rok.get('twelve_year_cycle', [])
    sub_cycle = rok.get('sub_star_cycle', [])
    combined = rok.get('reigou_combined', [])

    # Western
    west = p['western_astrology']['sun_sign']

    # Blood type
    bt = p['blood_type']

    # CliftonStrengths
    sf = p.get('strengths_finder', {})
    sf_top5 = sf.get('top5', [])
    sf_domains = sf.get('domain_distribution', {})

    # Personality (Tier 2)
    pers = p.get('personality', {})
    ennea = pers.get('enneagram', {})
    hsp = pers.get('hsp', {})
    adhd = pers.get('adhd', {})

    # Enneagram type names
    ennea_names = {1:'完璧主義者',2:'援助者',3:'達成者',4:'個性派',5:'観察者',6:'忠実家',7:'楽天家',8:'挑戦者',9:'調停者'}

    # HSP label mapping (supports both string and numeric)
    hsp_labels = {'low':'低感受性','medium':'中程度','high':'高感受性'}
    hsp_score_map = {'low': 8, 'medium': 18, 'high': 25}

    # ADHD label
    adhd_labels = {'minimal':'低傾向','leaning':'やや傾向あり','significant':'傾向あり'}
    adhd_tendency_map = {'minimal': 1, 'leaning': 3, 'significant': 5}

    # Current year cycle
    cur9 = next((c for c in cycle9 if c.get('current')), None)
    cur12 = next((c for c in cycle12 if c.get('current')), None)
    cur_sub = next((c for c in sub_cycle if c.get('current')), None) if sub_cycle else None
    cur_comb = next((c for c in combined if c.get('year') == 2026), None)

    # Build sub_cycle lookup by year for table alignment
    sub_by_year = {c['year']: c for c in sub_cycle} if sub_cycle else {}

    # Element bar data
    el_data = []
    for el_name in ['木','火','土','金','水']:
        info = elements.get(el_name, {})
        el_data.append({'name': el_name, 'pct': info.get('pct', 0), 'count': info.get('count', 0)})

    # Nine year cycle chart data
    chart9_labels = [str(c['year']) for c in cycle9]
    chart9_data = [c['energy'] for c in cycle9]

    # Twelve year cycle chart data
    chart12_labels = [str(c['year']) for c in cycle12]
    chart12_data = [c['energy'] for c in cycle12]

    # Combined chart
    comb_labels = [str(c['year']) for c in combined]
    comb_data = [c['score'] for c in combined]

    # CliftonStrengths section
    strengths_section = ''
    # Build narrative lookup for CliftonStrengths by name
    nar_top5_list = n(narratives, 'personality', 'clifton_top5', default=[]) or []
    nar_top5_map = {item['name']: item for item in nar_top5_list if isinstance(item, dict)}
    nar_clifton_intro = n(narratives, 'personality', 'clifton_intro', default='')

    if sf_top5:
        domain_colors = {'Relationship Building':'#22c55e','Strategic Thinking':'#6366f1','Executing':'#8b5cf6','Influencing':'#f59e0b'}
        sf_cards = ''
        for s in sf_top5:
            dc = domain_colors.get(s.get('domain',''), 'var(--accent)')
            nar_s = nar_top5_map.get(s['name'], {})
            desc_html = f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{nar_s["description"]}</div>' if nar_s.get('description') else ''
            name_jp = nar_s.get('name_jp', '')
            name_jp_html = f' <span style="font-size:13px;color:var(--text3)">({name_jp})</span>' if name_jp else ''
            sf_cards += f'''<div class="card" style="border-left:3px solid {dc}">
          <div class="card-label">#{s["rank"]}</div>
          <div class="card-value" style="font-size:18px">{s["name"]}{name_jp_html}</div>
          <div class="card-sub">{s["domain"]}</div>
          {desc_html}
        </div>'''
        # Domain distribution bars
        domain_bars = ''
        for dname, ranks in sf_domains.items():
            dc = domain_colors.get(dname, 'var(--accent)')
            top10_count = sum(1 for r in ranks if r <= 10)
            domain_bars += f'''<div class="el-row">
          <div style="width:120px;font-size:12px;color:var(--text2)">{dname}</div>
          <div class="el-bar-bg"><div class="el-bar" style="width:{len(ranks)/34*100:.0f}%;background:{dc}"></div></div>
          <div class="el-pct">{len(ranks)}</div>
        </div>'''
        clifton_intro_html = f'<p style="font-size:13px;color:var(--text2);margin-bottom:16px;line-height:1.6">{nar_clifton_intro}</p>' if nar_clifton_intro else ''
        strengths_section = f'''
    <section id="strengths">
      <h2 class="section-title">CliftonStrengths TOP5</h2>
      {clifton_intro_html}
      <div class="card-grid">{sf_cards}</div>
      <div style="margin-top:20px">
        <div class="card-label" style="font-size:12px;color:var(--text3);margin-bottom:10px">ドメイン分布（34資質中）</div>
        {domain_bars}
      </div>
    </section>'''

    personality_section = ''
    if tier >= 2 and ennea:
        etype = ennea.get('type', '?')
        ename = ennea_names.get(etype, '')
        ewing = ennea.get('wing', '')
        hsp_score_label = hsp_labels.get(hsp.get('score', ''), hsp.get('score', ''))
        # Support both numeric and string HSP scores
        hsp_total = hsp.get('total', hsp_score_map.get(hsp.get('score', ''), 0))
        hsp_max = hsp.get('max', 30)
        hsp_pct = int(hsp_total / hsp_max * 100) if hsp_max > 0 else 0
        adhd_label = adhd_labels.get(adhd.get('tendency', ''), adhd.get('tendency', ''))
        adhd_count = adhd.get('above_threshold_count', adhd_tendency_map.get(adhd.get('tendency', ''), 0))

        # Typology narratives
        nar_ennea = n(narratives, 'personality', 'typology', 'enneagram', default={})
        nar_blood = n(narratives, 'personality', 'typology', 'blood_type', default={})
        nar_hsp = n(narratives, 'personality', 'typology', 'hsp', default={})
        nar_adhd = n(narratives, 'personality', 'typology', 'adhd', default={})

        def desc_block(text):
            return f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{text}</div>' if text else ''

        personality_section = f'''
    <section id="personality">
      <h2 class="section-title">Personality Profile</h2>
      <div class="card-grid">
        <div class="card">
          <div class="card-label">エニアグラム</div>
          <div class="card-value">Type {etype}</div>
          <div class="card-sub">{ename}（Wing {ewing}）</div>
          <div class="card-detail" style="margin-top:8px;font-size:13px;color:var(--text2)">
            成長方向: Type {ennea.get("growth_direction","")} / ストレス方向: Type {ennea.get("stress_direction","")}
          </div>
          {desc_block(nar_ennea.get('description',''))}
        </div>
        <div class="card">
          <div class="card-label">HSP（感受性）</div>
          <div class="card-value">{hsp_score_label}</div>
          <div class="card-sub">スコア: {hsp_total}/{hsp_max}</div>
          <div class="mini-bar" style="margin-top:10px">
            <div class="mini-bar-fill" style="width:{hsp_pct}%;background:var(--accent)"></div>
          </div>
          {desc_block(nar_hsp.get('description',''))}
        </div>
        <div class="card">
          <div class="card-label">注意特性（ADHD傾向）</div>
          <div class="card-value">{adhd_label}</div>
          <div class="card-sub">閾値超え: {adhd_count}/6項目</div>
          {desc_block(nar_adhd.get('description',''))}
        </div>
        <div class="card">
          <div class="card-label">血液型</div>
          <div class="card-value">{blood}型</div>
          <div class="card-sub">日本人の{bt["population_pct"]}%</div>
          {desc_block(nar_blood.get('description',''))}
        </div>
      </div>
    </section>'''

    locked_section = ''
    core_id = n(narratives, 'core_identity', default={})
    ci_insight = n(narratives, 'core_identity', 'integrated_insight', default={})
    ci_cards = n(narratives, 'core_identity', 'summary_cards', default={})

    if tier >= 3:
        p1 = ci_insight.get('paragraph_1_essence', '')
        p2 = ci_insight.get('paragraph_2_depth', '')
        p3 = ci_insight.get('paragraph_3_duality', '')
        p4 = ci_insight.get('paragraph_4_watch_out', '')
        para_html = ''
        for para in [p1, p2, p3, p4]:
            if para:
                para_html += f'<p style="margin-bottom:16px;font-size:14px;line-height:1.7;color:var(--text2)">{para}</p>'

        def summary_card(key, default_title='', default_sub=''):
            c = ci_cards.get(key, {})
            title = c.get('title', default_title)
            subtitle = c.get('subtitle', default_sub)
            return f'''<div class="card">
              <div class="card-label" style="font-size:10px">{key.replace('_',' ').upper()}</div>
              <div class="card-value" style="font-size:16px">{title}</div>
              <div class="card-sub">{subtitle}</div>
            </div>''' if title else ''

        sum_cards_html = (
            summary_card('core_essence') +
            summary_card('strongest_axis') +
            summary_card('duality') +
            summary_card('watch_out')
        )

        locked_section = f'''
    <section id="core-identity" style="margin:32px 0">
      <h2 class="section-title">統合インサイト — Core Identity</h2>
      <div class="card-grid" style="margin-bottom:20px">{sum_cards_html}</div>
      <div class="card" style="padding:24px">
        {para_html if para_html else '<p style="color:var(--text3)">統合インサイトを読み込み中...</p>'}
      </div>
    </section>'''
    else:
        locked_section = '''
    <section id="locked" style="position:relative;margin:32px 0">
      <div style="filter:blur(6px);opacity:0.4;pointer-events:none">
        <h2 class="section-title">統合インサイト — Core Identity</h2>
        <div class="card" style="padding:24px"><p>全体系を統合したあなたの人物像がここに表示されます。占術・性格分析・特性を掛け合わせた独自の統合分析...</p></div>
      </div>
      <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--accent);color:#fff;padding:12px 24px;border-radius:8px;font-weight:600;font-size:14px;z-index:10;text-align:center">
        Tier 3（Big Five +20問）で解放
      </div>
    </section>'''

    # --- Pre-build forecast/monthly/cross HTML sections ---

    # Year overview
    _year_overview = n(narratives, 'forecast_2026', 'year_overview')
    _year_overview_html = (
        f'<div class="card" style="margin-top:16px;padding:20px">'
        f'<div class="card-label" style="margin-bottom:10px">年間概観</div>'
        f'<p style="font-size:13px;color:var(--text2);line-height:1.7">{_year_overview}</p>'
        f'</div>'
    ) if _year_overview else ''

    # Keywords
    _kw_list = n(narratives, 'forecast_2026', 'keywords', default=[]) or []
    _kw_cards = ''.join(
        f'<div class="card">'
        f'<div class="card-value" style="font-size:15px">{kw["title"]}</div>'
        f'<div class="card-sub" style="font-size:12px;margin-top:6px;line-height:1.5">{kw.get("description","")}</div>'
        f'</div>'
        for kw in _kw_list if isinstance(kw, dict)
    )
    _keywords_html = (
        f'<div style="margin-top:20px">'
        f'<div class="card-label" style="font-size:12px;color:var(--text3);margin-bottom:12px">2026年 キーワード</div>'
        f'<div class="card-grid">{_kw_cards}</div>'
        f'</div>'
    ) if _kw_cards else ''

    # Three system alignment
    _3sys = n(narratives, 'forecast_2026', 'three_system_alignment')
    _3sys_html = (
        f'<div style="margin-top:20px">'
        f'<div class="card-label" style="font-size:12px;color:var(--text3);margin-bottom:12px">3システム整合性分析</div>'
        f'<div class="card" style="padding:18px"><p style="font-size:13px;color:var(--text2);line-height:1.7">{_3sys}</p></div>'
        f'</div>'
    ) if _3sys else ''

    # Guidance by domain
    _guidance = n(narratives, 'forecast_2026', 'guidance', default={}) or {}
    _guidance_domain_cards = ''
    _domain_label_map = {'work': '仕事', 'money': 'お金', 'health': '健康', 'romance': '恋愛'}
    for _domain, _items in _guidance.items():
        if isinstance(_items, list):
            _li = ''.join(
                f'<li style="font-size:12px;color:var(--text2);line-height:1.6;margin-bottom:4px">{item}</li>'
                for item in _items
            )
            _domain_label = _domain_label_map.get(_domain, _domain)
            _guidance_domain_cards += (
                f'<div class="card">'
                f'<div class="card-label">{_domain_label}</div>'
                f'<ul style="padding-left:16px;margin-top:6px">{_li}</ul>'
                f'</div>'
            )
    _guidance_html = (
        f'<div style="margin-top:20px">'
        f'<div class="card-label" style="font-size:12px;color:var(--text3);margin-bottom:12px">分野別ガイダンス</div>'
        f'<div class="card-grid">{_guidance_domain_cards}</div>'
        f'</div>'
    ) if _guidance_domain_cards else ''

    forecast_extra_html = _year_overview_html + _keywords_html + _3sys_html + _guidance_html

    # Monthly Fortune section
    _monthly_list = n(narratives, 'monthly_2026', default=[]) or []
    if _monthly_list:
        _month_cards = ''
        for m in _monthly_list:
            if not isinstance(m, dict):
                continue
            _domain_blocks = ''
            _domain_names = {'work': '仕事', 'money': 'お金', 'health': '健康', 'romance': '恋愛'}
            for _dom in ['work', 'money', 'health', 'romance']:
                _ddata = m.get(_dom)
                if isinstance(_ddata, dict):
                    _stars = '★' * int(_ddata.get('stars', 0)) + '☆' * (5 - int(_ddata.get('stars', 0)))
                    _dname = _domain_names.get(_dom, _dom)
                    _domain_blocks += (
                        f'<div style="background:var(--surface2);border-radius:8px;padding:10px">'
                        f'<div class="card-label" style="font-size:10px">{_dname}</div>'
                        f'<div style="font-size:16px;margin:4px 0">{_stars}</div>'
                        f'<div style="font-size:12px;color:var(--text2);line-height:1.5">{_ddata.get("text","")}</div>'
                        f'</div>'
                    )
            _insight_html = (
                f'<div style="background:rgba(99,102,241,0.08);border-left:3px solid var(--accent);'
                f'padding:12px;border-radius:4px;font-size:12px;color:var(--text2);line-height:1.6">'
                f'{m["insight"]}</div>'
            ) if m.get('insight') else ''
            _nine_note = m.get('nine_star_note', '')
            _rok_phase = m.get('rokusei_phase', '')
            _month_cards += (
                f'<div class="card" style="padding:20px">'
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
                f'<div style="font-size:18px;font-weight:700;font-family:var(--mono)">{m.get("month","")}</div>'
                f'<div style="font-size:12px;color:var(--text3)">{_nine_note}</div>'
                f'<div style="font-size:12px;color:var(--text3)">{_rok_phase}</div>'
                f'</div>'
                f'<div class="card-grid" style="grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px">'
                f'{_domain_blocks}'
                f'</div>'
                f'{_insight_html}'
                f'</div>'
            )
        monthly_section_html = (
            f'<section id="monthly">'
            f'<h2 class="section-title">月別運勢（2026年）</h2>'
            f'<div style="display:flex;flex-direction:column;gap:16px">{_month_cards}</div>'
            f'</section>'
        )
    else:
        monthly_section_html = ''

    # Cross Analysis section
    _cross_list = n(narratives, 'cross_analysis', default=[]) or []
    if _cross_list:
        _cross_cards = ''
        for item in _cross_list:
            if not isinstance(item, dict):
                continue
            _practice = (
                f'<div style="background:rgba(34,197,94,0.06);border-left:3px solid var(--green);'
                f'padding:12px;border-radius:4px">'
                f'<div class="card-label" style="font-size:10px;color:var(--green);margin-bottom:6px">実践ガイド</div>'
                f'<p style="font-size:12px;color:var(--text2);line-height:1.6">{item["practice_guide"]}</p>'
                f'</div>'
            ) if item.get('practice_guide') else ''
            _cross_cards += (
                f'<div class="card" style="padding:20px">'
                f'<div class="card-value" style="font-size:16px;margin-bottom:12px">{item.get("title","")}</div>'
                f'<div style="margin-bottom:12px">'
                f'<div class="card-label" style="font-size:10px;margin-bottom:6px">分析</div>'
                f'<p style="font-size:13px;color:var(--text2);line-height:1.6">{item.get("analysis","")}</p>'
                f'</div>'
                f'{_practice}'
                f'</div>'
            )
        cross_section_html = (
            f'<section id="cross-analysis">'
            f'<h2 class="section-title">クロス分析</h2>'
            f'<div style="display:flex;flex-direction:column;gap:16px">{_cross_cards}</div>'
            f'</section>'
        )
    else:
        cross_section_html = ''

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Self-Insight — {name}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+JP:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root {{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2d3348;
  --accent:#6366f1;--accent2:#8b5cf6;--green:#22c55e;--red:#ef4444;--yellow:#eab308;
  --text:#e4e4e7;--text2:#9ca3af;--text3:#7c8293;
  --font:Inter,'Noto Sans JP',sans-serif;--mono:'JetBrains Mono',monospace;
  --r:12px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{font-size:16px;scroll-behavior:smooth;scroll-padding-top:60px}}
body{{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh;-webkit-font-smoothing:antialiased}}
.container{{max-width:900px;margin:0 auto;padding:20px 16px 80px}}

/* Nav */
.nav{{position:sticky;top:0;z-index:100;background:rgba(15,17,23,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);display:flex;justify-content:center;gap:4px;padding:0 16px;overflow-x:auto;scrollbar-width:none}}
.nav::-webkit-scrollbar{{display:none}}
.nav a{{color:var(--text3);text-decoration:none;font-size:12px;font-weight:500;padding:14px 14px;white-space:nowrap;transition:color .2s}}
.nav a:hover{{color:var(--text)}}

/* Hero */
.hero{{text-align:center;padding:32px 0 20px}}
.hero h1{{font-size:clamp(22px,3.5vw,30px);font-weight:700;background:linear-gradient(135deg,var(--accent2),var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero .sub{{color:var(--text2);font-size:14px;margin-top:4px}}
.chips{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:16px}}
.chip{{background:var(--surface);border:1px solid var(--border);padding:6px 14px;border-radius:20px;font-size:12px;color:var(--text2)}}
.chip b{{color:var(--text)}}

/* Section */
.section-title{{font-size:clamp(16px,2.5vw,20px);font-weight:700;margin:32px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--border)}}

/* Cards */
.card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:18px}}
.card-label{{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}}
.card-value{{font-size:22px;font-weight:700;font-family:var(--mono)}}
.card-sub{{font-size:13px;color:var(--text2);margin-top:2px}}
.card-detail{{font-size:12px;color:var(--text3)}}

/* Pillar cards */
.pillar-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.pillar{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px;text-align:center}}
.pillar .label{{font-size:11px;color:var(--text3)}}
.pillar .kanji{{font-size:28px;font-weight:700;margin:6px 0}}
.pillar .detail{{font-size:12px;color:var(--text2)}}

/* Element bar */
.el-row{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.el-name{{width:24px;font-size:14px;font-weight:600;text-align:center}}
.el-bar-bg{{flex:1;height:8px;background:var(--surface2);border-radius:4px;overflow:hidden}}
.el-bar{{height:100%;border-radius:4px;transition:width .5s}}
.el-pct{{width:36px;font-size:12px;color:var(--text2);font-family:var(--mono);text-align:right}}

/* Mini bar */
.mini-bar{{height:6px;background:var(--surface2);border-radius:3px;overflow:hidden}}
.mini-bar-fill{{height:100%;border-radius:3px}}

/* Cycle table */
.cycle-table{{width:100%;border-collapse:collapse;font-size:13px}}
.cycle-table th{{text-align:left;padding:8px 10px;color:var(--text3);font-weight:500;border-bottom:1px solid var(--border)}}
.cycle-table td{{padding:8px 10px;border-bottom:1px solid rgba(45,51,72,.5)}}
.cycle-table tr.current{{background:rgba(99,102,241,.08)}}
.cycle-table .殺界{{font-size:11px;padding:2px 8px;border-radius:10px;font-weight:600}}
.dai{{background:rgba(239,68,68,.15);color:var(--red)}}
.chu{{background:rgba(234,179,8,.15);color:var(--yellow)}}
.sho{{background:rgba(234,179,8,.1);color:var(--yellow)}}

/* Chart */
.chart-wrap{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:16px;margin:16px 0}}

/* Footer */
footer{{text-align:center;padding:40px 0 20px;font-size:12px;color:var(--text3)}}

@media(max-width:600px){{
  .card-grid{{grid-template-columns:1fr}}
  .pillar-grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<nav class="nav">
  {"<a href='#strengths'>Strengths</a>" if sf_top5 else ""}
  <a href="#pillars">四柱推命</a>
  <a href="#ninestar">九星気学</a>
  <a href="#rokusei">六星占術</a>
  <a href="#western">西洋占星術</a>
  {"<a href='#personality'>性格</a>" if tier >= 2 else ""}
  {"<a href='#core-identity'>統合</a>" if tier >= 3 else ""}
  <a href="#forecast">2026運勢</a>
  {"<a href='#monthly'>月別</a>" if n(narratives,'monthly_2026') else ""}
  {"<a href='#cross-analysis'>クロス分析</a>" if n(narratives,'cross_analysis') else ""}
</nav>

<div class="container">

  <!-- Hero -->
  <div class="hero">
    <h1>{name} — Self-Insight</h1>
    <div class="sub">{birth}（{age}歳）{" / " + sex_label if sex_label else ""}</div>
    <div class="chips">
      <div class="chip"><b>{west["symbol"]} {west["sign"]}</b></div>
      <div class="chip"><b>{ys["name"]}</b></div>
      <div class="chip"><b>{rok["main_star"]["name"]}({rok["main_star"]["polarity"]})</b>{"霊合" if rok.get("reigou") else ""}</div>
      <div class="chip"><b>{blood}型</b></div>
      {f'<div class="chip"><b>Type {ennea.get("type","")}</b> {ennea_names.get(ennea.get("type",""),"")}</div>' if tier >= 2 and ennea else ''}
    </div>
  </div>

  {strengths_section}

  <!-- Four Pillars -->
  <section id="pillars">
    <h2 class="section-title">四柱推命</h2>
    {f'<p style="font-size:13px;color:var(--text2);margin-bottom:16px;line-height:1.6">{n(narratives,"divination","four_pillars","intro")}</p>' if n(narratives,"divination","four_pillars","intro") else ''}
    <div class="pillar-grid">
      {"".join(f"""
      <div class="pillar">
        <div class="label">{"年柱" if i==0 else "月柱" if i==1 else "日柱"}</div>
        <div class="kanji">{pl["full"]}</div>
        <div class="detail">{pl["stem"]["char"]}({pl["stem"]["element"]}) {pl["branch"]["char"]}({pl["branch"]["animal"]})</div>
      </div>""" for i, pl in enumerate(pillars))}
    </div>

    <div style="margin-top:16px">
      <div class="card">
        <div class="card-label">日主（Day Master）</div>
        <div class="card-value">{dm["char"]}（{dm["element"]}）</div>
        <div class="card-sub">{dm["description"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","four_pillars","day_master")}</div>' if n(narratives,"divination","four_pillars","day_master") else ''}
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text3);line-height:1.5">{n(narratives,"divination","four_pillars","pillar_details")}</div>' if n(narratives,"divination","four_pillars","pillar_details") else ''}
      </div>
    </div>

    <div style="margin-top:16px">
      <div class="card-label" style="font-size:12px;color:var(--text3);margin-bottom:8px">五行バランス</div>
      {"".join(f"""
      <div class="el-row">
        <div class="el-name">{ed["name"]}</div>
        <div class="el-bar-bg"><div class="el-bar" style="width:{ed["pct"]}%;background:{'#22c55e' if ed['pct']>0 else 'var(--surface2)'}"></div></div>
        <div class="el-pct">{ed["pct"]}%</div>
      </div>""" for ed in el_data)}
      {f'<div style="font-size:12px;color:var(--yellow);margin-top:8px">欠如: {"・".join(missing)}{" — " + fp.get("element_insight","") if fp.get("element_insight") else ""}</div>' if missing else ''}
    </div>
  </section>

  <!-- Nine Star Ki -->
  <section id="ninestar">
    <h2 class="section-title">九星気学</h2>
    <div class="card-grid">
      <div class="card">
        <div class="card-label">本命星（年星）</div>
        <div class="card-value">{ys["name"]}</div>
        <div class="card-sub">{ys["element"]} / {ys["direction"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","nine_star_ki","honmei")}</div>' if n(narratives,"divination","nine_star_ki","honmei") else ''}
      </div>
      <div class="card">
        <div class="card-label">月命星</div>
        <div class="card-value">{ms["name"]}</div>
        <div class="card-sub">{ms["element"]} / {ms["direction"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","nine_star_ki","getsu")}</div>' if n(narratives,"divination","nine_star_ki","getsu") else ''}
      </div>
      {f"""<div class="card">
        <div class="card-label">2026年 宮位置</div>
        <div class="card-value">{cur9["palace"]}</div>
        <div class="card-sub">{cur9["theme"]}（エネルギー {cur9["energy"]}）</div>
      </div>""" if cur9 else ""}
    </div>
    <div class="chart-wrap">
      <canvas id="chart9" height="200"></canvas>
    </div>
  </section>

  <!-- Rokusei -->
  <section id="rokusei">
    <h2 class="section-title">六星占術</h2>
    <div class="card-grid">
      <div class="card">
        <div class="card-label">運命星</div>
        <div class="card-value">{rok["main_star"]["name"]}({rok["main_star"]["polarity"]})</div>
        <div class="card-sub">{rok["main_star"]["reading"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","rokusei","jupiter")}</div>' if n(narratives,"divination","rokusei","jupiter") else ''}
      </div>
      {f"""<div class="card">
        <div class="card-label">霊合サブ星</div>
        <div class="card-value">{rok["sub_star"]["name"]}({rok["sub_star"]["polarity"]})</div>
        <div class="card-sub">{rok["sub_star"]["reading"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","rokusei","venus")}</div>' if n(narratives,"divination","rokusei","venus") else ''}
      </div>""" if rok.get("reigou") and rok.get("sub_star") else ""}
      {f"""<div class="card">
        <div class="card-label">2026年</div>
        <div class="card-value">{cur12["phase"]}</div>
        <div class="card-sub">{"<span class='殺界 dai'>"+cur12["殺界"]+"</span>" if cur12.get("殺界") and "大" in str(cur12["殺界"]) else "<span class='殺界 chu'>"+cur12["殺界"]+"</span>" if cur12.get("殺界") and "中" in str(cur12["殺界"]) else "<span class='殺界 sho'>"+cur12["殺界"]+"</span>" if cur12.get("殺界") else "好調期"}（エネルギー {cur12["energy"]}）</div>
      </div>""" if cur12 else ""}
      {f"""<div class="card">
        <div class="card-label">霊合星人とは</div>
        <div class="card-detail" style="font-size:12px;color:var(--text2);line-height:1.5;margin-top:4px">{n(narratives,"divination","rokusei","reigo")}</div>
      </div>""" if rok.get("reigou") and n(narratives,"divination","rokusei","reigo") else ""}
    </div>

    {f"""<div class="chart-wrap">
      <canvas id="chartComb" height="200"></canvas>
    </div>""" if combined else ""}

    <div style="margin-top:12px">
      <table class="cycle-table">
        <thead><tr><th>年</th><th>メイン</th>{f"<th>サブ</th>" if rok.get("reigou") else ""}<th>殺界</th><th>Energy</th></tr></thead>
        <tbody>
        {"".join(f"""<tr class="{'current' if c.get('current') else ''}">
          <td>{c['year']}</td>
          <td>{c['phase']}</td>
          {f"<td>{sub_by_year[c['year']]['phase'] if c['year'] in sub_by_year else '—'}</td>" if rok.get("reigou") else ""}
          <td>{f"<span class='殺界 dai'>{c['殺界']}</span>" if c.get('殺界') and '大' in str(c['殺界']) else f"<span class='殺界 chu'>{c['殺界']}</span>" if c.get('殺界') and '中' in str(c['殺界']) else f"<span class='殺界 sho'>{c['殺界']}</span>" if c.get('殺界') else '—'}</td>
          <td><span style="color:{energy_bar_color(c['energy'])}">{c['energy']}</span></td>
        </tr>""" for i, c in enumerate(cycle12))}
        </tbody>
      </table>
    </div>
  </section>

  <!-- Western -->
  <section id="western">
    <h2 class="section-title">西洋占星術</h2>
    <div class="card-grid">
      <div class="card">
        <div class="card-label">太陽星座</div>
        <div class="card-value">{west["symbol"]} {west["sign"]}</div>
        <div class="card-sub">{west["element"]} / {west["quality"]}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","western","summary")}</div>' if n(narratives,"divination","western","summary") else ''}
      </div>
      <div class="card">
        <div class="card-label">支配星</div>
        <div class="card-value">{p["western_astrology"].get("ruling_planet","")}</div>
        {f'<div class="card-detail" style="margin-top:8px;font-size:12px;color:var(--text2);line-height:1.5">{n(narratives,"divination","western","detail")}</div>' if n(narratives,"divination","western","detail") else ''}
      </div>
    </div>
  </section>

  <!-- Personality (Tier 2) -->
  {personality_section}

  <!-- Locked (Tier 3) -->
  {locked_section}

  <!-- 2026 Forecast -->
  <section id="forecast">
    <h2 class="section-title">2026年 運勢サマリ</h2>
    <div class="card-grid">
      {f"""<div class="card">
        <div class="card-label">九星気学</div>
        <div class="card-value">{cur9["palace"]}</div>
        <div class="card-sub">{cur9["theme"]}</div>
      </div>""" if cur9 else ""}
      {f"""<div class="card">
        <div class="card-label">六星占術（メイン）</div>
        <div class="card-value">{cur12["phase"]}</div>
        <div class="card-sub">Energy {cur12["energy"]}</div>
      </div>""" if cur12 else ""}
      {f"""<div class="card">
        <div class="card-label">六星占術（サブ）</div>
        <div class="card-value">{cur_sub["phase"]}</div>
        <div class="card-sub">{"<span class='殺界 dai'>"+cur_sub["殺界"]+"</span>" if cur_sub.get("殺界") and "大" in str(cur_sub["殺界"]) else "Energy "+str(cur_sub["energy"])}</div>
      </div>""" if cur_sub else ""}
      {f"""<div class="card">
        <div class="card-label">霊合統合スコア</div>
        <div class="card-value" style="color:{'var(--green)' if cur_comb['score']>=70 else 'var(--yellow)' if cur_comb['score']>=40 else 'var(--red)'}">{cur_comb["score"]}</div>
        <div class="card-sub">{cur_comb["label"]}</div>
      </div>""" if cur_comb else ""}
    </div>

    {forecast_extra_html}
  </section>

  {monthly_section_html}

  {cross_section_html}

  <footer>
    AI Self-Insight v0.5 — Generated {gen_date}<br>
    Powered by 四柱推命 × 九星気学 × 六星占術 × 西洋占星術 {"× エニアグラム × HSP × ADHD" if tier >= 2 else ""}
  </footer>

</div>

<script>
// Nine Star Ki 9-year cycle
new Chart(document.getElementById('chart9'), {{
  type: 'line',
  data: {{
    labels: {chart9_labels},
    datasets: [{{
      label: '九星気学 Energy',
      data: {chart9_data},
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 5,
      pointBackgroundColor: [{','.join("'#22c55e'" if c.get('current') else "'#6366f1'" for c in cycle9)}]
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#9ca3af' }}, grid: {{ color: 'rgba(45,51,72,0.5)' }} }},
      y: {{ min: 0, max: 100, ticks: {{ color: '#9ca3af' }}, grid: {{ color: 'rgba(45,51,72,0.5)' }} }}
    }}
  }}
}});

// Rokusei combined chart
{f"""new Chart(document.getElementById('chartComb'), {{
  type: 'line',
  data: {{
    labels: {comb_labels},
    datasets: [{{
      label: '霊合統合スコア',
      data: {comb_data},
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139,92,246,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 5,
      pointBackgroundColor: [{','.join("'#22c55e'" if c.get('year')==2026 else "'#8b5cf6'" for c in combined)}]
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#9ca3af' }}, grid: {{ color: 'rgba(45,51,72,0.5)' }} }},
      y: {{ min: 0, max: 100, ticks: {{ color: '#9ca3af' }}, grid: {{ color: 'rgba(45,51,72,0.5)' }} }}
    }}
  }}
}});""" if combined else ""}
</script>
</body>
</html>'''
    return html

def main():
    parser = argparse.ArgumentParser(description='Generate Self-Insight Dashboard')
    parser.add_argument('--profile', required=True, help='Path to profile.yaml')
    parser.add_argument('--output', required=True, help='Output HTML path')
    parser.add_argument('--tier', type=int, default=2, help='Completed tier (1, 2, or 3)')
    parser.add_argument('--narratives', default=None, help='Path to narratives.yaml (optional)')
    args = parser.parse_args()

    profile = load_profile(args.profile)
    narratives = load_narratives(args.narratives)
    html = generate_html(profile, tier=args.tier, narratives=narratives)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(html)
    nar_msg = f' + narratives from {args.narratives}' if args.narratives else ''
    print(f'Dashboard written to {args.output}{nar_msg}')

if __name__ == '__main__':
    main()
