#!/usr/bin/env python3
"""Generate Self-Insight dashboard HTML from profile.yaml."""
import argparse, os
import sys as _sys
from pathlib import Path as _Path
from datetime import date as _date

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from sections import *

def generate_html(p, tier=2, show_gnav=False):
    name = p['identity']['name']
    archetype = _get_archetype(p)
    gender_css = CSS_FEMALE if p.get('identity', {}).get('sex', 'male') == 'female' else ''
    gnav_html = _gnav() if show_gnav else ''

    # Generate all sections
    dm = p['four_pillars']['day_master']
    ys = p['nine_star_ki']['year_star']
    essence_sub = _get_essence_sub(dm, ys)

    core_id_content = _core_identity(p)
    core_summary = f'{dm["char"]}火 × {ys["name"]} — {essence_sub}' if essence_sub else f'{dm["char"]}火 × {ys["name"]}'

    mf = p.get('monthly_fortune', [])
    current_month_num = _date.today().month
    cur_month = next((m for m in mf if m['month'] == current_month_num), None)
    if cur_month:
        domains = cur_month['domains']
        avg = sum(domains.values()) / len(domains)
        tones = {4: '追い風の月', 3: '安定の月', 2: '慎重の月'}
        month_tone = tones.get(int(avg), '充電の月') if avg >= 2 else '充電の月'
        month_summary = f'{current_month_num}月 — {month_tone}'
    else:
        month_summary = '月間運気データなし'

    blueprint_content = _action_blueprint(p)
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    if sf_top5:
        top_ja = SF_JA.get(sf_top5[0]['name'], sf_top5[0]['name'])
        bp_summary = f'{sf_top5[0]["name"]}（{top_ja}）を武器にする'
    else:
        bp_summary = '自分の本質を活かす行動指針'

    personality_content = _personality(p, tier)
    divination_content = _divination(p)
    forecast_content = _forecast(p)
    monthly_content = _monthly(p)
    cross_content = _cross_analysis(p)
    try:
        money_content = _money_section(p)
    except Exception:
        money_content = ''
    try:
        work_content = _work_section(p)
    except Exception:
        work_content = ''
    try:
        relationships_content = _relationships_section(p)
    except Exception:
        relationships_content = ''
    try:
        life_arc_content = _life_arc_section(p)
    except Exception:
        life_arc_content = ''

    # Wrap sections in hub cards
    hub_sections = ''

    # Core Identity — FIRST (most important, permanent self)
    hub_sections += _hub_card('core-identity', '&#9733;', 'rgba(99,102,241,0.12)', '#a5b4fc',
                              'あなたの本質', core_summary, core_id_content)

    # Tier 1 新規: 干支 × 血液型
    try:
        eto_animal = p['four_pillars']['year_pillar']['branch'].get('animal', '')
        bt_type = p.get('blood_type', {}).get('type', '')
        eto_title_jp = ETO_PROFILES.get(eto_animal, {}).get('jp', '')
        eto_summary = f'{eto_title_jp}年 × {bt_type}型 — 日本人の希少組み合わせ'
        hub_sections += _hub_card('eto-blood', '&#9775;', 'rgba(251,191,36,0.12)', 'var(--accent-amber-light)',
                                  '干支 × 血液型', eto_summary, _eto_section(p))
    except Exception:
        pass

    # Tier 1 新規: 5体系整合マップ
    hub_sections += _hub_card('integration-map', '&#9881;', 'rgba(34,197,94,0.12)', '#86efac',
                              '5つの体系が示す、あなたの軸', '多数決で浮かび上がる「本当のあなた」',
                              _integration_map(p))

    # Tier 1 新規: クロスリファレンス・インサイト（複数体系の一致/矛盾から深掘り）
    hub_sections += _hub_card('cross-reference', '&#10021;', 'rgba(99,102,241,0.12)', '#a5b4fc',
                              'クロスリファレンス・インサイト', '体系を跨いだ一致点と矛盾点から読む「あなた」',
                              _cross_reference_insight(p))

    # Tier 1 新規: 強み/罠の裏返し構造（CliftonStrengths Shadow Side パターン）
    hub_sections += _hub_card('strengths-traps', '&#9876;', 'rgba(236,72,153,0.12)', '#f9a8d4',
                              '強み × 裏返しの罠', 'あなたの強みが暴走した時の落とし穴',
                              _strengths_traps_section(p))

    # Action Blueprint
    if blueprint_content:
        hub_sections += _hub_card('blueprint', '&#9829;', 'rgba(139,92,246,0.12)', 'var(--accent-purple-light)',
                                  '明日からできること', bp_summary, blueprint_content)

    # Personality
    if personality_content:
        hub_sections += _hub_card('personality', '&#9632;', 'rgba(59,130,246,0.12)', 'var(--accent-blue-light)',
                                  '内なる才能の設計図', '強み × 性格タイプ × 感受性',
                                  personality_content)

    # Divination
    hub_sections += _hub_card('divination', '&#9679;', 'rgba(139,92,246,0.12)', 'var(--accent-purple-light)',
                              '星が語ること',
                              f'{_glossary_tooltip("四柱推命")} × {_glossary_tooltip("九星気学")} × {_glossary_tooltip("六星占術")} × {_glossary_tooltip("太陽星座", "西洋占星術")}',
                              divination_content)

    # Forecast
    hub_sections += _hub_card('forecast-2026', '&#9650;', 'rgba(234,179,8,0.12)', '#facc15',
                              '2026年 — いま、あなたはどこにいるか',
                              f'{_glossary_tooltip("九星気学")} × {_glossary_tooltip("六星占術")}が示す年間の流れ',
                              forecast_content)

    # Monthly — guidance is shown inline via JS buildGuidanceHtml() for the current month tab
    if monthly_content:
        hub_sections += _hub_card('monthly', '&#9671;', 'rgba(59,130,246,0.12)', 'var(--accent-blue-light)',
                                  '月間運勢フォーキャスト', month_summary,
                                  monthly_content)

    # Cross Analysis
    if cross_content:
        hub_sections += _hub_card('cross', '&#10022;', 'rgba(99,102,241,0.12)', '#a5b4fc',
                                  '才能 × 運命 — 交差点のインサイト', '強み × 運気の掛け合わせが生むシナジー',
                                  cross_content)

    # Money — premium deep-dive
    if money_content:
        interp = p.get('interpretations', {})
        money_summary = interp.get('money', {}).get('headline', '金運の流れを読む')
        hub_sections += _hub_card('money', '&#165;', 'rgba(161,98,7,0.12)', 'var(--gold)',
                                  '金運 — 富の流れ', money_summary, money_content)

    # Work — premium deep-dive
    if work_content:
        interp = p.get('interpretations', {})
        work_summary = interp.get('work', {}).get('headline', '仕事運の流れを読む')
        hub_sections += _hub_card('work', '&#9874;', 'rgba(29,78,216,0.12)', 'var(--accent-blue-light)',
                                  '仕事運 — 才能を積み上げる場所', work_summary, work_content)

    # Relationships — premium deep-dive
    if relationships_content:
        interp = p.get('interpretations', {})
        rel_summary = interp.get('relationships', {}).get('headline', '人間関係の型を読む')
        hub_sections += _hub_card('relationships', '&#9826;', 'rgba(190,51,78,0.12)', 'var(--accent-red-light)',
                                  '人間関係 — 縁の設計図', rel_summary, relationships_content)

    # Life Arc — premium deep-dive (past & future)
    if life_arc_content:
        interp = p.get('interpretations', {})
        arc_summary = interp.get('life_arc', {}).get('headline', '12年サイクルで見る物語')
        hub_sections += _hub_card('life-arc', '&#8734;', 'rgba(15,118,110,0.12)', 'var(--accent-teal-light)',
                                  '過去と未来 — 12年の物語', arc_summary, life_arc_content)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{archetype["ja"]} — {name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400..800&family=Noto+Sans+JP:wght@400..900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
{CSS}
{gender_css}
</head>
<body>
{gnav_html}
<div class="container">
{_hero(p, tier)}
{_glossary_card()}
{hub_sections}
{_footer(tier)}
</div>
{_charts_js(p)}
<div id="gloss-tip"></div>
<script>
(function(){{
  var tip=document.getElementById('gloss-tip');
  var active=null;
  function show(el){{
    var txt=el.getAttribute('data-tip');
    if(!txt)return;
    tip.textContent=txt;
    tip.style.display='block';
    tip.style.opacity='0';
    var r=el.getBoundingClientRect();
    var vw=window.innerWidth,vh=window.innerHeight;
    var tw=Math.min(320,vw-20);
    tip.style.maxWidth=tw+'px';
    // position above element, fallback below
    var top=r.top-tip.offsetHeight-10;
    if(top<8)top=r.bottom+8;
    var left=r.left+(r.width/2)-(tw/2);
    if(left<8)left=8;
    if(left+tw>vw-8)left=vw-tw-8;
    tip.style.top=top+'px';
    tip.style.left=left+'px';
    tip.style.opacity='1';
    active=el;
  }}
  function hide(){{tip.style.opacity='0';tip.style.display='none';active=null;}}
  document.querySelectorAll('abbr.term').forEach(function(el){{
    el.addEventListener('mouseenter',function(){{show(el);}});
    el.addEventListener('mouseleave',hide);
    el.addEventListener('focus',function(){{show(el);}});
    el.addEventListener('blur',hide);
    el.addEventListener('click',function(e){{e.stopPropagation();if(active===el)hide();else show(el);}});
  }});
  document.addEventListener('click',function(){{if(active)hide();}});
}})();
</script>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser(description='Generate Self-Insight Dashboard')
    parser.add_argument('--profile', required=True, help='Path to profile.yaml')
    parser.add_argument('--output', required=True, help='Output HTML path')
    parser.add_argument('--tier', type=int, default=2, help='Completed tier (1, 2, or 3)')
    parser.add_argument('--gnav', action='store_true', help='Show iUMA private navigation (for personal use)')
    args = parser.parse_args()

    profile = load_yaml(args.profile)
    html = generate_html(profile, tier=args.tier, show_gnav=args.gnav)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(html)
    print(f'Dashboard written to {args.output}')

if __name__ == '__main__':
    main()
