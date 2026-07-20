"""Premium narrative sections: money / work / relationships / life-arc.

All content is sourced from profile.yaml's `interpretations` block (the same
SSoT already consumed by core_identity.py / divination_forecast.py / monthly.py).
Each section degrades to '' when its interpretations key is absent, so users
without this content simply don't render the section.
"""

def _insight_box(title, paragraphs, accent_bg, accent_color):
    """Progressive-disclosure prose box: first paragraph visible, rest foldable."""
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return ''
    first_p = f'<p style="line-height:1.9;font-size:14px;">{paragraphs[0]}</p>'
    if len(paragraphs) == 1:
        return f'''<div class="insight-box" style="border-color:{accent_bg};background:linear-gradient(135deg,{accent_bg},rgba(255,255,255,0.02));">
    <div class="insight-title" style="font-size:15px;color:{accent_color}">{title}</div>
    {first_p}
  </div>'''
    rest_ps = ''.join(f'<p style="line-height:1.9;font-size:14px;margin-top:12px;">{para}</p>' for para in paragraphs[1:])
    return f'''<div class="insight-box" style="border-color:{accent_bg};background:linear-gradient(135deg,{accent_bg},rgba(255,255,255,0.02));">
    <div class="insight-title" style="font-size:15px;color:{accent_color}">{title}</div>
    {first_p}
    <div class="collapsible-content" style="display:none">{rest_ps}</div>
    <button class="collapse-toggle" onclick="this.previousElementSibling.style.display=this.previousElementSibling.style.display==='none'?'block':'none';this.textContent=this.previousElementSibling.style.display==='none'?'続きを読む':'閉じる'">続きを読む</button>
  </div>'''

def _practice_watch(practice_guide, caution, accent_bg, accent_color, icon='&#9670;'):
    practice_html = ''
    if practice_guide:
        practice_html = f'''<div class="guidance-action">
      <div class="guidance-action-icon" style="background:{accent_bg};color:{accent_color}">{icon}</div>
      <div><div class="guidance-action-title">明日からできること</div>
      <div class="guidance-action-desc">{practice_guide}</div></div>
    </div>'''
    watch_html = ''
    if caution:
        watch_html = f'''<div class="guidance-watch" style="margin-top:16px">
      <div class="guidance-watch-title">気をつけること</div>
      <div class="guidance-watch-item">{caution}</div>
    </div>'''
    return practice_html + watch_html

def _month_highlight_cards(mf, domain_key, good_color, bad_color):
    """Best/worst month stat cards from monthly_fortune's domain scores."""
    scored = [(m['month'], m['domains'].get(domain_key)) for m in mf if domain_key in m.get('domains', {})]
    if not scored:
        return ''
    best = max(scored, key=lambda x: x[1])
    worst = min(scored, key=lambda x: x[1])
    return f'''<div class="grid">
    <div class="card tc"><div class="card-label">2026年 好調月</div>
      <div class="card-value" style="color:{good_color}">{best[0]}月</div>
      <div class="card-sub">スコア {best[1]}/5</div></div>
    <div class="card tc"><div class="card-label">2026年 要注意月</div>
      <div class="card-value" style="color:{bad_color}">{worst[0]}月</div>
      <div class="card-sub">スコア {worst[1]}/5</div></div>
  </div>'''

def _money_section(p):
    interp = p.get('interpretations', {})
    d = interp.get('money')
    if not d:
        return ''
    mf = p.get('monthly_fortune', [])
    accent_bg, accent_color = 'rgba(161,98,7,0.12)', 'var(--gold)'

    banner = f'''<div class="year-theme-banner" style="background:linear-gradient(135deg,rgba(161,98,7,0.10),rgba(161,98,7,0.02))">
    <div class="year-theme-label">金運の型</div>
    <div class="year-theme-text" style="color:var(--gold)">{d.get('headline', '')}</div>
  </div>'''

    cards = _month_highlight_cards(mf, 'money', 'var(--accent-green-light)', 'var(--accent-red-light)')
    insight = _insight_box('金運の分析', [d.get('intro', ''), d.get('yearly_pattern', ''), d.get('analysis', '')], accent_bg, accent_color)
    action = _practice_watch(d.get('practice_guide', ''), d.get('caution', ''), accent_bg, accent_color, icon='&#165;')

    return f'''<section class="section" id="money-fortune">
  {banner}
  {cards}
  {insight}
  {action}
</section>'''

def _work_section(p):
    interp = p.get('interpretations', {})
    d = interp.get('work')
    if not d:
        return ''
    mf = p.get('monthly_fortune', [])
    accent_bg, accent_color = 'rgba(29,78,216,0.12)', 'var(--accent-blue-light)'

    banner = f'''<div class="year-theme-banner" style="background:linear-gradient(135deg,rgba(29,78,216,0.10),rgba(29,78,216,0.02))">
    <div class="year-theme-label">仕事運の型</div>
    <div class="year-theme-text" style="color:var(--accent-blue-light)">{d.get('headline', '')}</div>
  </div>'''

    cards = _month_highlight_cards(mf, 'work', 'var(--accent-green-light)', 'var(--accent-red-light)')
    insight = _insight_box('仕事運の分析', [d.get('intro', ''), d.get('yearly_pattern', ''), d.get('analysis', '')], accent_bg, accent_color)
    action = _practice_watch(d.get('practice_guide', ''), d.get('caution', ''), accent_bg, accent_color, icon='&#9874;')

    return f'''<section class="section" id="work-fortune">
  {banner}
  {cards}
  {insight}
  {action}
</section>'''

def _relationships_section(p):
    interp = p.get('interpretations', {})
    d = interp.get('relationships')
    if not d:
        return ''
    accent_bg, accent_color = 'rgba(190,51,78,0.12)', 'var(--accent-red-light)'

    banner = f'''<div class="year-theme-banner" style="background:linear-gradient(135deg,rgba(190,51,78,0.10),rgba(190,51,78,0.02))">
    <div class="year-theme-label">人間関係の型</div>
    <div class="year-theme-text" style="color:var(--accent-red-light)">{d.get('headline', '')}</div>
  </div>'''

    intro = _insight_box('複数体系が示す関係構築の型', [d.get('intro', '')], accent_bg, accent_color)

    pillar_cards = '<div class="grid">'
    for pillar in d.get('pillars', []):
        pillar_cards += f'''<div class="card">
      <div class="card-label" style="color:{accent_color}">{pillar.get('title', '')}</div>
      <p style="line-height:1.8;font-size:13px;margin-top:8px">{pillar.get('analysis', '')}</p>
      <div class="guidance-action" style="margin-top:12px">
        <div class="guidance-action-icon" style="background:{accent_bg};color:{accent_color}">&#9826;</div>
        <div><div class="guidance-action-title">実践のヒント</div>
        <div class="guidance-action-desc">{pillar.get('practice_guide', '')}</div></div>
      </div>
    </div>'''
    pillar_cards += '</div>'

    watch = ''
    if d.get('caution'):
        watch = f'''<div class="guidance-watch" style="margin-top:16px">
      <div class="guidance-watch-title">気をつけること</div>
      <div class="guidance-watch-item">{d['caution']}</div>
    </div>'''

    return f'''<section class="section" id="relationships">
  {banner}
  {intro}
  {pillar_cards}
  {watch}
</section>'''

def _life_arc_section(p):
    interp = p.get('interpretations', {})
    d = interp.get('life_arc')
    if not d:
        return ''
    accent_bg, accent_color = 'rgba(15,118,110,0.12)', 'var(--accent-teal-light)'
    peak_years = set(d.get('peak_years', []))
    caution_years = set(d.get('caution_years', []))

    banner = f'''<div class="year-theme-banner" style="background:linear-gradient(135deg,rgba(15,118,110,0.10),rgba(15,118,110,0.02))">
    <div class="year-theme-label">過去と未来</div>
    <div class="year-theme-text" style="color:var(--accent-teal-light)">{d.get('headline', '')}</div>
  </div>'''

    intro = _insight_box('12年サイクルの物語', [d.get('intro', '')], accent_bg, accent_color)

    def year_card(y, is_now=False):
        year = y.get('year')
        border_color = 'var(--border)'
        if year in peak_years:
            border_color = 'var(--accent-green-light)'
        elif year in caution_years:
            border_color = 'var(--accent-red-light)'
        now_badge = ' <span style="font-size:10px;color:var(--accent-teal-light)">← 今ここ</span>' if is_now else ''
        return f'''<div class="card" style="border-left:3px solid {border_color}">
      <div class="card-label">{year}年{now_badge}</div>
      <div class="card-value" style="font-size:16px">{y.get('label', '')}</div>
      <div class="card-sub">{y.get('narrative', '')}</div>
    </div>'''

    past_html = '<div class="grid">' + ''.join(year_card(y) for y in d.get('past', [])) + '</div>'
    now_html = '''<div class="card tc" style="border-left:3px solid var(--accent-teal-light);margin:16px 0">
    <div class="card-label">2026年 ← 今ここ</div>
    <div class="card-value" style="font-size:16px;color:var(--accent-teal-light)">物語の折り返し</div>
    <div class="card-sub">谷は越えた。ここからの3年が2029年の高さを決める</div>
  </div>'''
    future_html = '<div class="grid">' + ''.join(year_card(y) for y in d.get('future', [])) + '</div>'

    synthesis = _insight_box('12年を貫くテーマ', [d.get('synthesis', '')], accent_bg, accent_color)

    return f'''<section class="section" id="life-arc">
  {banner}
  {intro}
  {past_html}
  {now_html}
  {future_html}
  {synthesis}
</section>'''
