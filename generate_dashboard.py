#!/usr/bin/env python3
"""Generate Self-Insight dashboard HTML from profile.yaml."""
import argparse, yaml, os, json
from datetime import date as _date

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def star_html(n, mx=5):
    return (f'<span style="color:var(--yellow);">{"★"*int(n)}</span>'
            f'<span style="color:var(--border);">{"★"*(mx-int(n))}</span>')

def energy_color(e):
    if e >= 70: return '#4ade80'
    if e >= 40: return '#facc15'
    return '#f87171'

def satsukai_html(s):
    if not s: return '—'
    cls = 'dai' if '大' in str(s) else 'chu' if '中' in str(s) else 'sho'
    return f'<span class="satsukai {cls}">{s}</span>'

ENNEA_NAMES = {1:'完璧主義者',2:'援助者',3:'達成者',4:'個性派',5:'観察者',
               6:'忠実家',7:'楽天家',8:'挑戦者',9:'調停者'}
HSP_LABELS = {'low':'穏やか','medium':'中程度','high':'繊細'}
ADHD_LABELS = {'minimal':'安定型','leaning':'やや多動','significant':'多動型'}

# Private nav — order from design-system.md SSOT
GNAV_LINKS = [
    ('Stock', 'https://iuma-private.pages.dev/stock/portfolio.html'),
    ('Market Intel', 'https://iuma-private.pages.dev/stock/market-intel.html'),
    ('Insight', 'https://iuma-private.pages.dev/intel/'),
    ('Wealth', 'https://iuma-private.pages.dev/wealth/dashboard.html'),
    ('Action', 'https://iuma-private.pages.dev/action/'),
    ('Self-Insight', 'https://ymatz28-beep.github.io/self-insight/'),
    ('Health', 'https://iuma-private.pages.dev/health/'),
    ('Property', 'https://ymatz28-beep.github.io/property-report/'),
    ('Travel', 'https://ymatz28-beep.github.io/trip-planner/'),
    ('Newsletter', 'https://iuma-private.pages.dev/newsletter/'),
]


def _gnav():
    links = '\n    '.join(
        f'<a href="{url}"{" aria-current=page" if label=="Self-Insight" else ""}>{label}</a>'
        for label, url in GNAV_LINKS)
    return f'''<header class="site-header">
  <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation">
  <label for="nav-toggle" class="nav-toggle-label"><span></span></label>
  <nav class="site-nav">
    {links}
  </nav>
</header>'''


def _section_nav(has_personality):
    links = '<a href="#core-identity">Core Identity</a>'
    if has_personality:
        links += '<a href="#personality">Personality</a>'
    links += '<a href="#divination">占術プロファイル</a>'
    links += '<a href="#forecast-2026">2026 運勢</a>'
    links += '<a href="#monthly">月間運勢</a>'
    links += '<a href="#cross">Cross Analysis</a>'
    return f'<nav class="nav-bar">{links}</nav>'


def _hero(p, tier):
    ident = p['identity']
    west = p['western_astrology']['sun_sign']
    ys = p['nine_star_ki']['year_star']
    rok = p['rokusei']
    blood = p['blood_type']['type']
    ennea = p.get('personality', {}).get('enneagram', {})

    chips = [
        f'<span class="chip hl">{p["four_pillars"]["day_master"]["char"]}火 陰火</span>',
        f'<span class="chip hl">{ys["name"]}</span>',
        f'<span class="chip hl">{west["symbol"]} {west["sign"]}</span>',
        f'<span class="chip">{rok["main_star"]["name"]}({rok["main_star"]["polarity"]}){"霊合" if rok.get("reigou") else ""}</span>',
        f'<span class="chip">{blood}型</span>',
    ]
    if tier >= 2 and ennea:
        chips.append(f'<span class="chip">Enneagram {ennea.get("type","")}</span>')
    sf_top1 = (p.get('strengths_finder', {}).get('top5', [None]) or [None])[0]
    if sf_top1:
        chips.append(f'<span class="chip">{sf_top1["name"]} #1</span>')

    # Stat cards
    cur9 = next((c for c in p['nine_star_ki'].get('nine_year_cycle', []) if c.get('current')), None)
    cur12 = next((c for c in rok.get('twelve_year_cycle', []) if c.get('current')), None)
    stats = ''
    stats += '<div class="stat-card"><div class="label">Core Identity</div>'
    stats += f'<div class="value" style="color:#f87171">{p["four_pillars"]["day_master"]["char"]}火</div></div>'
    if cur9 and cur12:
        stats += '<div class="stat-card"><div class="label">2026 Phase</div>'
        stats += f'<div class="value" style="color:#a5b4fc">{cur9["palace"]}×{cur12["phase"]}</div></div>'
    cur_comb = next((c for c in rok.get('reigou_combined', []) if c.get('year') == 2026), None)
    if cur_comb:
        stats += f'<div class="stat-card"><div class="label">Combined Score</div>'
        stats += f'<div class="value" style="color:{energy_color(cur_comb["score"])}">{cur_comb["score"]}</div></div>'

    return f'''<section class="hero">
  <h1>Self-Insight</h1>
  <div class="subtitle">{ident["name"]} — AI Self-Insight Dashboard</div>
  <div class="hero-chips">{"".join(chips)}</div>
  <div class="stats">{stats}</div>
</section>'''


def _core_identity(p):
    dm = p['four_pillars']['day_master']
    ys = p['nine_star_ki']['year_star']
    missing = p['four_pillars'].get('missing_elements', [])
    interp = p.get('interpretations', {})

    # Integrated insight box
    insight_paras = interp.get('integrated_insight', [])
    insight_html = ''
    if insight_paras:
        ps = ''.join(f'<p style="line-height:1.9;font-size:14px;{" margin-top:12px;" if i else ""}">{para}</p>'
                     for i, para in enumerate(insight_paras))
        insight_html = f'''<div class="insight-box" style="border-color:rgba(99,102,241,0.4);background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.08));">
    <div class="insight-title" style="font-size:15px;">統合インサイト</div>
    {ps}
  </div>'''

    return f'''<section class="section" id="core-identity">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(99,102,241,0.15);color:#a5b4fc">&#9733;</div>
    <div><h2>Core Identity — あなたはこういう人</h2>
      <div class="pillar-sub">6つの分析体系が示す、時代を超えた人物像</div></div>
  </div>
  {insight_html}
  <div class="grid grid-4" style="margin-top:16px">
    <div class="card tc"><div class="card-label">Core Essence</div>
      <div class="card-value">{dm["char"]}火 × {ys["name"]}</div>
      <div class="card-sub">静かな炎 × 言葉の力</div></div>
    <div class="card tc"><div class="card-label">Strongest Axis</div>
      <div class="card-value">共感 × 洞察</div>
      <div class="card-sub">Empathy + Intellection + 繊細さ</div></div>
    <div class="card tc"><div class="card-label">Duality</div>
      <div class="card-value">合理 × 感性</div>
      <div class="card-sub">AB型 × 霊合星人 × Enneagram 4</div></div>
    <div class="card tc"><div class="card-label">Watch Out</div>
      <div class="card-value" style="color:var(--yellow)">{("・".join(str(m) for m in missing)) if missing else "—"}の欠如</div>
      <div class="card-sub">決断力 × 柔軟性を意識的に補う</div></div>
  </div>
</section>'''


def _personality(p, tier):
    if tier < 2:
        return ''
    pers = p.get('personality', {})
    ennea = pers.get('enneagram', {})
    hsp = pers.get('hsp', {})
    adhd = pers.get('adhd', {})
    bt = p['blood_type']
    sf = p.get('strengths_finder', {})
    sf_top5 = sf.get('top5', [])

    domain_colors = {'Relationship Building':'#3b82f6','Strategic Thinking':'#22c55e',
                     'Executing':'#8b5cf6','Influencing':'#ff6b35'}
    tag_cls = {'Relationship Building':'tag-rb','Strategic Thinking':'tag-st',
               'Executing':'tag-ex','Influencing':'tag-inf'}
    interp = p.get('interpretations', {})
    sf_descs = interp.get('strengths', {})
    sf_ja = interp.get('strengths_ja', {})
    pers_descs = interp.get('personality', {})

    sf_html = ''
    if sf_top5:
        items = ''
        for s in sf_top5:
            tc = tag_cls.get(s.get('domain',''), 'tag-rb')
            ja_name = sf_ja.get(s['name'], '')
            ja_span = f' <span style="font-size:12px;color:var(--text-secondary);font-weight:400">{ja_name}</span>' if ja_name else ''
            desc = sf_descs.get(s['name'], '')
            desc_html = f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.6;margin-top:6px">{desc}</div>' if desc else ''
            items += f'''<li class="top5-item"><span class="rank">{s["rank"]}</span>
          <div><div class="sf-name">{s["name"]}{ja_span}</div>
          <div class="sf-domain"><span class="tag {tc}">{s["domain"]}</span></div>{desc_html}</div></li>'''
        dom_bars = ''
        sf_domains = sf.get('domain_distribution', {})
        for dname, ranks in sf_domains.items():
            dc = domain_colors.get(dname, '#6366f1')
            top10 = sum(1 for r in ranks if r <= 10)
            dom_bars += f'''<div class="domain-bar">
          <div class="domain-header"><span>{dname}</span><span style="font-family:var(--font-mono)">{top10} / 10</span></div>
          <div class="domain-track"><div class="domain-fill" style="width:{top10*10}%;background:{dc}"></div></div></div>'''

        etype = ennea.get('type', '?')
        ename = ENNEA_NAMES.get(etype, '')
        hsp_label = HSP_LABELS.get(hsp.get('score', ''), hsp.get('score', ''))
        adhd_label = ADHD_LABELS.get(adhd.get('tendency', ''), adhd.get('tendency', ''))

        sf_html = f'''<div class="grid"><div class="card">
      <div class="card-title"><span class="icon">&#9733;</span> CliftonStrengths TOP 5</div>
      <ul class="top5-list">{items}</ul>
      <div style="font-size:11px;color:var(--text-muted);margin-top:12px">Lead Domain: {sf.get("lead_domain","")} | 受験日: {sf.get("date_taken","")}</div>
    </div>
    <div class="card">
      <div class="card-title"><span class="icon">&#9632;</span> ドメイン分布（TOP10内）</div>
      <div style="margin-top:8px">{dom_bars}</div>
      <div style="margin-top:24px">
        <div class="card-title" style="font-size:13px"><span class="icon">&#9830;</span> Typology</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px">
          <div class="typo-cell"><div class="typo-label">Enneagram</div>
            <div class="typo-value">Type {etype}</div><div class="typo-sub">{ename}</div>
            {"<div class='typo-desc'>"+pers_descs['enneagram']+"</div>" if pers_descs.get('enneagram') else ""}</div>
          <div class="typo-cell"><div class="typo-label">Blood Type</div>
            <div class="typo-value">{bt["type"]}</div><div class="typo-sub">日本人口の{bt["population_pct"]}%</div>
            {"<div class='typo-desc'>"+pers_descs['blood_type']+"</div>" if pers_descs.get('blood_type') else ""}</div>
          <div class="typo-cell"><div class="typo-label">感覚感受性</div>
            <div class="typo-value" style="color:#facc15">{hsp_label}</div><div class="typo-sub">環境・感情への感度</div>
            {"<div class='typo-desc'>"+pers_descs['sensitivity']+"</div>" if pers_descs.get('sensitivity') else ""}</div>
          <div class="typo-cell"><div class="typo-label">集中パターン</div>
            <div class="typo-value" style="color:#ff8f6b">{adhd_label}</div><div class="typo-sub">過集中×拡散の波</div>
            {"<div class='typo-desc'>"+pers_descs['focus_pattern']+"</div>" if pers_descs.get('focus_pattern') else ""}</div>
        </div></div>
    </div></div>'''

    return f'''<section class="section" id="personality">
  <h2 class="section-title">Personality Profile</h2>
  {sf_html}
</section>'''


def _western_detail(p):
    wa = p['western_astrology']
    west = wa['sun_sign']
    ruling = wa.get('ruling_planet', '')
    decan = wa.get('decan', {})
    el_traits = wa.get('element_traits', '')
    q_traits = wa.get('quality_traits', '')
    traits = wa.get('traits', '')
    forecast = wa.get('forecast_2026', '')

    cards = f'''<div class="grid grid-3">
    <div class="card"><div class="card-label">太陽星座</div>
      <div class="card-value">{west["symbol"]} {west["sign"]}</div>
      <div class="card-sub">{west["element"]} / {west["quality"]}</div>
      {"<div class='typo-desc' style='margin-top:8px'>"+traits+"</div>" if traits else ""}</div>
    <div class="card"><div class="card-label">支配星</div>
      <div class="card-value">{ruling}</div>
      {"<div class='typo-desc' style='margin-top:8px'>"+el_traits+"</div>" if el_traits else ""}</div>'''
    if decan:
        cards += f'''<div class="card"><div class="card-label">デカン（第{decan.get("number","")}区）</div>
      <div class="card-value">{decan.get("sub_ruler","")}</div>
      {"<div class='typo-desc' style='margin-top:8px'>"+decan.get("traits","")+"</div>" if decan.get("traits") else ""}</div>'''
    cards += '</div>'

    desc_parts = ''
    if q_traits:
        desc_parts += f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-top:12px">{q_traits}</div>'
    if forecast:
        desc_parts += f'''<div class="insight-box" style="margin-top:12px;border-color:rgba(139,92,246,0.3);background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(99,102,241,0.04))">
      <div class="insight-title" style="color:#c4b5fd">2026年 {west["sign"]}の運勢</div>
      <p style="line-height:1.9;font-size:14px">{forecast}</p></div>'''

    return cards + desc_parts


def _divination(p):
    fp = p['four_pillars']
    pillars = [fp['year_pillar'], fp['month_pillar'], fp['day_pillar']]
    dm = fp['day_master']
    elements = fp['five_elements_balance']
    missing = fp.get('missing_elements', [])
    nsk = p['nine_star_ki']
    ys, ms = nsk['year_star'], nsk['month_star']
    rok = p['rokusei']
    west = p['western_astrology']['sun_sign']

    interp = p.get('interpretations', {})
    fp_interp = interp.get('four_pillars', {})
    nsk_interp = interp.get('nine_star_ki', {})
    rok_interp = interp.get('rokusei', {})

    pillar_labels = ['年柱', '月柱', '日柱']
    pillar_roles = ['社会的顔・祖先運', '仕事・キャリア', '本質的な自己']
    pillar_keys = ['year', 'month', 'day']
    elem_cls = {'Wood':'elem-wood','Fire':'elem-fire','Earth':'elem-earth','Metal':'elem-metal','Water':'elem-water'}
    pcards = ''
    for i, pl in enumerate(pillars):
        ec = elem_cls.get(pl['stem']['element'], '')
        pcards += f'''<div class="pillar"><div class="pillar-label">{pillar_labels[i]}</div>
      <div class="kanji">{pl["full"]}</div>
      <div class="reading">{pl["stem"]["reading"]}・{pl["branch"]["reading"]}</div>
      <div class="element-badge {ec}">{pl["stem"]["element"]}</div>
      <div style="font-size:10px;color:var(--text-muted);margin-top:6px">{pillar_roles[i]}</div></div>'''
    pcards += '<div class="pillar unknown"><div class="pillar-label">時柱</div><div class="kanji">？？</div><div class="reading">出生時刻不明</div><div class="element-badge" style="background:rgba(255,255,255,0.05);color:var(--text-muted)">Locked</div><div style="font-size:10px;color:var(--text-muted);margin-top:6px">晩年・子孫運</div></div>'

    el_bars = ''
    el_colors = {'木':'#4ade80','火':'#f87171','土':'#facc15','金':'#94a3b8','水':'#60a5fa'}
    for el_name in ['木','火','土','金','水']:
        info = elements.get(el_name, {})
        pct = info.get('pct', 0)
        el_bars += f'''<div class="element-col">
      <div class="element-pct" style="color:{el_colors[el_name]}">{pct}%</div>
      <div class="element-fill" style="height:{max(pct,2)}%;background:{el_colors[el_name]}"></div>
      <div class="element-name">{el_name}</div></div>'''

    missing_html = ''
    if missing:
        insight = fp.get('element_insight', '')
        missing_html = f'<div style="font-size:12px;color:var(--yellow);margin-top:8px">欠如: {"・".join(str(m) for m in missing)}{" — "+insight if insight else ""}</div>'

    cur9 = next((c for c in nsk.get('nine_year_cycle', []) if c.get('current')), None)
    nsk_cards = f'''<div class="grid grid-3">
    <div class="card"><div class="card-label">本命星（年星）</div>
      <div class="card-value">{ys["name"]}</div><div class="card-sub">{ys["element"]} / {ys["direction"]}</div></div>
    <div class="card"><div class="card-label">月命星</div>
      <div class="card-value">{ms["name"]}</div><div class="card-sub">{ms["element"]} / {ms["direction"]}</div></div>'''
    if cur9:
        nsk_cards += f'''<div class="card"><div class="card-label">2026年 宮位置</div>
      <div class="card-value">{cur9["palace"]}</div><div class="card-sub">{cur9["theme"]}（Energy {cur9["energy"]}）</div></div>'''
    nsk_cards += '</div>'

    cur12 = next((c for c in rok.get('twelve_year_cycle', []) if c.get('current')), None)
    rok_cards = f'''<div class="grid grid-3">
    <div class="card"><div class="card-label">運命星</div>
      <div class="card-value">{rok["main_star"]["name"]}({rok["main_star"]["polarity"]})</div>
      <div class="card-sub">{rok["main_star"]["reading"]}</div></div>'''
    if rok.get('reigou') and rok.get('sub_star'):
        rok_cards += f'''<div class="card"><div class="card-label">霊合サブ星</div>
      <div class="card-value">{rok["sub_star"]["name"]}({rok["sub_star"]["polarity"]})</div>
      <div class="card-sub">{rok["sub_star"]["reading"]}</div></div>'''
    if cur12:
        phase_label = satsukai_html(cur12.get('殺界')) if cur12.get('殺界') else '好調期'
        rok_cards += f'''<div class="card"><div class="card-label">2026年</div>
      <div class="card-value">{cur12["phase"]}</div>
      <div class="card-sub">{phase_label}（Energy {cur12["energy"]}）</div></div>'''
    rok_cards += '</div>'

    cycle12 = rok.get('twelve_year_cycle', [])
    sub_by_year = {c['year']: c for c in rok.get('sub_star_cycle', [])}
    has_sub = rok.get('reigou', False)
    rows = ''
    for c in cycle12:
        cls = ' class="current"' if c.get('current') else ''
        sub_td = f'<td>{sub_by_year[c["year"]]["phase"] if c["year"] in sub_by_year else "—"}</td>' if has_sub else ''
        rows += f'<tr{cls}><td>{c["year"]}</td><td>{c["phase"]}</td>{sub_td}'
        rows += f'<td>{satsukai_html(c.get("殺界"))}</td>'
        rows += f'<td><span style="color:{energy_color(c["energy"])}">{c["energy"]}</span></td></tr>'

    sub_th = '<th>サブ</th>' if has_sub else ''
    table = f'<table class="cycle-table"><thead><tr><th>年</th><th>メイン</th>{sub_th}<th>殺界</th><th>Energy</th></tr></thead><tbody>{rows}</tbody></table>'

    # Four Pillars interpretation text
    fp_overview = fp_interp.get('overview', '')
    fp_overview_html = f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:16px">{fp_overview}</div>' if fp_overview else ''
    dm_detail = fp_interp.get('day_master_detail', dm['description'])
    pillar_descs = ''
    for key, label in [('year', '年柱'), ('month', '月柱'), ('day', '日柱')]:
        desc = fp_interp.get(key, '')
        if desc:
            full = fp[f'{key}_pillar']['full']
            pillar_descs += f'<strong style="color:var(--text)">{label}（{full}）</strong>: {desc}<br>'
    pillar_descs_html = f'<div style="margin-top:8px;font-size:12px;color:var(--text-secondary);line-height:1.7">{pillar_descs}</div>' if pillar_descs else ''

    # Nine Star Ki interpretation
    nsk_year_desc = nsk_interp.get('year', '')
    nsk_month_desc = nsk_interp.get('month', '')
    nsk_desc_html = ''
    if nsk_year_desc or nsk_month_desc:
        parts = ''
        if nsk_year_desc:
            parts += f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.7">{nsk_year_desc}</div>'
        if nsk_month_desc:
            parts += f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-top:8px">{nsk_month_desc}</div>'
        nsk_desc_html = f'<div class="card" style="margin-top:12px">{parts}</div>'

    # Rokusei interpretation
    rok_main_desc = rok_interp.get('main', '')
    rok_sub_desc = rok_interp.get('sub', '')
    rok_reigou_desc = rok_interp.get('reigou', '')
    rok_desc_html = ''
    if rok_main_desc or rok_sub_desc:
        parts = ''
        if rok_main_desc:
            parts += f'<strong style="color:var(--text)">{rok["main_star"]["name"]}({rok["main_star"]["polarity"]})</strong>: {rok_main_desc}<br>'
        if rok_sub_desc:
            parts += f'<strong style="color:var(--text)">{rok["sub_star"]["name"]}({rok["sub_star"]["polarity"]})</strong>: {rok_sub_desc}'
        rok_desc_html = f'<div style="font-size:12px;color:var(--text-secondary);line-height:1.7;margin-bottom:12px">{parts}</div>'
    reigou_box = ''
    if rok.get('reigou') and rok_reigou_desc:
        reigou_box = f'''<div style="background:rgba(234,179,8,0.08);border:1px solid rgba(234,179,8,0.2);border-radius:var(--radius-sm);padding:12px;text-align:center;margin-top:12px">
      <div style="font-size:13px;color:var(--yellow);font-weight:600">霊合星人</div>
      <div style="font-size:12px;color:var(--text-secondary);margin-top:6px;line-height:1.7;text-align:left">{rok_reigou_desc}</div></div>'''

    return f'''<section class="section" id="divination">
  <h2 class="section-title">占術プロファイル</h2>
  <p class="section-desc">四柱推命・九星気学・六星占術・西洋占星術 — 不変の本質的特性</p>

  <h3 class="sub-title">四柱推命</h3>
  {fp_overview_html}
  <div class="pillar-grid">{pcards}</div>
  <div style="margin-top:16px;font-size:13px;color:var(--text-secondary);line-height:1.7">
    <strong style="color:var(--text)">日主: {dm["char"]}火（{dm["yin_yang"]}火）</strong> — {dm_detail}</div>
  {pillar_descs_html}
  <div class="element-bar" style="margin-top:12px">{el_bars}</div>
  {missing_html}

  <h3 class="sub-title">九星気学</h3>
  {nsk_cards}
  {nsk_desc_html}

  <h3 class="sub-title">六星占術</h3>
  {rok_cards}
  {rok_desc_html}
  {reigou_box}
  <div style="margin-top:12px">{table}</div>

  <h3 class="sub-title">西洋占星術</h3>
  {_western_detail(p)}
  <div class="unlock-banner">出生時刻を追加すると、時柱・アセンダント・月星座が解放されます</div>
</section>'''


def _forecast(p):
    nsk = p['nine_star_ki']
    rok = p['rokusei']
    cur9 = next((c for c in nsk.get('nine_year_cycle', []) if c.get('current')), None)
    cur12 = next((c for c in rok.get('twelve_year_cycle', []) if c.get('current')), None)
    cur_sub = next((c for c in rok.get('sub_star_cycle', []) if c.get('current')), None)
    cur_comb = next((c for c in rok.get('reigou_combined', []) if c.get('year') == 2026), None)
    has_reigou = rok.get('reigou', False)

    cards = '<div class="grid grid-4">'
    if cur9:
        cards += f'''<div class="card tc"><div class="card-label">九星気学</div>
      <div class="card-value">{cur9["palace"]}</div><div class="card-sub">{cur9["theme"]}</div></div>'''
    if cur12:
        cards += f'''<div class="card tc"><div class="card-label">六星占術（メイン）</div>
      <div class="card-value">{cur12["phase"]}</div><div class="card-sub">Energy {cur12["energy"]}</div></div>'''
    if cur_sub:
        sub_label = satsukai_html(cur_sub.get('殺界')) if cur_sub.get('殺界') else f'Energy {cur_sub["energy"]}'
        cards += f'''<div class="card tc"><div class="card-label">六星占術（サブ）</div>
      <div class="card-value">{cur_sub["phase"]}</div><div class="card-sub">{sub_label}</div></div>'''
    if cur_comb:
        cards += f'''<div class="card tc"><div class="card-label">霊合統合スコア</div>
      <div class="card-value" style="color:{energy_color(cur_comb["score"])}">{cur_comb["score"]}</div>
      <div class="card-sub">{cur_comb["label"]}</div></div>'''
    cards += '</div>'

    # Chart legend: explain each line
    legend_items = [
        ('#6366f1', '九星気学', '9年周期。本命星の宮遷移による運気の波。社会的な運勢の流れを示す'),
        ('#22c55e', '六星占術', '12年周期。大殺界を含む運命星の巡り。個人的な運気のバイオリズム'),
    ]
    if has_reigou:
        legend_items.append(('#eab308', '霊合合成', 'メイン星70% + サブ星30%の加重平均。霊合星人の実効的な運気スコア'))

    legend_html = '<div class="chart-legend">'
    for color, label, desc in legend_items:
        legend_html += f'''<div class="chart-legend-item">
      <span class="chart-legend-line" style="background:{color}"></span>
      <div><span class="chart-legend-label">{label}</span>
      <span class="chart-legend-desc">{desc}</span></div></div>'''
    legend_html += '</div>'

    # Integrated forecast insight
    insight = _forecast_insight(cur9, cur12, cur_sub, cur_comb, has_reigou, nsk, rok)

    return f'''<section class="section" id="forecast-2026">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(234,179,8,0.15);color:#facc15">&#9733;</div>
    <div><h2>2026年 運勢フォーキャスト</h2>
      <div class="pillar-sub">九星気学 × 六星占術が示す年間の流れ</div></div>
  </div>
  {cards}
  <div class="chart-wrap"><canvas id="chartOverlay" height="280"></canvas></div>
  {legend_html}
  {insight}
</section>'''


def _forecast_insight(cur9, cur12, cur_sub, cur_comb, has_reigou, nsk, rok):
    """Generate integrated forecast narrative from multiple systems."""
    parts = []

    # Nine Star Ki reading
    if cur9:
        parts.append(f'九星気学では<strong>{cur9["palace"]}</strong>（{cur9["theme"]}）に位置し、エネルギーは<strong>{cur9["energy"]}</strong>。')

    # Rokusei reading
    if cur12:
        satsukai = cur12.get('殺界')
        if satsukai:
            parts.append(f'六星占術のメイン星は<strong>{cur12["phase"]}</strong>（{satsukai}）で要注意期。')
        else:
            parts.append(f'六星占術のメイン星は<strong>{cur12["phase"]}</strong>（Energy {cur12["energy"]}）で好調期。')

    if has_reigou and cur_sub:
        sub_satsukai = cur_sub.get('殺界')
        if sub_satsukai:
            parts.append(f'一方、霊合サブ星は<strong>{cur_sub["phase"]}</strong>（{sub_satsukai}）で逆風。')
        else:
            parts.append(f'霊合サブ星も<strong>{cur_sub["phase"]}</strong>（Energy {cur_sub["energy"]}）で順調。')

    # Synthesis
    if cur_comb and has_reigou:
        score = cur_comb['score']
        label = cur_comb['label']
        if score >= 70:
            synthesis = f'統合スコア<strong>{score}</strong>（{label}）— 複数の体系が好調を示しており、<strong>攻めの年</strong>。新しい挑戦や投資に適したタイミング。'
        elif score >= 50:
            synthesis = f'統合スコア<strong>{score}</strong>（{label}）— 体系間で評価が分かれており、<strong>慎重な前進</strong>が最適解。大きな決断は十分な分析の上で。'
        elif score >= 30:
            synthesis = f'統合スコア<strong>{score}</strong>（{label}）— 複数の体系で注意信号が出ており、<strong>守りを固める年</strong>。基盤の強化と内面の充実に集中。'
        else:
            synthesis = f'統合スコア<strong>{score}</strong>（{label}）— 全体系で低エネルギー期。<strong>無理をせず回復に専念</strong>する時期。大きな変更は避けるのが吉。'
        parts.append(synthesis)
    elif cur9 and cur12:
        avg = (cur9['energy'] + cur12['energy']) // 2
        if avg >= 60:
            parts.append(f'両体系の平均エネルギーは<strong>{avg}</strong>。全体的に好調で、<strong>積極的に動ける年</strong>。')
        else:
            parts.append(f'両体系の平均エネルギーは<strong>{avg}</strong>。<strong>地固めと準備</strong>に適した年。')

    # Peak year
    cycle9 = nsk.get('nine_year_cycle', [])
    combined = rok.get('reigou_combined', [])
    if combined:
        peak = max(combined, key=lambda c: c['score'])
        parts.append(f'次のピークは<strong>{peak["year"]}年</strong>（統合スコア{peak["score"]}）。そこへ向けた布石を今から打つ。')
    elif cycle9:
        peak = max(cycle9, key=lambda c: c['energy'])
        parts.append(f'九星気学のピークは<strong>{peak["year"]}年</strong>（{peak["palace"]}、Energy {peak["energy"]}）。')

    body = ''.join(parts)
    return f'''<div class="insight-box" style="margin-top:16px;border-color:rgba(234,179,8,0.3);background:linear-gradient(135deg,rgba(234,179,8,0.08),rgba(250,204,21,0.04))">
    <div class="insight-title" style="color:var(--yellow)">統合フォーキャスト</div>
    <p style="line-height:1.9;font-size:14px">{body}</p>
  </div>'''


DOMAIN_MSGS = {
    'work': {
        5: '全力投球で成果が出る時期。新プロジェクトの立ち上げに最適',
        4: '順調に進む。チャンスを逃さず着実に成果を積む',
        3: '普通ペース。地道な積み重ねが後に効いてくる',
        2: '停滞感あり。焦らず基礎固めに集中',
        1: '無理は禁物。現状維持を心がけ、回復を優先',
    },
    'money': {
        5: '金運好調。投資・交渉に良い時期。大きな判断も可',
        4: '堅実な収入が見込める。無駄遣いを避ければ蓄積できる',
        3: '収支トントン。計画的な支出管理が重要',
        2: '予想外の出費に注意。大きな買い物は延期が吉',
        1: '金運低迷。守りの姿勢で乗り切る。衝動買い厳禁',
    },
    'health': {
        5: '体調絶好調。新しい運動習慣を始めるチャンス',
        4: '概ね良好。規則正しい生活を維持して好調を保つ',
        3: '可もなく不可もなく。睡眠の質に注意を払う',
        2: '疲れが出やすい。休息を意識的に増やす',
        1: '体調管理に細心の注意。無理なスケジュールは避ける',
    },
    'romance': {
        5: '人間関係が最も輝く時期。新しい出会いも深い絆も',
        4: '良好な関係が築ける。コミュニケーションが円滑',
        3: '平穏な時期。既存の関係を大切にする',
        2: 'すれ違いが起きやすい。丁寧な対話を心がける',
        1: '距離感が大事。一人の時間で自分を充電する',
    },
}


def _domain_msg(domain, stars, phase):
    return DOMAIN_MSGS.get(domain, {}).get(stars, '')


def _monthly(p):
    mf = p.get('monthly_fortune', [])
    if not mf:
        return ''
    current_month = _date.today().month - 1  # 0-based

    # Year timeline bar
    timeline_colors = {
        'great': 'rgba(34,197,94,0.5)', 'good': 'rgba(59,130,246,0.4)',
        'caution': 'rgba(234,179,8,0.4)', 'danger': 'rgba(239,68,68,0.45)',
    }
    timeline = ''
    for m in mf:
        bg = timeline_colors.get(m['rokusei']['type'], 'rgba(99,102,241,0.3)')
        timeline += f'<div class="yt-month" data-month="{m["month"]-1}" style="background:{bg}">{m["month"]}</div>'

    # Month panels with domain messages
    panels_data = json.dumps([{
        'month': f'{m["month"]}月',
        'nineStarNote': m['nine_star']['note'],
        'nineStarEnergy': m['nine_star']['energy'],
        'rokuseiPhase': m['rokusei']['phase'],
        'rokuseiType': m['rokusei']['type'],
        'work': m['domains']['work'],
        'money': m['domains']['money'],
        'health': m['domains']['health'],
        'romance': m['domains']['romance'],
        'workMsg': _domain_msg('work', m['domains']['work'], m['rokusei']['phase']),
        'moneyMsg': _domain_msg('money', m['domains']['money'], m['rokusei']['phase']),
        'healthMsg': _domain_msg('health', m['domains']['health'], m['rokusei']['phase']),
        'romanceMsg': _domain_msg('romance', m['domains']['romance'], m['rokusei']['phase']),
    } for m in mf])

    return f'''<section class="section" id="monthly">
  <h2 class="section-title">2026年 月間運勢</h2>
  <p class="section-desc">九星気学の月宮位置 × 六星占術の月フェーズを統合し、4ドメインで分析</p>
  <div class="year-timeline" id="yearTimeline">{timeline}</div>
  <div class="month-selector" id="monthSelector"></div>
  <div id="monthPanels"></div>
</section>
<script>
const monthlyData={panels_data};
const currentMonth={current_month};
function starRating(n){{return'<span style="color:var(--yellow);">'+'★'.repeat(n)+'</span><span style="color:var(--border);">'+'★'.repeat(5-n)+'</span>';}}
function phaseColor(t){{
  if(t==='great')return{{bg:'rgba(34,197,94,0.12)',border:'rgba(34,197,94,0.3)',color:'#4ade80'}};
  if(t==='good')return{{bg:'rgba(59,130,246,0.12)',border:'rgba(59,130,246,0.3)',color:'#60a5fa'}};
  if(t==='caution')return{{bg:'rgba(234,179,8,0.12)',border:'rgba(234,179,8,0.3)',color:'#facc15'}};
  return{{bg:'rgba(239,68,68,0.12)',border:'rgba(239,68,68,0.3)',color:'#f87171'}};
}}
const selEl=document.getElementById('monthSelector');
const panEl=document.getElementById('monthPanels');
monthlyData.forEach((m,i)=>{{
  const btn=document.createElement('button');
  btn.className='month-btn'+(i===currentMonth?' active current':'');
  btn.textContent=m.month;btn.dataset.month=i;btn.onclick=()=>selectMonth(i);
  selEl.appendChild(btn);
  const pc=phaseColor(m.rokuseiType);
  const panel=document.createElement('div');
  panel.className='month-panel'+(i===currentMonth?' active':'');
  panel.id='month-'+i;
  panel.innerHTML=`<div class="card">
    <div class="month-card-header">
      <div class="month-label">${{m.month}}</div>
      <div class="month-tags">
        <span class="month-tag" style="background:rgba(99,102,241,0.15);color:#a5b4fc">九星: ${{m.nineStarNote}}</span>
        <span class="month-tag" style="background:${{pc.bg}};color:${{pc.color}};border:1px solid ${{pc.border}}">六星: ${{m.rokuseiPhase}}</span>
      </div>
    </div>
    <div class="domain-grid">
      <div class="domain-card work"><div class="domain-icon-label"><div class="domain-label" style="color:var(--blue)">仕事</div><div class="domain-stars">${{starRating(m.work)}}</div></div><div class="domain-msg">${{m.workMsg}}</div></div>
      <div class="domain-card money"><div class="domain-icon-label"><div class="domain-label" style="color:var(--gold)">お金</div><div class="domain-stars">${{starRating(m.money)}}</div></div><div class="domain-msg">${{m.moneyMsg}}</div></div>
      <div class="domain-card health"><div class="domain-icon-label"><div class="domain-label" style="color:var(--green)">健康</div><div class="domain-stars">${{starRating(m.health)}}</div></div><div class="domain-msg">${{m.healthMsg}}</div></div>
      <div class="domain-card romance"><div class="domain-icon-label"><div class="domain-label" style="color:#f472b6">恋愛</div><div class="domain-stars">${{starRating(m.romance)}}</div></div><div class="domain-msg">${{m.romanceMsg}}</div></div>
    </div>
  </div>`;
  panEl.appendChild(panel);
}});
function selectMonth(idx){{
  document.querySelectorAll('.month-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.month-panel').forEach(p=>p.classList.remove('active'));
  document.querySelector(`.month-btn[data-month="${{idx}}"]`).classList.add('active');
  document.getElementById('month-'+idx).classList.add('active');
  document.querySelectorAll('.yt-month').forEach(m=>m.style.opacity='0.5');
  document.querySelector(`.yt-month[data-month="${{idx}}"]`).style.opacity='1';
}}
document.querySelectorAll('.yt-month').forEach(el=>{{
  el.addEventListener('click',()=>selectMonth(parseInt(el.dataset.month)));
}});
selectMonth(currentMonth);
</script>'''


def _cross_analysis(p):
    """Cross Analysis — 強み×運気の掛け合わせ insight boxes."""
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    pers = p.get('personality', {})
    ennea = pers.get('enneagram', {})
    hsp = pers.get('hsp', {})
    adhd = pers.get('adhd', {})
    dm = p['four_pillars']['day_master']
    ys = p['nine_star_ki']['year_star']
    west = p['western_astrology']['sun_sign']
    bt = p['blood_type']
    rok = p['rokusei']

    # Build insight boxes from profile data
    boxes = []

    # 1. Empathy × Sensitivity × Enneagram
    if sf_top5 and ennea and hsp:
        etype = ennea.get('type', '')
        hsp_score = hsp.get('score', '')
        sens_label = HSP_LABELS.get(hsp_score, hsp_score)
        boxes.append({
            'title': f'Empathy × 繊細さ × エニアグラム{etype}',
            'text': f'CliftonStrengths 1位の共感性と{sens_label}な感受性、'
                    f'エニアグラムType {etype}の独自性追求が共鳴。'
                    f'「人の感情を深く理解し、独自の視点で表現する力」を形成する。'
                    f'この組み合わせはサービス設計においてユーザーの痛みを自分事として感じられるPMFの源泉。',
        })

    # 2. Intellection × Focus Pattern × Day Master
    if len(sf_top5) >= 2 and adhd:
        focus_label = ADHD_LABELS.get(adhd.get('tendency', ''), '')
        boxes.append({
            'title': f'Intellection × 集中パターン × {dm["char"]}火（陰火）',
            'text': f'深い思考力（Intellection 2位）× {focus_label}の集中特性 × '
                    f'{dm["char"]}火（ロウソクの炎）。'
                    f'環境を整えれば安定して燃え続けるが、刺激に弱い。'
                    f'自動化で雑務を排除し、思考に没頭できる環境を作ることが最重要。',
        })

    # 3. Deliberative × Blood Type × Western
    if len(sf_top5) >= 3:
        boxes.append({
            'title': f'Deliberative × {bt["type"]}型 × {west["sign"]} {west["quality"]}',
            'text': f'慎重さ（3位）× {bt["type"]}型の合理的分析 × '
                    f'{west["sign"]}の{west["quality"]}（不動宮）。'
                    f'三重の慎重さは深い分析に基づく確実な意思決定を可能にする。'
                    f'一方で「分析麻痺」に陥りやすく、行動が遅れるリスクもある。',
        })

    # 4. Connectedness × Nine Star × Current Year
    cur9 = next((c for c in p['nine_star_ki'].get('nine_year_cycle', []) if c.get('current')), None)
    if len(sf_top5) >= 4 and cur9:
        boxes.append({
            'title': f'Connectedness × {ys["name"]} × {cur9["palace"]}2026',
            'text': f'全てを繋げて見る直感力（4位）× {ys["name"]}の社交力と言葉の力。'
                    f'2026年の{cur9["palace"]}は「{cur9["theme"]}」の年 — '
                    f'点在するプロジェクト群を繋ぎ、エコシステムを設計するのに最適なタイミング。',
        })

    # 5. Maximizer × Systems
    if len(sf_top5) >= 5:
        boxes.append({
            'title': 'Maximizer × 3S原則 × 7つの習慣',
            'text': '「良い→最高」の追求（5位）がOSそのもの。'
                    '3S（Simple, Scalable, Sustainable）でフィルターし、'
                    '第II領域（重要×非緊急）に集中投資する。'
                    '「もっと良くできないか？」が止まらない性質は自動化・最適化の原動力。',
        })

    if not boxes:
        return ''

    # Build HTML
    grid_items = ''
    for b in boxes:
        grid_items += f'''<div class="insight-box">
      <div class="insight-title">{b["title"]}</div>
      <p>{b["text"]}</p>
    </div>'''

    return f'''<section class="section" id="cross">
  <h2 class="section-title">Cross Analysis — 強み×運気の掛け合わせ</h2>
  <div class="grid">{grid_items}</div>
</section>'''


def _footer(tier):
    gen_date = _date.today().isoformat()
    systems = '四柱推命 × 九星気学 × 六星占術 × 西洋占星術'
    if tier >= 2:
        systems += ' × CliftonStrengths × Enneagram'
    return f'''<footer class="page-footer">
  <div>Self-Insight v0.5 — Phase 0→1</div>
  <div style="margin-top:4px">Generated {gen_date} | {systems}</div>
</footer>'''


def _charts_js(p):
    nsk = p['nine_star_ki']
    rok = p['rokusei']
    cycle9 = nsk.get('nine_year_cycle', [])
    combined = rok.get('reigou_combined', [])
    cycle12 = rok.get('twelve_year_cycle', [])

    # Overlay data — single chart with all lines
    nine_by_year = {c['year']: c['energy'] for c in cycle9}
    twelve_by_year = {c['year']: c['energy'] for c in cycle12}
    comb_by_year = {c['year']: c['score'] for c in combined}
    years = sorted(set(list(nine_by_year) + list(twelve_by_year) + list(comb_by_year)))
    overlay_labels = json.dumps([str(y) for y in years])
    nine_data = json.dumps([nine_by_year.get(y) for y in years])
    twelve_data = json.dumps([twelve_by_year.get(y) for y in years])
    comb_data = json.dumps([comb_by_year.get(y) for y in years])

    return f'''<script>
new Chart(document.getElementById('chartOverlay'),{{
  type:'line',
  data:{{labels:{overlay_labels},datasets:[
    {{label:'九星気学',data:{nine_data},borderColor:'#6366f1',fill:false,tension:0.4,borderWidth:2,pointRadius:4,pointBackgroundColor:'#6366f1'}},
    {{label:'六星占術',data:{twelve_data},borderColor:'#22c55e',fill:false,tension:0.4,borderWidth:2,pointRadius:4,pointBackgroundColor:'#22c55e'}},
    {{label:'霊合合成',data:{comb_data},borderColor:'#eab308',fill:false,tension:0.4,borderWidth:2,borderDash:[6,3],pointRadius:4,pointBackgroundColor:'#eab308'}}
  ]}},
  options:{{responsive:true,maintainAspectRatio:false,animation:{{duration:1500,easing:'easeOutQuart'}},interaction:{{mode:'index',intersect:false}},
    plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{color:'#7c8293',font:{{family:"'JetBrains Mono',monospace",size:11}}}},grid:{{color:'rgba(255,255,255,0.05)'}}}},
      y:{{min:0,max:110,ticks:{{display:false}},grid:{{color:'rgba(255,255,255,0.05)'}}}}}}
  }}
}});
const sections=document.querySelectorAll('.section[id]');
const navLinks=document.querySelectorAll('.nav-bar a');
const observer=new IntersectionObserver((entries)=>{{
  entries.forEach(e=>{{if(e.isIntersecting){{navLinks.forEach(l=>l.classList.remove('active'));
    const link=document.querySelector(`.nav-bar a[href="#${{e.target.id}}"]`);if(link)link.classList.add('active');}}}});
}},{{threshold:0.2,rootMargin:'-80px 0px -60% 0px'}});
sections.forEach(s=>observer.observe(s));
</script>'''


# === CSS ===
CSS = '''<style>
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2d3348;--border-light:#3d4460;
  --accent:#6366f1;--accent2:#8b5cf6;--blue:#3b82f6;--green:#22c55e;--red:#ef4444;--yellow:#eab308;--gold:#c9a84c;
  --text:#e4e4e7;--text-secondary:#9ca3af;--text-muted:#7c8293;
  --font-body:'Inter','Noto Sans JP',sans-serif;--font-mono:'JetBrains Mono',monospace;
  --r-sm:6px;--r-md:10px;--r-lg:14px;--r-xl:16px;--gnav-height:52px}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth;scroll-padding-top:calc(52px + 60px)}
body{font-family:var(--font-body);background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh;-webkit-font-smoothing:antialiased;position:relative}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;opacity:0.03;pointer-events:none;z-index:9999;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.container{max-width:1100px;margin:0 auto;padding:24px}
.site-header{display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:52px;background:rgba(22,24,31,0.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,0.08);position:sticky;top:0;z-index:100}
.site-nav{display:flex;gap:4px}
.site-nav a{color:#71717a;text-decoration:none;font-size:13px;font-weight:500;padding:6px 14px;border-radius:6px;transition:background .15s,color .15s;font-family:var(--font-body)}
.site-nav a:hover,.site-nav a[aria-current=page]{background:rgba(255,255,255,0.065);color:#f5f5f7}
.nav-toggle{display:none}
.nav-toggle-label{display:none;cursor:pointer;width:44px;height:44px;align-items:center;justify-content:center}
.nav-toggle-label span,.nav-toggle-label span::before,.nav-toggle-label span::after{display:block;background:#9ca3af;height:2px;width:20px;border-radius:2px;position:relative;transition:all .3s}
.nav-toggle-label span::before,.nav-toggle-label span::after{content:'';position:absolute}
.nav-toggle-label span::before{top:-6px}
.nav-toggle-label span::after{top:6px}
.nav-bar{position:sticky;top:52px;z-index:90;background:rgba(15,17,23,0.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 24px;display:flex;justify-content:center;gap:4px;overflow-x:auto;scrollbar-width:none}
.nav-bar::-webkit-scrollbar{display:none}
.nav-bar a{color:var(--text-muted);text-decoration:none;font-size:12px;font-weight:500;padding:14px 16px;white-space:nowrap;transition:color .2s,background .2s;border-radius:var(--r-sm)}
.nav-bar a:hover,.nav-bar a.active{color:var(--accent);background:rgba(99,102,241,0.12)}
.hero{background:linear-gradient(135deg,#1e1b4b,#312e81,#1e1b4b);background-size:200% 200%;animation:heroShift 12s ease-in-out infinite;border-radius:var(--r-xl);padding:40px 32px;margin-bottom:32px;border:1px solid var(--border);overflow:hidden}
@keyframes heroShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.hero h1{font-size:clamp(20px,2.5vw,26px);font-weight:700;margin-bottom:4px}
.hero .subtitle{color:var(--text-muted);font-size:14px;margin-bottom:20px}
.hero-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.chip{font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;background:rgba(255,255,255,0.08);color:var(--text-secondary);border:1px solid rgba(255,255,255,0.1)}
.chip.hl{background:rgba(99,102,241,0.15);color:#a5b4fc;border-color:rgba(99,102,241,0.3)}
.stats{display:flex;gap:24px;flex-wrap:wrap}
.stat-card{background:rgba(255,255,255,0.05);border-radius:var(--r-md);padding:12px 20px;backdrop-filter:blur(10px)}
.stat-card .label{font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px}
.stat-card .value{font-size:20px;font-weight:700;font-family:var(--font-mono);margin-top:2px}
.section{margin-bottom:40px}
.section-title{font-size:clamp(16px,2vw,22px);font-weight:700;margin-bottom:20px;padding-left:12px;border-left:3px solid var(--accent)}
.sub-title{font-size:15px;font-weight:600;color:var(--text-secondary);margin:24px 0 12px;padding-top:16px;border-top:1px solid var(--border)}
.pillar-header{display:flex;align-items:center;gap:12px;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.pillar-header .pillar-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.pillar-header h2{font-size:clamp(16px,2vw,20px);font-weight:700;margin:0}
.pillar-header .pillar-sub{font-size:12px;color:var(--text-muted);margin-top:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:20px;transition:transform .2s}
.card:hover{transform:translateY(-2px)}
.card-title{font-size:14px;font-weight:600;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.card-title .icon{font-size:18px}
.card-label{font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
.card-value{font-size:22px;font-weight:700;font-family:var(--font-mono)}
.card-sub{font-size:12px;color:var(--text-secondary);margin-top:4px}
.tc{text-align:center;padding:16px}
.pillar-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.pillar{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:16px;text-align:center}
.pillar.unknown{opacity:0.4;border-style:dashed}
.pillar .pillar-label{font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px}
.pillar .kanji{font-size:28px;font-weight:700;line-height:1.2}
.pillar .reading{font-size:11px;color:var(--text-secondary);margin-top:4px}
.element-badge{display:inline-block;font-size:10px;font-weight:500;padding:2px 10px;border-radius:12px;margin-top:8px}
.elem-wood{background:rgba(34,197,94,0.15);color:#4ade80}
.elem-fire{background:rgba(239,68,68,0.15);color:#f87171}
.elem-earth{background:rgba(234,179,8,0.15);color:#facc15}
.elem-metal{background:rgba(148,163,184,0.15);color:#94a3b8}
.elem-water{background:rgba(59,130,246,0.15);color:#60a5fa}
.element-bar{display:flex;gap:8px;align-items:end;height:100px;margin:16px 0}
.element-col{flex:1;display:flex;flex-direction:column;align-items:center;gap:4px}
.element-fill{width:100%;border-radius:4px 4px 0 0;transition:height .6s ease}
.element-pct{font-size:12px;font-weight:600;font-family:var(--font-mono)}
.element-name{font-size:11px;color:var(--text-muted)}
.domain-bar{margin-bottom:12px}
.domain-header{display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px}
.domain-track{height:8px;background:var(--surface2);border-radius:4px;overflow:hidden}
.domain-fill{height:100%;border-radius:4px;transition:width .6s ease}
.top5-list{list-style:none}
.top5-item{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border)}
.top5-item:last-child{border-bottom:none}
.rank{width:28px;height:28px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-size:12px;font-weight:700;font-family:var(--font-mono);background:rgba(99,102,241,0.15);color:var(--accent);flex-shrink:0}
.sf-name{font-size:14px;font-weight:600}
.sf-domain{font-size:11px;color:var(--text-muted)}
.tag{display:inline-block;font-size:11px;font-weight:500;padding:3px 10px;border-radius:12px;margin:2px}
.tag-rb{background:rgba(59,130,246,0.15);color:#60a5fa}
.tag-st{background:rgba(34,197,94,0.15);color:#4ade80}
.tag-ex{background:rgba(139,92,246,0.15);color:#c4b5fd}
.tag-inf{background:rgba(255,107,53,0.15);color:#ff8f6b}
.typo-cell{background:var(--surface2);border-radius:var(--r-sm);padding:10px}
.typo-label{font-size:10px;color:var(--text-muted);text-transform:uppercase}
.typo-value{font-size:18px;font-weight:700;margin-top:2px}
.typo-sub{font-size:11px;color:var(--text-secondary)}
.typo-desc{font-size:11px;color:var(--text-muted);line-height:1.5;margin-top:6px}
.cycle-table{width:100%;border-collapse:collapse;font-size:13px}
.cycle-table th{text-align:left;padding:8px 10px;color:var(--text-muted);font-weight:500;border-bottom:1px solid var(--border)}
.cycle-table td{padding:8px 10px;border-bottom:1px solid rgba(45,51,72,0.5)}
.cycle-table tr.current{background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3)}
.satsukai{font-size:11px;padding:2px 8px;border-radius:10px;font-weight:600}
.dai{background:rgba(239,68,68,0.15);color:var(--red)}
.chu{background:rgba(234,179,8,0.15);color:var(--yellow)}
.sho{background:rgba(234,179,8,0.1);color:var(--yellow)}
.chart-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:16px;margin:16px 0}
.unlock-banner{background:rgba(234,179,8,0.08);border:1px dashed rgba(234,179,8,0.3);border-radius:var(--r-md);padding:16px 20px;font-size:12px;color:var(--yellow);text-align:center;margin-top:16px}
.insight-box{background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.06));border:1px solid rgba(99,102,241,0.2);border-radius:var(--r-md);padding:20px;margin-bottom:16px}
.insight-box .insight-title{font-size:13px;font-weight:600;color:#a5b4fc;margin-bottom:8px}
.insight-box p{font-size:13px;color:var(--text-secondary);line-height:1.7}
.section-desc{font-size:13px;color:var(--text-muted);margin-bottom:16px}
.year-timeline{display:flex;gap:2px;margin:16px 0}
.yt-month{flex:1;height:24px;border-radius:3px;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:600;color:rgba(255,255,255,0.7);cursor:pointer;transition:all .2s}
.yt-month:hover{transform:scaleY(1.3)}
.month-selector{display:flex;gap:4px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:8px 0;margin-bottom:20px}
.month-selector::-webkit-scrollbar{display:none}
.month-btn{flex-shrink:0;padding:8px 14px;border-radius:8px;background:var(--surface);border:1px solid var(--border);color:var(--text-muted);font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;white-space:nowrap;font-family:var(--font-body)}
.month-btn:hover{background:var(--surface2);color:var(--text-secondary)}
.month-btn.active{background:rgba(99,102,241,0.15);color:#a5b4fc;border-color:rgba(99,102,241,0.4)}
.month-btn.current{box-shadow:0 0 0 1px rgba(99,102,241,0.5)}
.month-panel{display:none}
.month-panel.active{display:block}
.month-card-header{display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border)}
.month-label{font-size:18px;font-weight:700;font-family:var(--font-mono)}
.month-tags{display:flex;gap:6px;flex-wrap:wrap}
.month-tag{font-size:10px;font-weight:500;padding:2px 8px;border-radius:10px}
.domain-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.domain-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:16px;border-left:3px solid var(--accent)}
.domain-card.work{border-left-color:var(--blue)}
.domain-card.money{border-left-color:var(--gold)}
.domain-card.health{border-left-color:var(--green)}
.domain-card.romance{border-left-color:#f472b6}
.domain-icon-label{display:flex;align-items:center;gap:8px}
.domain-label{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.domain-stars{font-family:var(--font-mono);font-size:13px;letter-spacing:1px}
.domain-msg{font-size:11px;color:var(--text-secondary);line-height:1.5;margin-top:6px}
.chart-legend{display:flex;flex-direction:column;gap:10px;margin-top:12px;padding:16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md)}
.chart-legend-item{display:flex;align-items:flex-start;gap:10px}
.chart-legend-line{display:inline-block;width:24px;height:3px;border-radius:2px;margin-top:7px;flex-shrink:0}
.chart-legend-label{font-size:13px;font-weight:600;margin-right:6px}
.chart-legend-desc{font-size:12px;color:var(--text-secondary)}
.page-footer{text-align:center;padding:32px 0;font-size:11px;color:var(--text-muted);border-top:1px solid var(--border);margin-top:40px}
@media(max-width:768px){.grid{grid-template-columns:1fr}.pillar-grid{grid-template-columns:repeat(2,1fr)}.domain-grid{grid-template-columns:1fr}}
@media(max-width:640px){
  .nav-toggle-label{display:inline-flex}
  .site-header{flex-wrap:wrap;gap:8px;padding:8px 12px;height:auto}
  .site-nav{display:none;width:100%;flex-direction:column;gap:4px;padding-top:8px}
  .nav-toggle:checked~.site-nav{display:flex}
  .nav-toggle:checked+.nav-toggle-label span{background:transparent}
  .nav-toggle:checked+.nav-toggle-label span::before{top:0;transform:rotate(45deg)}
  .nav-toggle:checked+.nav-toggle-label span::after{top:0;transform:rotate(-45deg)}
  .site-nav a{padding:8px 12px;font-size:12px;min-height:44px}
  .container{padding:12px}
  .hero{padding:20px 16px;border-radius:var(--r-md)}
  .stats{gap:8px}.stat-card{padding:8px 12px}
  .stat-card .value{font-size:16px}
  .pillar .kanji{font-size:22px}
}
</style>'''


def generate_html(p, tier=2):
    name = p['identity']['name']
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Self-Insight — {name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+JP:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
{CSS}
</head>
<body>
{_gnav()}
{_section_nav(tier >= 2)}
<div class="container">
{_hero(p, tier)}
{_core_identity(p)}
{_personality(p, tier)}
{_divination(p)}
{_forecast(p)}
{_monthly(p)}
{_cross_analysis(p)}
{_footer(tier)}
</div>
{_charts_js(p)}
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='Generate Self-Insight Dashboard')
    parser.add_argument('--profile', required=True, help='Path to profile.yaml')
    parser.add_argument('--output', required=True, help='Output HTML path')
    parser.add_argument('--tier', type=int, default=2, help='Completed tier (1, 2, or 3)')
    args = parser.parse_args()

    profile = load_yaml(args.profile)
    html = generate_html(profile, tier=args.tier)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(html)
    print(f'Dashboard written to {args.output}')


if __name__ == '__main__':
    main()
