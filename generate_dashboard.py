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

# Japanese translations
SF_JA = {
    'Empathy': '共感性', 'Intellection': '内省', 'Deliberative': '慎重さ',
    'Connectedness': '運命思考', 'Maximizer': '最上志向', 'Futuristic': '未来志向',
    'Relator': '親密性', 'Activator': '活発性', 'Individualization': '個別化',
    'Learner': '学習欲', 'Input': '収集心', 'Ideation': '着想',
    'Command': '指令性', 'Context': '原点思考', 'Focus': '目標志向',
    'Developer': '成長促進', 'Achiever': '達成欲', 'Self-Assurance': '自己確信',
    'Arranger': 'アレンジ', 'Analytical': '分析思考', 'Responsibility': '責任感',
    'Consistency': '公平性', 'Positivity': 'ポジティブ', 'Strategic': '戦略性',
    'Adaptability': '適応性', 'Harmony': '調和性', 'Includer': '包含',
    'Communication': 'コミュニケーション', 'Woo': '社交性', 'Restorative': '回復志向',
    'Discipline': '規律性', 'Significance': '自我', 'Competition': '競争性',
    'Belief': '信念',
}
DOMAIN_JA = {
    'Relationship Building': '人間関係構築',
    'Strategic Thinking': '戦略的思考',
    'Executing': '実行力',
    'Influencing': '影響力',
}
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
    links = '<a href="#this-month">今月のあなたへ</a>'
    links += '<a href="#core-identity">Core Identity（自己本質）</a>'
    if has_personality:
        links += '<a href="#personality">Personality（性格特性）</a>'
    links += '<a href="#divination">占術プロファイル</a>'
    links += '<a href="#forecast-2026">2026 運勢</a>'
    links += '<a href="#monthly">月間運勢</a>'
    links += '<a href="#cross">Cross Analysis（クロス分析）</a>'
    return f'<nav class="nav-bar">{links}</nav>'


def _hero(p, tier):
    ident = p['identity']
    interp = p.get('interpretations', {})
    hero = interp.get('hero', {})
    rok = p['rokusei']

    # Tagline
    tagline = hero.get('tagline', '')
    tagline_html = f'<div class="hero-tagline">「{tagline}」</div>' if tagline else ''

    # Trait chips — human-readable with source labels
    traits = hero.get('traits', [])
    chips = ''
    for t in traits:
        chips += (f'<div class="hero-trait">'
                  f'<div class="hero-trait-keyword">{t["keyword"]}</div>'
                  f'<div class="hero-trait-detail">{t["detail"]}</div>'
                  f'<div class="hero-trait-source">{t["source"]}</div>'
                  f'</div>')

    # Stat card — plain language
    cur_comb = next((c for c in rok.get('reigou_combined', []) if c.get('year') == 2026), None)
    stats = ''
    if cur_comb:
        score = cur_comb['score']
        label = cur_comb.get('label', '')
        stats = (f'<div class="stat-card">'
                 f'<div class="label">2026年 総合運勢</div>'
                 f'<div class="value" style="color:{energy_color(score)}">{label}</div>'
                 f'<div class="stat-sub">{score} / 100</div>'
                 f'</div>')

    return f'''<section class="hero">
  <h1>Self-Insight</h1>
  <div class="subtitle">{ident["name"]} — AI自己分析ダッシュボード</div>
  {tagline_html}
  <div class="hero-traits">{chips}</div>
  <div class="stats">{stats}</div>
</section>'''


def _get_essence_sub(dm, ys):
    """Generate Core Essence sub-description from day master + year star."""
    dm_subs = {
        '丁': '静かな炎',
        '丙': '太陽の輝き',
        '甲': '大木の力',
        '乙': '草花のしなやかさ',
        '戊': '大地の安定',
        '己': '大地の柔軟さ',
        '庚': '鋼の意志',
        '辛': '宝石の繊細さ',
        '壬': '大河の流れ',
        '癸': '雨露の慈しみ',
    }
    ys_subs = {
        '七赤金星': '言葉の力',
        '五黄土星': '中央の統率力',
        '一白水星': '知恵と柔軟性',
        '二黒土星': '献身と安定',
        '三碧木星': '行動と成長',
        '四緑木星': '信用と調和',
        '六白金星': '権威と正義',
        '八白土星': '改革と蓄積',
        '九紫火星': '華やかさと直感',
    }
    dm_sub = dm_subs.get(dm.get('char', ''), '')
    ys_sub = ys_subs.get(ys.get('name', ''), '')
    if dm_sub and ys_sub:
        return f'{dm_sub} × {ys_sub}'
    return dm_sub or ys_sub or ''


def _get_duality_value(bt, ennea, rok):
    """Generate duality value from blood type + personality."""
    bt_traits = {
        'AB': '合理 × 感性',
        'A': '誠実 × 繊細',
        'B': '自由 × 情熱',
        'O': '大胆 × 包容',
    }
    return bt_traits.get(bt.get('type', ''), '独自の二面性')


def _get_missing_sub(missing):
    """Generate sub-description for missing elements."""
    elem_meanings = {
        '金': '決断力・収穫',
        '水': '柔軟性・知恵',
        '木': '成長力・発展',
        '火': '情熱・行動力',
        '土': '安定・信頼',
    }
    parts = []
    for m in missing[:2]:
        meaning = elem_meanings.get(str(m), '')
        if meaning:
            parts.append(meaning)
    if parts:
        return f'{" × ".join(parts)}を意識的に補う'
    return ''


def _this_month_guidance(p):
    """Generate 'This Month's Guidance' — the #1 value section right after Hero."""
    mf = p.get('monthly_fortune', [])
    current_month_num = _date.today().month
    cur_month = next((m for m in mf if m['month'] == current_month_num), None)
    if not cur_month:
        return ''

    interp = p.get('interpretations', {})
    hero = interp.get('hero', {})
    tagline = hero.get('tagline', '')
    dm = p['four_pillars']['day_master']
    ys = p['nine_star_ki']['year_star']
    rok = p['rokusei']
    west = p['western_astrology']['sun_sign']
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    ennea = p.get('personality', {}).get('enneagram', {})
    missing = p['four_pillars'].get('missing_elements', [])

    # Determine overall month energy
    domains = cur_month['domains']
    avg_stars = sum(domains.values()) / len(domains)
    nine_energy = cur_month['nine_star']['energy']
    rok_phase = cur_month['rokusei']['phase']
    rok_type = cur_month['rokusei']['type']

    # Month narrative — personalized by connecting traits to fortune
    month_label = f'{current_month_num}月'

    # Build narrative pieces
    if avg_stars >= 4:
        energy_tone = '追い風'
        energy_desc = 'エネルギーが高く、積極的に動ける月'
        energy_icon_bg = 'rgba(34,197,94,0.15)'
        energy_icon_color = '#4ade80'
        energy_icon = '&#9650;'  # up triangle
    elif avg_stars >= 3:
        energy_tone = '安定'
        energy_desc = '地固めと準備に適した月'
        energy_icon_bg = 'rgba(59,130,246,0.15)'
        energy_icon_color = '#60a5fa'
        energy_icon = '&#9654;'  # right triangle
    elif avg_stars >= 2:
        energy_tone = '慎重'
        energy_desc = '守りを固め、無理をしない月'
        energy_icon_bg = 'rgba(234,179,8,0.15)'
        energy_icon_color = '#facc15'
        energy_icon = '&#9660;'  # down triangle
    else:
        energy_tone = '充電'
        energy_desc = '休息と回復を最優先にする月'
        energy_icon_bg = 'rgba(239,68,68,0.15)'
        energy_icon_color = '#f87171'
        energy_icon = '&#9724;'  # square

    # Generate personalized action items based on profile + fortune
    actions = _generate_monthly_actions(p, cur_month, avg_stars)
    actions_html = ''
    for a in actions:
        actions_html += f'''<div class="guidance-action">
          <div class="guidance-action-icon" style="background:{a['icon_bg']};color:{a['icon_color']}">{a['icon']}</div>
          <div>
            <div class="guidance-action-title">{a['title']}</div>
            <div class="guidance-action-desc">{a['desc']}</div>
          </div>
        </div>'''

    # Watch out
    watch_items = _generate_monthly_watchouts(p, cur_month, avg_stars)
    watch_html = ''
    if watch_items:
        watch_html = '<div class="guidance-watch"><div class="guidance-watch-title">気をつけること</div>'
        for w in watch_items:
            watch_html += f'<div class="guidance-watch-item">{w}</div>'
        watch_html += '</div>'

    # Nine Star + Rokusei tags
    nine_note = cur_month['nine_star']['note']
    pc = _phase_color_py(rok_type)

    return f'''<section class="section" id="this-month">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:{energy_icon_bg};color:{energy_icon_color}">{energy_icon}</div>
    <div><h2>{month_label}のあなたへ</h2>
      <div class="pillar-sub">{energy_desc}</div></div>
  </div>
  <div class="guidance-summary">
    <div class="guidance-overview">
      <div class="guidance-energy-badge" style="background:{energy_icon_bg};color:{energy_icon_color};border:1px solid {energy_icon_color}">{energy_tone}</div>
      <div class="guidance-tags">
        <span class="month-tag" style="background:rgba(99,102,241,0.15);color:#a5b4fc">九星: {nine_note}</span>
        <span class="month-tag" style="background:{pc['bg']};color:{pc['color']};border:1px solid {pc['border']}">六星: {rok_phase}</span>
      </div>
    </div>
    <div class="guidance-narrative">{_generate_monthly_narrative(p, cur_month, avg_stars, energy_tone)}</div>
    <div class="guidance-actions-grid">
      <div class="guidance-actions-section">
        <div class="guidance-section-label">今月やるべきこと</div>
        {actions_html}
      </div>
      {watch_html}
    </div>
  </div>
</section>'''


def _phase_color_py(rtype):
    """Return phase color dict for Python-side rendering."""
    if rtype == 'great':
        return {'bg': 'rgba(34,197,94,0.12)', 'border': 'rgba(34,197,94,0.3)', 'color': '#4ade80'}
    if rtype == 'good':
        return {'bg': 'rgba(59,130,246,0.12)', 'border': 'rgba(59,130,246,0.3)', 'color': '#60a5fa'}
    if rtype == 'caution':
        return {'bg': 'rgba(234,179,8,0.12)', 'border': 'rgba(234,179,8,0.3)', 'color': '#facc15'}
    return {'bg': 'rgba(239,68,68,0.12)', 'border': 'rgba(239,68,68,0.3)', 'color': '#f87171'}


def _generate_monthly_narrative(p, cur_month, avg_stars, energy_tone):
    """Generate a personalized narrative for the current month."""
    dm = p['four_pillars']['day_master']
    ys = p['nine_star_ki']['year_star']
    west = p['western_astrology']['sun_sign']
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    missing = p['four_pillars'].get('missing_elements', [])
    ennea = p.get('personality', {}).get('enneagram', {})
    rok_phase = cur_month['rokusei']['phase']
    nine_note = cur_month['nine_star']['note']
    month_num = cur_month['month']

    top_strength = sf_top5[0]['name'] if sf_top5 else ''
    top_ja = SF_JA.get(top_strength, '')

    parts = []

    # Opening — connect personality to month
    if avg_stars >= 4:
        parts.append(f'{month_num}月は、あなたの持ち味が最も活きる月です。')
        if top_strength:
            parts.append(f'{top_strength}（{top_ja}）を全開にして、新しいことに積極的に挑戦してください。')
        parts.append(f'九星気学では「{nine_note}」、六星占術では「{rok_phase}」— 複数の体系が後押ししています。')
    elif avg_stars >= 3:
        parts.append(f'{month_num}月は、地道な積み上げが後に大きく効いてくる月です。')
        if top_strength:
            parts.append(f'{top_strength}（{top_ja}）を活かしつつ、着実に一歩ずつ前進する意識を。')
        parts.append(f'九星気学と六星占術で体系間に差があるため、バランス感覚が鍵になります。')
    elif avg_stars >= 2:
        parts.append(f'{month_num}月は、守りを固めて内面を充実させる月です。')
        parts.append(f'大きな決断は避け、情報収集と計画立案に集中してください。')
        if missing:
            missing_str = '・'.join(str(m) for m in missing)
            parts.append(f'五行で欠如している「{missing_str}」の要素を意識的に補うのが特に有効なタイミングです。')
    else:
        parts.append(f'{month_num}月は、無理をせず回復に専念する月です。')
        parts.append(f'この時期に充電したエネルギーが、次の好調期で花開きます。')
        if ennea:
            etype = ennea.get('type', '')
            stress = ennea.get('stress_direction', '')
            if stress:
                parts.append(f'エニアグラムType {etype}はストレス下でType {stress}に退行しやすいので、意識的にリラックスの時間を確保してください。')

    return ''.join(parts)


def _generate_monthly_actions(p, cur_month, avg_stars):
    """Generate 3 actionable items based on profile + current month fortune."""
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    ennea = p.get('personality', {}).get('enneagram', {})
    dm = p['four_pillars']['day_master']
    domains = cur_month['domains']
    actions = []

    # Best domain this month
    best_domain = max(domains, key=domains.get)
    domain_ja = {'work': '仕事', 'money': 'お金', 'health': '健康', 'romance': '人間関係'}
    domain_icons = {
        'work': ('&#9733;', 'rgba(59,130,246,0.15)', '#60a5fa'),
        'money': ('&#9830;', 'rgba(201,168,76,0.15)', '#c9a84c'),
        'health': ('&#9829;', 'rgba(34,197,94,0.15)', '#4ade80'),
        'romance': ('&#9827;', 'rgba(244,114,182,0.15)', '#f472b6'),
    }

    # Action 1: Leverage best domain
    icon_data = domain_icons.get(best_domain, ('&#9733;', 'rgba(99,102,241,0.15)', '#a5b4fc'))
    if avg_stars >= 3:
        actions.append({
            'title': f'{domain_ja.get(best_domain, best_domain)}に注力する',
            'desc': _domain_action_desc(best_domain, domains[best_domain], True),
            'icon': icon_data[0], 'icon_bg': icon_data[1], 'icon_color': icon_data[2],
        })
    else:
        actions.append({
            'title': f'{domain_ja.get(best_domain, best_domain)}を守る',
            'desc': _domain_action_desc(best_domain, domains[best_domain], False),
            'icon': icon_data[0], 'icon_bg': icon_data[1], 'icon_color': icon_data[2],
        })

    # Action 2: Strength-based action
    if sf_top5:
        top = sf_top5[0]
        top_ja = SF_JA.get(top['name'], '')
        if avg_stars >= 3:
            actions.append({
                'title': f'{top["name"]}（{top_ja}）を武器にする',
                'desc': _strength_action(top['name'], True),
                'icon': '&#9733;', 'icon_bg': 'rgba(99,102,241,0.15)', 'icon_color': '#a5b4fc',
            })
        else:
            actions.append({
                'title': f'{top["name"]}（{top_ja}）で自分を守る',
                'desc': _strength_action(top['name'], False),
                'icon': '&#9733;', 'icon_bg': 'rgba(99,102,241,0.15)', 'icon_color': '#a5b4fc',
            })

    # Action 3: Element/spiritual action
    hsp = p.get('personality', {}).get('hsp', {})
    if hsp.get('score') == 'high' or hsp.get('total', 0) >= 18:
        if avg_stars <= 2:
            actions.append({
                'title': '繊細さのケアを最優先に',
                'desc': 'エネルギーが低い月は、繊細な感覚が過敏になりがち。ネガティブな刺激を避け、自然の中で過ごす時間や、一人で内省する時間を意識的に確保する',
                'icon': '&#9826;', 'icon_bg': 'rgba(139,92,246,0.15)', 'icon_color': '#c4b5fd',
            })
        else:
            actions.append({
                'title': '繊細さを創造性に変換する',
                'desc': '好調期の繊細さは、美しいものや深い体験から何倍もの充足を引き出す。アート・音楽・深い会話を意識的に取り入れて、感性を栄養にする',
                'icon': '&#9826;', 'icon_bg': 'rgba(139,92,246,0.15)', 'icon_color': '#c4b5fd',
            })
    else:
        missing = p['four_pillars'].get('missing_elements', [])
        if missing:
            elem_actions = {
                '金': ('決断力を意識的に鍛える', '考えすぎる前に「小さく試す」を実践。完璧を待たず、70点で動き出す訓練を'),
                '水': ('柔軟性を意識する', '予定通りにいかない時こそ成長のチャンス。「別のルートもある」と自分に言い聞かせる'),
                '木': ('成長のエネルギーを補う', '新しい学びや挑戦を一つ始める。木のように上へ伸びる意識を持つ'),
                '火': ('情熱を燃やす場を作る', '心が躍ることに時間を使う。義務感だけの行動を減らし、ワクワクを優先する'),
                '土': ('安定の基盤を作る', 'ルーティンを一つ定着させる。毎日同じ時間に同じことをする習慣が土の力を補う'),
            }
            first_missing = str(missing[0])
            ea = elem_actions.get(first_missing, ('バランスを整える', '欠けている要素を意識的に生活に取り入れる'))
            actions.append({
                'title': ea[0],
                'desc': ea[1],
                'icon': '&#9670;', 'icon_bg': 'rgba(234,179,8,0.15)', 'icon_color': '#facc15',
            })

    return actions[:3]


def _domain_action_desc(domain, stars, is_offensive):
    """Generate domain-specific action description."""
    if domain == 'work':
        if is_offensive:
            return '仕事運が好調。新しいプロジェクトの提案や、後回しにしていた重要タスクに着手するベストタイミング'
        return '仕事は現状維持がベスト。新規案件は控え、既存の仕事を丁寧に仕上げることに集中する'
    if domain == 'money':
        if is_offensive:
            return '金運が高い月。投資判断や価格交渉に適している。ただし衝動買いには注意'
        return '金運は守り。大きな出費は避け、計画的な支出管理を。固定費の見直しに良いタイミング'
    if domain == 'health':
        if is_offensive:
            return '体調が安定。新しい運動習慣を始めたり、健康投資に踏み切るのに最適'
        return '体調を崩しやすい月。睡眠の質を最優先に。無理なスケジュールは組まない'
    # romance
    if is_offensive:
        return '人間関係が良好。新しい出会いにオープンに、既存の関係も深まるタイミング'
    return '対人関係で誤解が生じやすい。丁寧なコミュニケーションを心がけ、衝突は避ける'


def _strength_action(strength_name, is_offensive):
    """Generate strength-specific action for the month."""
    offensive_map = {
        'Empathy': '共感力を使って、チームメンバーや周囲の人が本当に求めていることを察知し、先回りで動く。サービス設計やフィードバック収集に最適',
        'Intellection': '深い思考に没頭できる時間をブロックする。重要なテーマについて、ノートに書きながら考えを整理する',
        'Deliberative': '重要な意思決定に取り組むベストタイミング。慎重さを武器に、リスクを見極めた上で前進する',
        'Connectedness': '異なるプロジェクトや人脈の「つながり」を意識する。一見無関係なものの間にシナジーを見出す',
        'Maximizer': '既にうまくいっていることを「さらに良く」する。弱みの修正より、強みの極大化に集中する',
    }
    defensive_map = {
        'Empathy': '他者の感情を吸収しすぎないよう、意識的に境界線を引く。「感じ取っても、背負わない」を練習する',
        'Intellection': '考えすぎて動けなくならないよう注意。思考は30分で区切り、小さなアクションに変換する',
        'Deliberative': '慎重さが行動の先延ばしにならないよう意識する。「完璧な答えより、今できる最善」で動く',
        'Connectedness': '全体を見すぎて疲れてしまわないよう、今週やることだけに焦点を絞る',
        'Maximizer': '「もっと良くできる」の追求を一旦止めて、現状の「十分良い」を認める練習をする',
    }
    if is_offensive:
        return offensive_map.get(strength_name, f'{strength_name}を最大限に活用して、新しい挑戦に取り組む')
    return defensive_map.get(strength_name, f'{strength_name}が裏目に出ないよう、バランスを意識する')


def _generate_monthly_watchouts(p, cur_month, avg_stars):
    """Generate watch-out items based on profile weaknesses + fortune."""
    items = []
    missing = p['four_pillars'].get('missing_elements', [])
    ennea = p.get('personality', {}).get('enneagram', {})
    rok_type = cur_month['rokusei']['type']
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])

    # Rokusei danger
    if rok_type in ('danger', 'caution'):
        satsukai = cur_month['rokusei'].get('satsukai')
        if satsukai:
            items.append(f'六星占術で{satsukai}に入っています。大きな契約・転職・引越しなど人生の重大決断は可能な限り避ける')
        else:
            items.append('六星占術で注意期。衝動的な判断は避け、一晩寝かせてから決める')

    # Missing elements warning
    if missing and avg_stars <= 3:
        missing_warnings = {
            '金': '「決断できない」状態に陥りやすい月。迷ったら信頼できる人に相談して背中を押してもらう',
            '水': '柔軟性が低下しやすい月。予定変更にイライラしたら深呼吸。「流れに身を任せる」ことも戦略',
            '土': '地に足がつかない感覚がある月。毎朝のルーティンを崩さないことが安定の鍵',
            '木': '成長が停滞する感覚がある月。小さな学びを一つ始めるだけでエネルギーが回復する',
            '火': 'モチベーションが上がりにくい月。「なぜやるのか」原点に立ち返ると情熱が再点火する',
        }
        for m in missing[:2]:
            warn = missing_warnings.get(str(m))
            if warn:
                items.append(warn)

    # Enneagram stress
    if avg_stars <= 2 and ennea:
        stress = ennea.get('stress_direction')
        stress_msgs = {
            1: '完璧主義に陥りすぎないよう注意。「まあいいか」を意識的に唱える',
            2: '自己犠牲モードに入りやすい。「自分のニーズも大切にしていい」と意識する',
            4: '感情の波に飲まれやすい時期。客観的な視点を保つ工夫を',
            5: '殻にこもりすぎないよう注意。信頼できる人との対話を意識的に入れる',
            7: '楽しいことに逃避しやすい。不快でも向き合うべきことから目をそらさない',
            8: '攻撃的になりやすい。反射的に言葉を返す前に3秒待つ',
        }
        msg = stress_msgs.get(stress)
        if msg:
            items.append(msg)

    return items[:3]


def _action_blueprint(p):
    """Generate actionable takeaways section connecting Core Identity to daily life."""
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    ennea = p.get('personality', {}).get('enneagram', {})
    missing = p['four_pillars'].get('missing_elements', [])
    dm = p['four_pillars']['day_master']
    hsp = p.get('personality', {}).get('hsp', {})
    adhd = p.get('personality', {}).get('adhd', {})
    west = p['western_astrology']['sun_sign']

    items = []

    # 1. Energy management based on Day Master + HSP + ADHD
    if hsp.get('score') == 'high' or hsp.get('total', 0) >= 18:
        items.append({
            'label': 'エネルギー管理',
            'title': '繊細さ × 過集中 — 「没頭」と「回復」のリズムを設計する',
            'desc': '繊細な感受性は最大の武器であると同時に、消耗の原因にもなる。90分集中→15分完全回復のサイクルを基本リズムに。ネガティブな環境からは物理的に距離を取る仕組みを作る',
        })
    else:
        items.append({
            'label': 'エネルギー管理',
            'title': f'{dm["char"]}火の炎を安定させる — 環境設計が鍵',
            'desc': f'{dm["char"]}火（ロウソクの炎）は環境次第で安定も不安定もする。集中できる環境を意識的に選び、エネルギーの無駄遣いを避ける仕組みを作る',
        })

    # 2. Weakness compensation
    if missing:
        elem_comp = {
            '金': ('決断力の補完', '「70点で動く」ルールを設定する。完璧な答えを待つのではなく、仮説→実行→修正のサイクルを高速で回す。タイマーで考える時間を制限するのも有効'),
            '水': ('柔軟性の補完', '計画通りにいかない状況を「学びのチャンス」と再定義する。月に一度、いつもと違う行動パターンを試す習慣を作る'),
            '木': ('成長力の補完', '月に一つ新しいスキルや知識を学ぶ習慣。小さくても継続的な成長が、欠けた木の力を補う'),
            '火': ('情熱の補完', '「なぜ自分がこれをやるのか」を定期的に言語化する。目的を明確にすることで内なる火を維持する'),
            '土': ('安定基盤の補完', 'ルーティンを少なくとも3つ持つ。毎日同じ時間に起き、同じ順序で朝の準備をするだけで土の力が補完される'),
        }
        first_missing = str(missing[0])
        comp = elem_comp.get(first_missing, ('バランスの補完', '欠けている要素を意識的に日常に取り入れる'))
        items.append({
            'label': '弱点の構造的カバー',
            'title': comp[0],
            'desc': comp[1],
        })

    # 3. Strength optimization
    if sf_top5:
        top = sf_top5[0]
        top_ja = SF_JA.get(top['name'], '')
        opt_map = {
            'Empathy': ('共感力の最適活用', '共感力は「他者を理解する」だけでなく「他者が何を求めているか先読みする」戦略的スキル。サービス設計・チームマネジメント・交渉において、相手の言葉にならないニーズを読む武器として使う。ただし境界線は必須 — 「感じ取っても、背負わない」を原則に'),
            'Intellection': ('思考力の最適活用', '一人で深く考える時間を「生産的な仕事」として確保する。周囲には「考える時間」の必要性を説明し、カレンダーにブロック。思考の成果はメモや図で言語化し、価値を可視化する'),
            'Deliberative': ('慎重さの最適活用', 'リスク分析力を「守り」だけでなく「攻めの意思決定」に使う。「慎重に分析した結果、今が動くべきタイミング」と判断できれば、それは最も確実な攻め'),
            'Connectedness': ('つながりの力の最適活用', '異なる分野・プロジェクト・人物の間に隠された接点を見つけ出す力を戦略的に使う。月に一度「一見無関係な2つのことを結びつける」思考実験を行う'),
            'Maximizer': ('最上志向の最適活用', '「良い→最高」の追求を、最もインパクトのある領域に集中する。全てを完璧にしようとせず、20%の努力で80%の成果が出る領域を見極める'),
        }
        opt = opt_map.get(top['name'], (f'{top["name"]}の最適活用', f'{top["name"]}（{top_ja}）を日常の意思決定と行動に組み込み、最大限に活用する'))
        items.append({
            'label': '最大の武器',
            'title': opt[0],
            'desc': opt[1],
        })

    if not items:
        return ''

    cards_html = ''
    for item in items:
        cards_html += f'''<div class="blueprint-card">
      <div class="blueprint-label">{item['label']}</div>
      <div class="blueprint-title">{item['title']}</div>
      <div class="blueprint-desc">{item['desc']}</div>
    </div>'''

    return f'''<div class="blueprint-section">
  <div class="blueprint-header">この特性を活かすには</div>
  <div class="blueprint-grid">{cards_html}</div>
</div>'''


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

    # Dynamic summary cards
    dm_desc = dm.get('description', '')
    # Core Essence
    yin_yang_ja = {'Yin':'陰','Yang':'陽'}.get(dm.get('yin_yang',''), '')
    elem_ja = {'Fire':'火','Wood':'木','Earth':'土','Metal':'金','Water':'水'}.get(dm.get('element',''), '')
    essence_value = f'{dm["char"]}{elem_ja} × {ys["name"]}'
    essence_sub = _get_essence_sub(dm, ys)

    # Strongest Axis
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    if sf_top5 and len(sf_top5) >= 2:
        t1_ja = SF_JA.get(sf_top5[0]['name'], sf_top5[0]['name'])
        t2_ja = SF_JA.get(sf_top5[1]['name'], sf_top5[1]['name'])
        axis_value = f'{t1_ja} × {t2_ja}'
        axis_sub = f'{sf_top5[0]["name"]}（{t1_ja}）+ {sf_top5[1]["name"]}（{t2_ja}）'
    else:
        axis_value = '—'
        axis_sub = ''

    # Duality
    bt = p['blood_type']
    ennea = p.get('personality', {}).get('enneagram', {})
    rok = p['rokusei']
    etype = ennea.get('type', '?')
    if rok.get('reigou'):
        dual_sub = f'{bt["type"]}型 × 霊合星人 × エニアグラム {etype}'
    else:
        dual_sub = f'{bt["type"]}型 × エニアグラム {etype}'
    dual_value = _get_duality_value(bt, ennea, rok)

    # Watch Out
    if missing:
        missing_str = "・".join(str(m) for m in missing)
        watch_value = f'{missing_str}の欠如'
        watch_sub = _get_missing_sub(missing)
    else:
        watch_value = '—'
        watch_sub = ''

    return f'''<section class="section" id="core-identity">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(99,102,241,0.15);color:#a5b4fc">&#9733;</div>
    <div><h2>Core Identity（自己本質）— あなたはこういう人</h2>
      <div class="pillar-sub">6つの分析体系が示す、時代を超えた人物像</div></div>
  </div>
  {insight_html}
  <div class="grid grid-4" style="margin-top:16px">
    <div class="card tc"><div class="card-label">Core Essence（本質）</div>
      <div class="card-value">{essence_value}</div>
      <div class="card-sub">{essence_sub}</div></div>
    <div class="card tc"><div class="card-label">Strongest Axis（最強の軸）</div>
      <div class="card-value">{axis_value}</div>
      <div class="card-sub">{axis_sub}</div></div>
    <div class="card tc"><div class="card-label">Duality（二面性）</div>
      <div class="card-value">{dual_value}</div>
      <div class="card-sub">{dual_sub}</div></div>
    <div class="card tc"><div class="card-label">Watch Out（注意点）</div>
      <div class="card-value" style="color:var(--yellow)">{watch_value}</div>
      <div class="card-sub">{watch_sub}</div></div>
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
            ja_name = sf_ja.get(s['name'], '') or SF_JA.get(s['name'], '')
            ja_span = f' <span style="font-size:12px;color:var(--text-secondary);font-weight:400">（{ja_name}）</span>' if ja_name else ''
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
            dname_ja = DOMAIN_JA.get(dname, '')
            dname_disp = f'{dname}（{dname_ja}）' if dname_ja else dname
            dom_bars += f'''<div class="domain-bar">
          <div class="domain-header"><span>{dname_disp}</span><span style="font-family:var(--font-mono)">{top10} / 10</span></div>
          <div class="domain-track"><div class="domain-fill" style="width:{top10*10}%;background:{dc}"></div></div></div>'''

        etype = ennea.get('type', '?')
        ename = ENNEA_NAMES.get(etype, '')
        hsp_label = HSP_LABELS.get(hsp.get('score', ''), hsp.get('score', ''))
        adhd_label = ADHD_LABELS.get(adhd.get('tendency', ''), adhd.get('tendency', ''))

        sf_html = f'''<div class="grid"><div class="card">
      <div class="card-title"><span class="icon">&#9733;</span> CliftonStrengths（強み診断）TOP 5</div>
      <ul class="top5-list">{items}</ul>
      <div style="font-size:11px;color:var(--text-muted);margin-top:12px">Lead Domain（主要領域）: {sf.get("lead_domain","")}{" (" + DOMAIN_JA.get(sf.get("lead_domain",""), "") + ")" if DOMAIN_JA.get(sf.get("lead_domain","")) else ""} | 受験日: {sf.get("date_taken","")}</div>
    </div>
    <div class="card">
      <div class="card-title"><span class="icon">&#9632;</span> ドメイン分布（TOP10内）</div>
      <div style="margin-top:8px">{dom_bars}</div>
      <div style="margin-top:24px">
        <div class="card-title" style="font-size:13px"><span class="icon">&#9830;</span> Typology（類型分析）</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px">
          <div class="typo-cell"><div class="typo-label">Enneagram（エニアグラム）</div>
            <div class="typo-value">Type {etype}</div><div class="typo-sub">{ename}</div>
            {"<div class='typo-desc'>"+pers_descs['enneagram']+"</div>" if pers_descs.get('enneagram') else ""}</div>
          <div class="typo-cell"><div class="typo-label">Blood Type（血液型）</div>
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
  <h2 class="section-title">Personality Profile（性格プロファイル）</h2>
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
    west_el_ja = {'Water':'水','Fire':'火','Earth':'地','Air':'風'}.get(west['element'], west['element'])
    west_q_ja = {'Fixed':'不動宮','Cardinal':'活動宮','Mutable':'柔軟宮'}.get(west['quality'], west['quality'])

    cards = f'''<div class="grid grid-3">
    <div class="card"><div class="card-label">太陽星座</div>
      <div class="card-value">{west["symbol"]} {west["sign"]}</div>
      <div class="card-sub">{west_el_ja}（{west["element"]}）/ {west_q_ja}（{west["quality"]}）</div>
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
    elem_ja = {'Wood':'木','Fire':'火','Earth':'土','Metal':'金','Water':'水'}
    pcards = ''
    for i, pl in enumerate(pillars):
        ec = elem_cls.get(pl['stem']['element'], '')
        pcards += f'''<div class="pillar"><div class="pillar-label">{pillar_labels[i]}</div>
      <div class="kanji">{pl["full"]}</div>
      <div class="reading">{pl["stem"]["reading"]}・{pl["branch"]["reading"]}</div>
      <div class="element-badge {ec}">{elem_ja.get(pl["stem"]["element"], pl["stem"]["element"])}（{pl["stem"]["element"]}）</div>
      <div style="font-size:10px;color:var(--text-muted);margin-top:6px">{pillar_roles[i]}</div></div>'''
    pcards += '<div class="pillar unknown"><div class="pillar-label">時柱</div><div class="kanji">？？</div><div class="reading">出生時刻不明</div><div class="element-badge" style="background:rgba(255,255,255,0.05);color:var(--text-muted)">未解放</div><div style="font-size:10px;color:var(--text-muted);margin-top:6px">晩年・子孫運</div></div>'

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
    el5_ja = {'Metal':'金','Fire':'火','Earth':'土','Water':'水','Wood':'木'}
    dir_ja = {'N':'北','S':'南','E':'東','W':'西','NE':'北東','NW':'北西','SE':'南東','SW':'南西','C':'中央'}
    nsk_cards = f'''<div class="grid grid-3">
    <div class="card"><div class="card-label">本命星（年星）— あなたの根幹</div>
      <div class="card-value">{ys["name"]}</div><div class="card-sub">{el5_ja.get(ys["element"],ys["element"])}（{ys["element"]}）/ {dir_ja.get(ys["direction"],ys["direction"])}（{ys["direction"]}）</div></div>
    <div class="card"><div class="card-label">月命星 — 内面の性格</div>
      <div class="card-value">{ms["name"]}</div><div class="card-sub">{el5_ja.get(ms["element"],ms["element"])}（{ms["element"]}）/ {dir_ja.get(ms["direction"],ms["direction"])}（{ms["direction"]}）</div></div>'''
    if cur9:
        nsk_cards += f'''<div class="card"><div class="card-label">2026年 宮位置 — 今年の運気</div>
      <div class="card-value">{cur9["palace"]}</div><div class="card-sub">{cur9["theme"]}（運気 {cur9["energy"]}/100）</div></div>'''
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
      <div class="card-sub">{phase_label}（運気 {cur12["energy"]}/100）</div></div>'''
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
    table = f'<table class="cycle-table"><thead><tr><th>年</th><th>メイン</th>{sub_th}<th>殺界</th><th>運気</th></tr></thead><tbody>{rows}</tbody></table>'

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
    <strong style="color:var(--text)">日主（にっしゅ）: {dm["char"]}火（{dm["yin_yang"]}火 / ひのと）</strong> — あなたの生まれ持った本質。{dm_detail}</div>
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
      <div class="card-value">{cur12["phase"]}</div><div class="card-sub">運気 {cur12["energy"]}/100</div></div>'''
    if cur_sub:
        sub_label = satsukai_html(cur_sub.get('殺界')) if cur_sub.get('殺界') else f'運気 {cur_sub["energy"]}/100'
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

    # Year theme one-liner
    year_theme = _year_theme(cur_comb, cur9, cur12, has_reigou, p)

    return f'''<section class="section" id="forecast-2026">
  <div class="pillar-header">
    <div class="pillar-icon" style="background:rgba(234,179,8,0.15);color:#facc15">&#9733;</div>
    <div><h2>2026年 運勢フォーキャスト</h2>
      <div class="pillar-sub">九星気学 × 六星占術が示す年間の流れ</div></div>
  </div>
  {year_theme}
  {cards}
  <div class="chart-wrap"><canvas id="chartOverlay" height="280"></canvas></div>
  {legend_html}
  {insight}
</section>'''


def _year_theme(cur_comb, cur9, cur12, has_reigou, p):
    """Generate a one-line year theme banner."""
    dm = p['four_pillars']['day_master']
    west = p['western_astrology']
    forecast_west = west.get('forecast_2026', '')

    if cur_comb and has_reigou:
        score = cur_comb['score']
        if score >= 70:
            theme = '攻めの年 — 種を蒔き、未来の収穫を設計する'
            color = '#4ade80'
        elif score >= 50:
            theme = '布石の年 — 足場を固め、次の飛躍を準備する'
            color = '#60a5fa'
        elif score >= 30:
            theme = '守りの年 — 基盤を強化し、内面を充実させる'
            color = '#facc15'
        else:
            theme = '充電の年 — 回復に専念し、嵐が過ぎるのを待つ'
            color = '#f87171'
    elif cur9:
        if cur9['energy'] >= 70:
            theme = '攻めの年 — 積極的にチャンスを掴みにいく'
            color = '#4ade80'
        elif cur9['energy'] >= 40:
            theme = '布石の年 — 準備と基盤づくりに集中する'
            color = '#60a5fa'
        else:
            theme = '耐える年 — 守りを固め、次の好機を待つ'
            color = '#facc15'
    else:
        theme = '変化の年 — 新しい流れを受け入れる'
        color = '#a5b4fc'

    return f'''<div class="year-theme-banner">
    <div class="year-theme-label">2026年のテーマ</div>
    <div class="year-theme-text" style="color:{color}">{theme}</div>
  </div>'''


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


def _monthly_advice(p, month_data):
    """Generate personalized advice text for a specific month."""
    domains = month_data['domains']
    avg = sum(domains.values()) / len(domains)
    rok_type = month_data['rokusei']['type']
    rok_phase = month_data['rokusei']['phase']
    nine_note = month_data['nine_star']['note']
    month_num = month_data['month']
    sf_top5 = p.get('strengths_finder', {}).get('top5', [])
    missing = p['four_pillars'].get('missing_elements', [])

    parts = []

    if avg >= 4:
        parts.append(f'全体的にエネルギーが高い月。')
        best = max(domains, key=domains.get)
        domain_ja = {'work': '仕事', 'money': '金運', 'health': '健康', 'romance': '人間関係'}
        parts.append(f'特に{domain_ja.get(best, best)}が好調なので、ここに集中投資するのが吉。')
        if sf_top5:
            top_ja = SF_JA.get(sf_top5[0]['name'], '')
            parts.append(f'{sf_top5[0]["name"]}（{top_ja}）を積極的に使って攻めてください。')
    elif avg >= 3:
        parts.append(f'安定した月。大きな波はないが、地道な努力が蓄積される時期。')
        parts.append(f'今月の積み重ねが、次の好調期の成果につながります。')
    elif avg >= 2:
        parts.append(f'エネルギーが低下しやすい月。')
        if rok_type in ('danger', 'caution'):
            parts.append(f'六星占術で「{rok_phase}」のため、大きな決断は控えるのが賢明。')
        if missing:
            parts.append(f'欠如要素の影響が出やすいので、意識的にケアを。')
    else:
        parts.append(f'充電を最優先にする月。無理は禁物。')
        parts.append(f'この時期の休息が、後の回復力を左右します。')

    return ''.join(parts) if parts else ''


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

    # Month panels with domain messages + personalized advice
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
        'advice': _monthly_advice(p, m),
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
    ${{m.advice ? '<div class="month-advice">' + m.advice + '</div>' : ''}}
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
            'title': f'Empathy（共感性）× 繊細さ × エニアグラム{etype}',
            'text': f'CliftonStrengths 1位の共感性と{sens_label}な感受性、'
                    f'エニアグラムType {etype}の独自性追求が共鳴。'
                    f'「人の感情を深く理解し、独自の視点で表現する力」を形成する。'
                    f'この組み合わせはサービス設計においてユーザーの痛みを自分事として感じられるPMFの源泉。',
        })

    # 2. Intellection × Focus Pattern × Day Master
    if len(sf_top5) >= 2 and adhd:
        focus_label = ADHD_LABELS.get(adhd.get('tendency', ''), '')
        boxes.append({
            'title': f'Intellection（内省）× 集中パターン × {dm["char"]}火（陰火）',
            'text': f'深い思考力（Intellection 2位）× {focus_label}の集中特性 × '
                    f'{dm["char"]}火（ロウソクの炎）。'
                    f'環境を整えれば安定して燃え続けるが、刺激に弱い。'
                    f'自動化で雑務を排除し、思考に没頭できる環境を作ることが最重要。',
        })

    # 3. Deliberative × Blood Type × Western
    q_ja = {'Fixed':'不動宮','Cardinal':'活動宮','Mutable':'柔軟宮'}.get(west['quality'], west['quality'])
    if len(sf_top5) >= 3:
        boxes.append({
            'title': f'Deliberative（慎重さ）× {bt["type"]}型 × {west["sign"]}（{q_ja}）',
            'text': f'慎重さ（3位）× {bt["type"]}型の合理的分析 × '
                    f'{west["sign"]}の{q_ja}。'
                    f'三重の慎重さは深い分析に基づく確実な意思決定を可能にする。'
                    f'一方で「分析麻痺」に陥りやすく、行動が遅れるリスクもある。',
        })

    # 4. Connectedness × Nine Star × Current Year
    cur9 = next((c for c in p['nine_star_ki'].get('nine_year_cycle', []) if c.get('current')), None)
    if len(sf_top5) >= 4 and cur9:
        boxes.append({
            'title': f'Connectedness（運命思考）× {ys["name"]} × {cur9["palace"]}2026',
            'text': f'全てを繋げて見る直感力（4位）× {ys["name"]}の社交力と言葉の力。'
                    f'2026年の{cur9["palace"]}は「{cur9["theme"]}」の年 — '
                    f'点在するプロジェクト群を繋ぎ、エコシステムを設計するのに最適なタイミング。',
        })

    # 5. Maximizer × Systems
    if len(sf_top5) >= 5:
        boxes.append({
            'title': 'Maximizer（最上志向）× 3S原則 × 7つの習慣',
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
  <h2 class="section-title">Cross Analysis（クロス分析）— 強み×運気の掛け合わせ</h2>
  <div class="grid">{grid_items}</div>
</section>'''


def _footer(tier):
    gen_date = _date.today().isoformat()
    systems = '四柱推命 × 九星気学 × 六星占術 × 西洋占星術'
    if tier >= 2:
        systems += ' × CliftonStrengths（強み診断）× Enneagram（エニアグラム）'
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
.hero-tagline{font-size:clamp(15px,2vw,18px);font-weight:600;color:#e0e7ff;margin-bottom:24px;line-height:1.6}
.hero-traits{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:24px}
.hero-trait{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:var(--r-md);padding:14px 16px;transition:transform .2s}
.hero-trait:hover{transform:translateY(-2px)}
.hero-trait-keyword{font-size:14px;font-weight:600;color:#e0e7ff;margin-bottom:4px}
.hero-trait-detail{font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:6px}
.hero-trait-source{font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px}
.stat-sub{font-size:12px;color:var(--text-secondary);margin-top:2px;font-family:var(--font-mono)}
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
.guidance-summary{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:24px;margin-bottom:8px}
.guidance-overview{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.guidance-energy-badge{display:inline-block;font-size:14px;font-weight:700;padding:6px 16px;border-radius:20px}
.guidance-tags{display:flex;gap:6px;flex-wrap:wrap}
.guidance-narrative{font-size:14px;color:var(--text);line-height:1.8;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.guidance-actions-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.guidance-actions-section{display:flex;flex-direction:column;gap:12px}
.guidance-section-label{font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
.guidance-action{display:flex;gap:12px;align-items:flex-start}
.guidance-action-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.guidance-action-title{font-size:13px;font-weight:600;color:var(--text);margin-bottom:2px}
.guidance-action-desc{font-size:12px;color:var(--text-secondary);line-height:1.6}
.guidance-watch{display:flex;flex-direction:column;gap:8px}
.guidance-watch-title{font-size:11px;font-weight:600;color:var(--yellow);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
.guidance-watch-item{font-size:12px;color:var(--text-secondary);line-height:1.6;padding-left:12px;border-left:2px solid rgba(234,179,8,0.3)}
.year-theme-banner{background:linear-gradient(135deg,rgba(234,179,8,0.06),rgba(139,92,246,0.04));border:1px solid rgba(234,179,8,0.15);border-radius:var(--r-md);padding:20px 24px;margin-bottom:20px;text-align:center}
.year-theme-label{font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.year-theme-text{font-size:clamp(16px,2.5vw,22px);font-weight:700;line-height:1.4}
.blueprint-section{margin-top:24px;margin-bottom:8px}
.blueprint-header{font-size:14px;font-weight:600;color:var(--text-secondary);margin-bottom:12px;padding-left:12px;border-left:3px solid var(--accent2)}
.blueprint-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.blueprint-card{background:linear-gradient(135deg,rgba(139,92,246,0.06),rgba(99,102,241,0.04));border:1px solid rgba(139,92,246,0.15);border-radius:var(--r-md);padding:16px 20px}
.blueprint-label{font-size:10px;font-weight:600;color:var(--accent2);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px}
.blueprint-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:8px;line-height:1.4}
.blueprint-desc{font-size:12px;color:var(--text-secondary);line-height:1.7}
.month-advice{font-size:13px;color:var(--text-secondary);line-height:1.7;padding:12px 16px;background:linear-gradient(135deg,rgba(99,102,241,0.06),rgba(139,92,246,0.04));border:1px solid rgba(99,102,241,0.12);border-radius:var(--r-sm);margin-bottom:16px}
@media(max-width:768px){.grid{grid-template-columns:1fr}.pillar-grid{grid-template-columns:repeat(2,1fr)}.domain-grid{grid-template-columns:1fr}.guidance-actions-grid{grid-template-columns:1fr}.blueprint-grid{grid-template-columns:1fr}}
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
  .hero-traits{grid-template-columns:repeat(2,1fr);gap:8px}
  .hero-trait{padding:10px 12px}
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
{_this_month_guidance(p)}
{_core_identity(p)}
{_action_blueprint(p)}
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
