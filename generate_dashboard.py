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
HSP_LABELS = {'low':'低感受性','medium':'中程度','high':'高感受性'}
ADHD_LABELS = {'minimal':'低傾向','leaning':'やや傾向あり','significant':'傾向あり'}

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

    return f'''<section class="section" id="core-identity">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(99,102,241,0.15);color:#a5b4fc">&#9733;</div>
    <div><h2>Core Identity — あなたはこういう人</h2>
      <div class="pillar-sub">6つの分析体系が示す、時代を超えた人物像</div></div>
  </div>
  <div class="grid grid-4">
    <div class="card tc"><div class="card-label">Core Essence</div>
      <div class="card-value">{dm["char"]}火 × {ys["name"]}</div>
      <div class="card-sub">静かな炎 × 言葉の力</div></div>
    <div class="card tc"><div class="card-label">Strongest Axis</div>
      <div class="card-value">共感 × 洞察</div>
      <div class="card-sub">Empathy + Intellection + HSP</div></div>
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
    sf_html = ''
    if sf_top5:
        items = ''
        for s in sf_top5:
            tc = tag_cls.get(s.get('domain',''), 'tag-rb')
            items += f'''<li class="top5-item"><span class="rank">{s["rank"]}</span>
          <div><div class="sf-name">{s["name"]}</div>
          <div class="sf-domain"><span class="tag {tc}">{s["domain"]}</span></div></div></li>'''
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
            <div class="typo-value">Type {etype}</div><div class="typo-sub">{ename}</div></div>
          <div class="typo-cell"><div class="typo-label">Blood Type</div>
            <div class="typo-value">{bt["type"]}</div><div class="typo-sub">日本人口の{bt["population_pct"]}%</div></div>
          <div class="typo-cell"><div class="typo-label">HSP</div>
            <div class="typo-value" style="color:#facc15">{hsp_label}</div><div class="typo-sub">感覚処理感受性</div></div>
          <div class="typo-cell"><div class="typo-label">ADHD</div>
            <div class="typo-value" style="color:#ff8f6b">{adhd_label}</div><div class="typo-sub">過集中×散漫の波</div></div>
        </div></div>
    </div></div>'''

    return f'''<section class="section" id="personality">
  <h2 class="section-title">Personality Profile</h2>
  {sf_html}
</section>'''


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

    pillar_labels = ['年柱', '月柱', '日柱']
    elem_cls = {'Wood':'elem-wood','Fire':'elem-fire','Earth':'elem-earth','Metal':'elem-metal','Water':'elem-water'}
    pcards = ''
    for i, pl in enumerate(pillars):
        ec = elem_cls.get(pl['stem']['element'], '')
        pcards += f'''<div class="pillar"><div class="pillar-label">{pillar_labels[i]}</div>
      <div class="kanji">{pl["full"]}</div>
      <div class="reading">{pl["stem"]["reading"]}・{pl["branch"]["reading"]}</div>
      <div class="element-badge {ec}">{pl["stem"]["element"]}</div></div>'''
    pcards += '<div class="pillar unknown"><div class="pillar-label">時柱</div><div class="kanji">？？</div><div class="reading">出生時刻不明</div></div>'

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

    return f'''<section class="section" id="divination">
  <h2 class="section-title">占術プロファイル</h2>

  <h3 class="sub-title">四柱推命</h3>
  <div class="pillar-grid">{pcards}</div>
  <div class="card" style="margin-top:12px"><div class="card-label">日主（Day Master）</div>
    <div class="card-value">{dm["char"]}（{dm["element"]}）</div><div class="card-sub">{dm["description"]}</div></div>
  <div class="element-bar">{el_bars}</div>
  {missing_html}

  <h3 class="sub-title">九星気学</h3>
  {nsk_cards}
  <div class="chart-wrap"><canvas id="chart9" height="200"></canvas></div>

  <h3 class="sub-title">六星占術</h3>
  {rok_cards}
  {"<div class='chart-wrap'><canvas id='chartComb' height='200'></canvas></div>" if rok.get('reigou_combined') else ""}
  <div style="margin-top:12px">{table}</div>

  <h3 class="sub-title">西洋占星術</h3>
  <div class="grid grid-3">
    <div class="card"><div class="card-label">太陽星座</div>
      <div class="card-value">{west["symbol"]} {west["sign"]}</div>
      <div class="card-sub">{west["element"]} / {west["quality"]}</div></div>
    <div class="card"><div class="card-label">支配星</div>
      <div class="card-value">{p["western_astrology"].get("ruling_planet","")}</div></div>
  </div>
  <div class="unlock-banner">出生時刻を追加すると、時柱・アセンダント・月星座が解放されます</div>
</section>'''


def _forecast(p):
    nsk = p['nine_star_ki']
    rok = p['rokusei']
    cur9 = next((c for c in nsk.get('nine_year_cycle', []) if c.get('current')), None)
    cur12 = next((c for c in rok.get('twelve_year_cycle', []) if c.get('current')), None)
    cur_sub = next((c for c in rok.get('sub_star_cycle', []) if c.get('current')), None)
    cur_comb = next((c for c in rok.get('reigou_combined', []) if c.get('year') == 2026), None)

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

    return f'''<section class="section" id="forecast-2026">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(234,179,8,0.15);color:#facc15">&#9733;</div>
    <div><h2>2026年 運勢フォーキャスト</h2>
      <div class="pillar-sub">九星気学 × 六星占術が示す年間の流れ</div></div>
  </div>
  {cards}
  <div class="chart-wrap"><canvas id="chartOverlay" height="280"></canvas></div>
</section>'''


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

    # Month panels
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
      <div class="domain-card work"><div class="domain-icon-label"><div class="domain-label" style="color:var(--blue)">仕事</div><div class="domain-stars">${{starRating(m.work)}}</div></div></div>
      <div class="domain-card money"><div class="domain-icon-label"><div class="domain-label" style="color:var(--gold)">お金</div><div class="domain-stars">${{starRating(m.money)}}</div></div></div>
      <div class="domain-card health"><div class="domain-icon-label"><div class="domain-label" style="color:var(--green)">健康</div><div class="domain-stars">${{starRating(m.health)}}</div></div></div>
      <div class="domain-card romance"><div class="domain-icon-label"><div class="domain-label" style="color:#f472b6">恋愛</div><div class="domain-stars">${{starRating(m.romance)}}</div></div></div>
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

    chart9_labels = json.dumps([str(c['year']) for c in cycle9])
    chart9_data = json.dumps([c['energy'] for c in cycle9])
    chart9_colors = json.dumps(['#22c55e' if c.get('current') else '#6366f1' for c in cycle9])

    comb_labels = json.dumps([str(c['year']) for c in combined])
    comb_scores = json.dumps([c['score'] for c in combined])
    comb_colors = json.dumps(['#22c55e' if c.get('year') == 2026 else '#8b5cf6' for c in combined])

    # 3-line overlay data
    nine_by_year = {c['year']: c['energy'] for c in cycle9}
    twelve_by_year = {c['year']: c['energy'] for c in cycle12}
    comb_by_year = {c['year']: c['score'] for c in combined}
    years = sorted(set(list(nine_by_year) + list(twelve_by_year) + list(comb_by_year)))
    overlay_labels = json.dumps([str(y) for y in years])
    nine_data = json.dumps([nine_by_year.get(y) for y in years])
    twelve_data = json.dumps([twelve_by_year.get(y) for y in years])
    comb_data = json.dumps([comb_by_year.get(y) for y in years])

    return f'''<script>
const chartOpts=(ds)=>({{type:'line',data:ds,options:{{responsive:true,plugins:{{legend:{{display:false}}}},
  scales:{{x:{{ticks:{{color:'#7c8293',font:{{family:"'JetBrains Mono',monospace",size:11}}}},grid:{{color:'rgba(255,255,255,0.05)'}}}},
    y:{{min:0,max:110,ticks:{{display:false}},grid:{{color:'rgba(255,255,255,0.05)'}}}}}}
}}}});
new Chart(document.getElementById('chart9'),chartOpts({{
  labels:{chart9_labels},
  datasets:[{{label:'九星気学',data:{chart9_data},borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,0.1)',fill:true,tension:0.3,pointRadius:5,pointBackgroundColor:{chart9_colors}}}]
}}));
{f"""new Chart(document.getElementById('chartComb'),chartOpts({{
  labels:{comb_labels},
  datasets:[{{label:'霊合統合',data:{comb_scores},borderColor:'#8b5cf6',backgroundColor:'rgba(139,92,246,0.1)',fill:true,tension:0.3,pointRadius:5,pointBackgroundColor:{comb_colors}}}]
}}));""" if combined else ""}
new Chart(document.getElementById('chartOverlay'),{{
  type:'line',
  data:{{labels:{overlay_labels},datasets:[
    {{label:'九星気学',data:{nine_data},borderColor:'#6366f1',fill:false,tension:0.4,borderWidth:2,pointRadius:4,pointBackgroundColor:'#6366f1'}},
    {{label:'六星占術',data:{twelve_data},borderColor:'#22c55e',fill:false,tension:0.4,borderWidth:2,pointRadius:4,pointBackgroundColor:'#22c55e'}},
    {{label:'霊合合成',data:{comb_data},borderColor:'#eab308',fill:false,tension:0.4,borderWidth:2,borderDash:[6,3],pointRadius:4,pointBackgroundColor:'#eab308'}}
  ]}},
  options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},
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
body{font-family:var(--font-body);background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}
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
.hero{background:linear-gradient(135deg,#1e1b4b,#312e81,#1e1b4b);border-radius:var(--r-xl);padding:40px 32px;margin-bottom:32px;border:1px solid var(--border);overflow:hidden}
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
.page-footer{text-align:center;padding:32px 0;font-size:11px;color:var(--text-muted);border-top:1px solid var(--border);margin-top:40px}
@media(max-width:768px){.grid{grid-template-columns:1fr}.pillar-grid{grid-template-columns:repeat(2,1fr)}}
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
