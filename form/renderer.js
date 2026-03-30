/**
 * Self-Insight Dashboard Renderer v2.0
 * Production-quality renderer matching generate_dashboard.py output.
 * "30秒で鳥肌" — birth date alone delivers a premium experience.
 */

// ============================================================
// Constants & Dictionaries
// ============================================================

const ELEMENT_EMOJI = {'木':'🌳','火':'🔥','土':'⛰️','金':'⚔️','水':'💧'};
const ELEMENT_MEANING = {'木':'成長力・発展','火':'情熱・行動力','土':'安定・信頼','金':'決断力・収穫','水':'知恵・柔軟性'};
const DOMAIN_LABELS = { work:'仕事', money:'お金', health:'健康', romance:'恋愛' };
const DOMAIN_COLORS = { work:'#6366f1', money:'#eab308', health:'#34d399', romance:'#f472b6' };
const MONTH_NAMES = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];

const PALACE_DESC = {
  '震宮': '行動力が高まり、新しいスタートを切りやすい時期',
  '巽宮': '人脈と信用が拡大する時期。情報が集まりやすい',
  '中宮': '年間で最もエネルギーが集中する中心位置。影響力が最大化',
  '乾宮': '目上の人や権威者からの後押しが得やすい時期',
  '兌宮': '悦びと収穫の時期。社交的なイベントが好結果を生む',
  '艮宮': '変化のタイミング。過去の蓄積を見直し、方向転換に適した時期',
  '離宮': '注目を集めやすい時期。自己表現と発信が効果的',
  '坎宮': '内省と忍耐の時期。表面的には停滞感があるが、内面の成長が進む',
  '坤宮': '受容と準備の時期。土台をしっかり固め、次の飛躍に備える',
};

const PHASE_DESC = {
  '安定': '最も安定した運気。大きな決断や長期計画に最適',
  '財成': '財運が充実する時期。投資や資産形成に追い風',
  '達成': '努力が成果として実を結ぶ時期。目標達成に全力を',
  '立花': '才能や魅力が開花する時期。クリエイティブな活動に最適',
  '再会': '過去のつながりが復活する時期。旧友や以前の経験が価値を持つ',
  '種子': '新しい種をまく時期。将来の芽を育てるスタート地点',
  '緑生': '芽が伸び始める成長期。学びと実験に適した時期',
  '陰影': '大殺界の入口。慎重に行動し、新規の大きな契約は避ける',
  '停止': '大殺界の中心。じっと耐え、現状維持を最優先に',
  '減退': '大殺界の出口。少しずつ回復するが、まだ油断は禁物',
  '健弱': '小殺界。体調や気力にムラが出やすい。無理は禁物',
  '乱気': '中殺界。判断力が鈍りやすい。衝動的な決断を避ける',
};

const SECTION_QUOTES = {
  core: 'あなたを一言で表すなら—',
  divination: '2,000年の叡智が、あなたの星を読み解く',
  forecast: '未来は決まっていない。しかし、流れは見える',
  monthly: '毎月、あなたの運気は新しい色に染まる',
  personality: '才能は、使い方を知ったとき初めて力になる',
};

const EL_JP = {'Wood':'木','Fire':'火','Earth':'土','Metal':'金','Water':'水'};
const EL_NAMES = {'Wood':'樹','Fire':'炎','Earth':'大地','Metal':'剣','Water':'海'};
const YY_JP = {'Yang':'陽','Yin':'陰'};

const DM_NARRATIVE = {
  'Wood_Yang': 'まっすぐに伸びる大樹のように、あなたは困難に屈せず成長し続ける力を持っています。正義感が強く、リーダーシップを発揮する場面で輝きます',
  'Wood_Yin': '草花のようにしなやかで、環境に適応しながら着実に根を張る力があります。繊細な感性と粘り強さを兼ね備えた人物です',
  'Fire_Yang': '太陽のように周囲を明るく照らし、人々にエネルギーを与える存在です。行動力と情熱で道を切り拓きますが、燃え尽きにも注意が必要です',
  'Fire_Yin': 'ロウソクの炎のように、静かで温かい光で人を照らします。直感力に優れ、繊細な洞察で本質を見抜く力があります',
  'Earth_Yang': '山のような安定感と包容力を持ち、周囲から信頼される存在です。大きな決断を任されることが多く、責任を全うする力があります',
  'Earth_Yin': '田畑のように、人や物事を育て受け入れる力があります。穏やかな性格の中に、着実に結果を出す底力を秘めています',
  'Metal_Yang': '鋼のような決断力と実行力を持ちます。目標に向かって迷いなく進む姿は、周囲に強い印象を与えます',
  'Metal_Yin': '宝石のように洗練された美しさと鋭い感性を持っています。細部にこだわり、品質を追求する姿勢が独自の価値を生みます',
  'Water_Yang': '大海のような広大な知恵と包容力を持ちます。多角的な視点で物事を捉え、柔軟な発想で解決策を見出します',
  'Water_Yin': '雨露のように繊細で浸透する力を持っています。静かに人の心に入り込み、深いレベルで影響を与える存在です',
};

const WESTERN_NARRATIVE = {
  'Fire': '情熱的で行動力に溢れ、直感を信じて前に進む力があります',
  'Earth': '現実的で安定志向。着実に成果を積み上げる信頼の人です',
  'Air': '知的好奇心が旺盛で、コミュニケーションを通じて世界を広げます',
  'Water': '感受性が豊かで、人の感情を深く理解する共感の達人です',
};

const NINE_STAR_NARRATIVE = {
  1: '水の静けさを持つあなたは、内面に深い知恵を蓄えています。周囲が騒がしい時も、冷静に本質を見抜く力があります',
  2: '大地の包容力を持ち、周囲を支える縁の下の力持ち。献身的な姿勢が信頼を集めます',
  3: '雷のような行動力と発想力。新しいことを始めるエネルギーに満ちた開拓者です',
  4: '風のように柔軟で、人との調和を重んじます。情報感度が高く、時代の流れを読む力があります',
  5: '中心に立つ帝王星。強いカリスマ性と統率力で、周囲を巻き込む力を持っています',
  6: '天の恵みを受けた金星。勤勉で品格があり、目上からの引き立てに恵まれます',
  7: '悦びの星。社交性と楽観性で人を惹きつけ、場を明るくする存在です',
  8: '山のような不動の意志。変化の時代に安定感をもたらす存在として頼られます',
  9: '太陽のように輝く火の星。知性と美意識に優れ、人々の注目を集めます',
};

// ============================================================
// Utility Functions
// ============================================================

function starRating(n) { return '★'.repeat(n) + '☆'.repeat(5 - n); }

function generateArchetype(dm, nsStar) {
  const prefix = dm.yin_yang === 'Yin' ? '静かな' : '燃える';
  const core = EL_NAMES[dm.element] || dm.element;
  const suffixes = {1:'の哲人',2:'の守護者',3:'の開拓者',4:'の導き手',5:'の帝王',6:'の賢者',7:'の詩人',8:'の求道者',9:'の先駆者'};
  return `${prefix}${core}${suffixes[nsStar] || 'の探求者'}`;
}

function generateIntegratedInsight(p) {
  const dm = p.four_pillars.day_master;
  const ns = p.nine_star_ki;
  const wa = p.western_astrology;
  const bt = p.blood_type;
  const rk = p.rokusei;

  const dmKey = `${dm.element}_${dm.yin_yang}`;
  const dmNarr = DM_NARRATIVE[dmKey] || '';
  const nsNarr = NINE_STAR_NARRATIVE[ns.year_star.number] || '';
  const waNarr = WESTERN_NARRATIVE[wa.sun_sign.element] || '';

  const missing = p.four_pillars.missing_elements || [];
  let balanceNote = '';
  if (missing.length > 0) {
    balanceNote = `五行の中で${missing.map(e => `${e}（${ELEMENT_MEANING[e]}）`).join('と')}が欠如しています。意識的にこれらの要素を補う行動が、あなたの成長を加速させます。`;
  } else {
    balanceNote = '五行がバランスよく備わっており、総合力の高さが強みです。どの領域でも一定の成果を出せる安定感があります。';
  }

  let reigouNote = '';
  if (rk.reigou) {
    reigouNote = `さらに、全人口のわずか約10%しかいない「霊合星人」として、${rk.main_star.name}と${rk.sub_star?.name || ''}の二つの星の性質を併せ持ちます。矛盾する二面性こそが、あなたの奥深さの源泉です。`;
  }

  return `<p>${dmNarr}</p>
<p>${nsNarr}。${waNarr}。${bt.type}型特有の${bt.strengths?.[0] || '個性'}も、あなたの行動に現れています。</p>
<p>${balanceNote}</p>
${reigouNote ? `<p>${reigouNote}</p>` : ''}`;
}

function monthlyNarrative(m) {
  const palace = m.nine_star.palace;
  const phase = m.rokusei.phase;
  const pd = PALACE_DESC[palace] || '';
  const phd = PHASE_DESC[phase] || '';
  const parts = [];
  if (pd) parts.push(`九星気学では${palace}に位置し、${pd}。`);
  if (phd) parts.push(`六星占術では「${phase}」の月。${phd}。`);
  if (m.rokusei.satsukai) parts.push(`⚠️ ${m.rokusei.satsukai}期間中。大きな決断は慎重に。`);
  return parts.join('');
}

// ============================================================
// Card Builder
// ============================================================

function card(id, title, quote, content, defaultOpen = false) {
  return `
  <section class="si-card-wrap si-fade" id="card-${id}">
    <button class="si-card-header" onclick="siToggle('${id}')" aria-expanded="${defaultOpen}">
      <div>
        <h2>${title}</h2>
        ${quote ? `<div class="si-quote">"${quote}"</div>` : ''}
      </div>
      <span class="si-chevron ${defaultOpen ? 'open' : ''}"></span>
    </button>
    <div class="si-card-body ${defaultOpen ? 'open' : ''}" id="body-${id}">
      ${content}
    </div>
  </section>`;
}

function badge(text, type = 'accent') {
  return `<span class="si-badge ${type}">${text}</span>`;
}

// ============================================================
// Main Render
// ============================================================

function renderDashboard(profile, container) {
  const p = profile;
  const fp = p.four_pillars;
  const ns = p.nine_star_ki;
  const rk = p.rokusei;
  const wa = p.western_astrology;
  const bt = p.blood_type;
  const pers = p.personality || {};
  const monthly = p.monthly_fortune;
  const currentMonth = new Date().getMonth() + 1;
  const year = new Date().getFullYear();

  const archetype = generateArchetype(fp.day_master, ns.year_star.number);
  const dmEl = fp.day_master.element;

  // Rarity badges
  const rarities = [];
  if (rk.reigou) rarities.push(badge('霊合星人 — 全人口の約10%', 'rare'));
  const missingEls = fp.missing_elements || [];
  if (missingEls.length >= 2) rarities.push(badge(`${missingEls.join('・')}欠落 — 希少な五行構成`, 'rare'));

  // Current year rokusei
  const currentPhase = rk.twelve_year_cycle?.find(e => e.current);
  const currentNsPalace = ns.year_cycle?.position;

  // === Build sections ===

  // 1. Core Identity (統合インサイト)
  const coreContent = `
    <div class="si-inner">
      ${generateIntegratedInsight(p)}
    </div>
    ${rarities.length ? `<div class="si-rarities">${rarities.join('')}</div>` : ''}
    <div class="si-summary-grid">
      <div class="si-sum-card">
        <div class="si-sum-label">日主</div>
        <div class="si-sum-val">${fp.day_master.char}</div>
        <div class="si-sum-sub">${EL_JP[dmEl]}の${YY_JP[fp.day_master.yin_yang]}</div>
      </div>
      <div class="si-sum-card">
        <div class="si-sum-label">本命星</div>
        <div class="si-sum-val">${ns.year_star.name.replace(/星$/, '')}</div>
        <div class="si-sum-sub">${ns.year_star.element}</div>
      </div>
      <div class="si-sum-card">
        <div class="si-sum-label">運命星</div>
        <div class="si-sum-val">${rk.main_star.name}</div>
        <div class="si-sum-sub">${rk.main_star.polarity}${rk.reigou ? ' 霊合' : ''}</div>
      </div>
      <div class="si-sum-card">
        <div class="si-sum-label">星座</div>
        <div class="si-sum-val">${wa.sun_sign.symbol}</div>
        <div class="si-sum-sub">${wa.sun_sign.jp}</div>
      </div>
    </div>`;

  // 2. Four Pillars
  const fpContent = `
    <div class="si-inner">
      <p>${fp.day_master.description}</p>
    </div>
    <div class="si-pillars">
      ${[['年柱', fp.year_pillar], ['月柱', fp.month_pillar], ['日柱', fp.day_pillar]].map(([label, pillar]) =>
        `<div class="si-pillar-card">
          <div class="pillar-label">${label}</div>
          <div class="pillar-chars">${pillar.full}</div>
          <div class="pillar-reading">${pillar.stem.reading}${pillar.branch.reading}</div>
          <div class="pillar-element">${EL_JP[pillar.stem.element]}/${EL_JP[pillar.branch.element]}</div>
        </div>`
      ).join('')}
    </div>
    <div class="si-inner" style="margin-top:16px">
      <h3>五行バランス</h3>
      <div class="si-elements">
        ${['木','火','土','金','水'].map(el => {
          const b = fp.five_elements_balance[el];
          return `<div class="si-element ${b.count === 0 ? 'missing' : ''}">
            <span class="emoji">${ELEMENT_EMOJI[el]}</span>
            <span class="label">${el}</span>
            <span class="pct">${b.pct}%</span>
          </div>`;
        }).join('')}
      </div>
      <p class="si-note">${fp.element_insight}</p>
    </div>`;

  // 3. Nine Star Ki + Rokusei + Western (占術プロファイル)
  const divContent = `
    <div class="si-accordion">
      <div class="si-acc-item open">
        <button class="si-acc-btn" onclick="siAccToggle(this)">九星気学</button>
        <div class="si-acc-body">
          <p><strong>本命星:</strong> ${ns.year_star.name}（${ns.year_star.element}）</p>
          <p><strong>月命星:</strong> ${ns.month_star.name}（${ns.month_star.element}）</p>
          ${currentNsPalace ? `<p><strong>${year}年:</strong> ${currentNsPalace.palace} — ${currentNsPalace.meaning}</p>` : ''}
          <p class="si-note">${NINE_STAR_NARRATIVE[ns.year_star.number] || ''}</p>
        </div>
      </div>
      <div class="si-acc-item">
        <button class="si-acc-btn" onclick="siAccToggle(this)">六星占術</button>
        <div class="si-acc-body">
          <p><strong>運命星:</strong> ${rk.main_star.name}${rk.main_star.polarity}${rk.reigou ? ` ${badge('霊合星人', 'rare')}` : ''}</p>
          ${rk.sub_star ? `<p><strong>副星:</strong> ${rk.sub_star.name}${rk.sub_star.polarity}</p>` : ''}
          ${currentPhase ? `<p><strong>${year}年:</strong> ${currentPhase.phase}${currentPhase['殺界'] ? ` ${badge(currentPhase['殺界'], 'danger')}` : ''}</p>
          <p class="si-note">${PHASE_DESC[currentPhase.phase] || ''}</p>` : ''}
        </div>
      </div>
      <div class="si-acc-item">
        <button class="si-acc-btn" onclick="siAccToggle(this)">西洋占星術</button>
        <div class="si-acc-body">
          <p><strong>太陽星座:</strong> ${wa.sun_sign.jp}（${wa.sun_sign.sign}）${wa.sun_sign.symbol}</p>
          <p><strong>エレメント:</strong> ${wa.sun_sign.element} · ${wa.sun_sign.quality}</p>
          <p><strong>守護星:</strong> ${wa.ruling_planet}</p>
          <p class="si-note">${WESTERN_NARRATIVE[wa.sun_sign.element] || ''}</p>
        </div>
      </div>
      <div class="si-acc-item">
        <button class="si-acc-btn" onclick="siAccToggle(this)">血液型</button>
        <div class="si-acc-body">
          <p><strong>${bt.type}型</strong>（日本人の${bt.pct || '?'}%）</p>
          ${bt.strengths ? `<p>✦ ${bt.strengths.join(' · ')}</p>` : ''}
          ${bt.challenges ? `<p>△ ${bt.challenges.join(' · ')}</p>` : ''}
        </div>
      </div>
    </div>`;

  // 4. Year Forecast
  const forecastContent = `
    ${currentPhase ? `
    <div class="si-inner">
      <p>${year}年のあなたは、九星気学では<strong>${currentNsPalace?.palace || ''}</strong>、六星占術では<strong>「${currentPhase.phase}」</strong>の年です。</p>
      <p>${PALACE_DESC[currentNsPalace?.palace] || ''}。${PHASE_DESC[currentPhase.phase] || ''}。</p>
      ${currentPhase['殺界'] ? `<p class="si-warn">⚠️ ${currentPhase['殺界']}期間中です。大きなリスクを伴う決断は慎重に。現状維持と内面の充実に注力する時期です。</p>` : ''}
    </div>` : ''}
    ${ns.nine_year_cycle ? `
    <div class="si-inner">
      <h3>運気サイクル</h3>
      <div class="si-cycle-bar">
        ${ns.nine_year_cycle.map(y => {
          const h = Math.round(y.energy / 100 * 60);
          const color = y.energy >= 70 ? '#34d399' : y.energy >= 40 ? '#eab308' : '#f87171';
          return `<div class="si-cycle-item ${y.current ? 'current' : ''}">
            <div class="bar" style="height:${h}px;background:${color}"></div>
            <span class="yr">${String(y.year).slice(2)}</span>
          </div>`;
        }).join('')}
      </div>
    </div>` : ''}`;

  // 5. Monthly Fortune
  const monthlyContent = `
    <div class="si-month-tabs">
      ${MONTH_NAMES.map((name, i) =>
        `<button class="si-month-tab ${i + 1 === currentMonth ? 'active' : ''}" data-month="${i+1}">${name}</button>`
      ).join('')}
    </div>
    <div class="si-month-panels">
      ${monthly.map(m => `
        <div class="si-month-panel ${m.month === currentMonth ? 'active' : ''}" data-month="${m.month}">
          <div class="si-month-header">
            <span>${m.month}月</span>
            <span class="si-phase-tag ${m.rokusei.type || ''}">${m.rokusei.phase}${m.rokusei.satsukai ? ` · ${m.rokusei.satsukai}` : ''}</span>
          </div>
          <div class="si-month-narrative">${monthlyNarrative(m)}</div>
          <div class="si-domains">
            ${Object.entries(DOMAIN_LABELS).map(([key, label]) =>
              `<div class="si-domain">
                <span class="domain-label" style="color:${DOMAIN_COLORS[key]}">${label}</span>
                <span class="domain-stars">${starRating(m.domains[key])}</span>
              </div>`
            ).join('')}
          </div>
        </div>
      `).join('')}
    </div>`;

  // 6. Personality (Tier 2+)
  let personalityContent = '';
  if (pers.enneagram || pers.hsp || pers.adhd || pers.big_five) {
    const parts = [];
    if (pers.enneagram) {
      parts.push(`<div class="si-inner">
        <h3>エニアグラム</h3>
        <p><strong>タイプ ${pers.enneagram.type}: ${pers.enneagram.name}</strong></p>
        <p>${pers.enneagram.description}</p>
        ${pers.enneagram.wing ? `<p>ウイング: ${pers.enneagram.wing}</p>` : ''}
        <p>成長方向: → タイプ${pers.enneagram.growth_direction} / ストレス方向: → タイプ${pers.enneagram.stress_direction}</p>
      </div>`);
    }
    if (pers.hsp) {
      parts.push(`<div class="si-inner">
        <h3>感受性プロファイル</h3>
        <p><strong>${pers.hsp.score === 'high' ? '高感受性' : pers.hsp.score === 'medium' ? '中程度' : '低感受性'}</strong>（${pers.hsp.total}/30）</p>
        <div class="si-bar-group">
          ${[['感覚', pers.hsp.subscales.sensory, 10],['感情', pers.hsp.subscales.emotional, 10],['社会', pers.hsp.subscales.social, 10]].map(([l, v, mx]) =>
            `<div class="si-bar-item"><span>${l}</span><div class="si-bar"><div style="width:${v/mx*100}%"></div></div><span>${v}/${mx}</span></div>`
          ).join('')}
        </div>
      </div>`);
    }
    if (pers.adhd) {
      parts.push(`<div class="si-inner">
        <h3>注意特性</h3>
        <p><strong>${pers.adhd.tendency === 'significant' ? '顕著な傾向' : pers.adhd.tendency === 'leaning' ? '傾向あり' : '低い傾向'}</strong></p>
        <p>閾値超過: ${pers.adhd.above_threshold_count}/${pers.adhd.total_items}項目</p>
      </div>`);
    }
    if (pers.big_five) {
      parts.push(`<div class="si-inner">
        <h3>Big Five性格特性${pers.mbti ? ` → ${pers.mbti}` : ''}</h3>
        <div class="si-bar-group">
          ${Object.entries({Extraversion:'外向性',Agreeableness:'協調性',Conscientiousness:'誠実性',Neuroticism:'神経症傾向',Openness:'開放性'}).map(([k,l]) =>
            `<div class="si-bar-item"><span>${l}</span><div class="si-bar"><div style="width:${(pers.big_five[k]||0)/20*100}%"></div></div><span>${pers.big_five[k]||0}/20</span></div>`
          ).join('')}
        </div>
      </div>`);
    }
    personalityContent = parts.join('');
  }

  // === Assemble ===
  container.innerHTML = `
<div class="si-dashboard">
  ${SI_STYLES}

  <!-- Hero -->
  <section class="si-hero">
    <div class="si-particles" aria-hidden="true"></div>
    <div class="si-archetype-glow">${archetype}</div>
    <h1>${p.identity.name}</h1>
    <div class="si-tagline">
      ${wa.sun_sign.jp} ${wa.sun_sign.symbol} · ${ns.year_star.name} · ${rk.main_star.name}${rk.main_star.polarity}${rk.reigou ? ' 霊合' : ''} · ${bt.type}型
    </div>
    <div class="si-hero-sub">あなたの取扱説明書</div>
  </section>

  <!-- Hub Cards -->
  <div class="si-hub">
    <button class="si-hub-card" onclick="siOpen('core')">✦ あなたの本質</button>
    <button class="si-hub-card" onclick="siOpen('div')">占術プロファイル</button>
    <button class="si-hub-card" onclick="siOpen('forecast')">${year}年の運勢</button>
    <button class="si-hub-card" onclick="siOpen('monthly')">月間運勢</button>
    ${personalityContent ? `<button class="si-hub-card" onclick="siOpen('pers')">性格分析</button>` : ''}
  </div>

  ${card('core', '✦ あなたの本質', SECTION_QUOTES.core, coreContent, true)}
  ${card('div', '占術プロファイル', SECTION_QUOTES.divination, divContent + fpContent)}
  ${card('forecast', `✦ ${year}年の運勢`, SECTION_QUOTES.forecast, forecastContent)}
  ${card('monthly', '月間運勢', SECTION_QUOTES.monthly, monthlyContent)}
  ${personalityContent ? card('pers', '性格分析', SECTION_QUOTES.personality, personalityContent) : ''}

  <footer class="si-footer">
    <p>Self-Insight — あなたの取扱説明書を、AIが作ります</p>
    <p class="si-footer-sub">東洋占術 × 心理学 × AI</p>
  </footer>
</div>`;

  // === Interactions ===
  // Month tabs
  container.querySelectorAll('.si-month-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      container.querySelectorAll('.si-month-tab').forEach(t => t.classList.remove('active'));
      container.querySelectorAll('.si-month-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      container.querySelector(`.si-month-panel[data-month="${tab.dataset.month}"]`)?.classList.add('active');
    });
  });

  // Scroll fade-in
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
  }, { threshold: 0.1 });
  container.querySelectorAll('.si-fade').forEach(el => observer.observe(el));
}

// ============================================================
// Global Interaction Functions
// ============================================================

function siToggle(id) {
  const body = document.getElementById('body-' + id);
  const header = body?.previousElementSibling;
  const chevron = header?.querySelector('.si-chevron');
  if (body) { body.classList.toggle('open'); }
  if (chevron) { chevron.classList.toggle('open'); }
  if (header) { header.setAttribute('aria-expanded', body.classList.contains('open')); }
}

function siOpen(id) {
  const body = document.getElementById('body-' + id);
  if (body && !body.classList.contains('open')) { siToggle(id); }
  document.getElementById('card-' + id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function siAccToggle(btn) {
  const item = btn.closest('.si-acc-item');
  item.classList.toggle('open');
}

// ============================================================
// Styles (inline, self-contained)
// ============================================================

const SI_STYLES = `<style>
.si-dashboard{max-width:640px;margin:0 auto;padding:0 16px 40px;color:#e8e9ed;font-family:Inter,'Noto Sans JP',sans-serif;-webkit-font-smoothing:antialiased}

/* Fade in */
.si-fade{opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s ease}
.si-fade.visible{opacity:1;transform:translateY(0)}

/* Hero */
.si-hero{text-align:center;padding:40px 0 28px;position:relative;overflow:hidden}
.si-particles{position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,rgba(99,102,241,.08) 0%,transparent 70%);pointer-events:none}
.si-archetype-glow{font-size:clamp(17px,3vw,22px);color:#818cf8;text-shadow:0 0 24px rgba(99,102,241,.5),0 0 48px rgba(99,102,241,.2);margin-bottom:10px;letter-spacing:.5px;animation:glowPulse 3s ease-in-out infinite}
@keyframes glowPulse{0%,100%{text-shadow:0 0 24px rgba(99,102,241,.5),0 0 48px rgba(99,102,241,.2)}50%{text-shadow:0 0 32px rgba(99,102,241,.7),0 0 64px rgba(99,102,241,.3)}}
.si-hero h1{font-size:clamp(26px,5vw,34px);font-weight:700;margin:0;position:relative}
.si-tagline{color:#9ca3af;font-size:13px;margin-top:8px}
.si-hero-sub{margin-top:14px;font-size:12px;color:#6366f1;letter-spacing:2px;text-transform:uppercase;font-weight:600}

/* Hub Cards */
.si-hub{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:20px 0}
.si-hub-card{background:#1a1d27;border:1px solid #2e3347;border-radius:10px;padding:14px 12px;font-size:13px;font-weight:600;color:#e8e9ed;cursor:pointer;font-family:inherit;transition:all .2s;text-align:left}
.si-hub-card:hover{border-color:#6366f1;background:rgba(99,102,241,.06)}

/* Card Sections */
.si-card-wrap{margin-top:20px;background:#1a1d27;border:1px solid #2e3347;border-radius:14px;overflow:hidden}
.si-card-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:18px 20px;background:transparent;border:none;color:#e8e9ed;cursor:pointer;font-family:inherit;text-align:left}
.si-card-header h2{font-size:16px;font-weight:600;margin:0}
.si-quote{font-size:12px;color:#818cf8;font-style:italic;margin-top:4px;opacity:.8}
.si-chevron{width:10px;height:10px;border-right:2px solid #9ca3af;border-bottom:2px solid #9ca3af;transform:rotate(45deg);transition:transform .3s ease;flex-shrink:0}
.si-chevron.open{transform:rotate(-135deg)}
.si-card-body{max-height:0;overflow:hidden;transition:max-height .4s ease,padding .3s ease;padding:0 20px}
.si-card-body.open{max-height:5000px;padding:0 20px 20px}

/* Inner content */
.si-inner{margin-bottom:16px}
.si-inner h3{font-size:14px;font-weight:600;color:#818cf8;margin-bottom:8px}
.si-inner p{font-size:13px;color:#d1d5db;line-height:1.7;margin:6px 0}
.si-note{font-size:12px;color:#9ca3af;margin-top:8px;line-height:1.6}
.si-warn{color:#fbbf24;font-size:13px;line-height:1.6;padding:10px 14px;background:rgba(251,191,36,.06);border-radius:8px;border-left:3px solid #fbbf24}

/* Summary Grid */
.si-summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:16px}
.si-sum-card{text-align:center;padding:12px 6px;background:#242837;border-radius:10px}
.si-sum-label{font-size:10px;color:#9ca3af;margin-bottom:4px}
.si-sum-val{font-size:20px;font-weight:700}
.si-sum-sub{font-size:10px;color:#818cf8;margin-top:2px}

/* Badges */
.si-badge{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600}
.si-badge.accent{background:rgba(99,102,241,.15);color:#818cf8}
.si-badge.rare{background:rgba(167,139,250,.12);color:#a78bfa;border:1px solid rgba(167,139,250,.2)}
.si-badge.danger{background:rgba(248,113,113,.12);color:#f87171}
.si-rarities{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}

/* Elements */
.si-elements{display:flex;gap:8px;margin:8px 0}
.si-element{flex:1;text-align:center;padding:10px 4px;background:#242837;border-radius:8px;transition:opacity .2s}
.si-element.missing{opacity:.35}
.si-element .emoji{font-size:18px;display:block}
.si-element .label{font-size:12px;display:block;margin:2px 0}
.si-element .pct{font-size:11px;color:#9ca3af}

/* Pillars */
.si-pillars{display:flex;gap:8px}
.si-pillar-card{flex:1;text-align:center;background:#242837;border-radius:10px;padding:14px 8px}
.pillar-label{font-size:11px;color:#9ca3af}
.pillar-chars{font-size:22px;font-weight:700;margin:4px 0}
.pillar-reading{font-size:11px;color:#9ca3af}
.pillar-element{font-size:11px;color:#818cf8;margin-top:4px}

/* Accordion */
.si-accordion{display:flex;flex-direction:column;gap:2px}
.si-acc-btn{width:100%;padding:14px 16px;background:#242837;border:none;color:#e8e9ed;font-size:14px;font-weight:500;text-align:left;cursor:pointer;font-family:inherit;border-radius:8px;transition:background .2s}
.si-acc-btn:hover{background:#2e3347}
.si-acc-body{max-height:0;overflow:hidden;padding:0 16px;transition:max-height .3s ease,padding .2s ease}
.si-acc-item.open .si-acc-body{max-height:1000px;padding:12px 16px}
.si-acc-body p{font-size:13px;color:#d1d5db;line-height:1.7;margin:4px 0}

/* Bars */
.si-bar-group{display:flex;flex-direction:column;gap:8px}
.si-bar-item{display:flex;align-items:center;gap:8px;font-size:12px}
.si-bar-item>span:first-child{width:60px;text-align:right;color:#9ca3af}
.si-bar-item>span:last-child{width:40px;color:#9ca3af}
.si-bar{flex:1;height:8px;background:#242837;border-radius:4px;overflow:hidden}
.si-bar>div{height:100%;background:linear-gradient(90deg,#6366f1,#818cf8);border-radius:4px;transition:width .6s ease}

/* Cycle Chart */
.si-cycle-bar{display:flex;align-items:flex-end;gap:4px;height:80px;padding-top:8px}
.si-cycle-item{flex:1;display:flex;flex-direction:column;align-items:center;gap:4px}
.si-cycle-item .bar{width:100%;border-radius:4px 4px 0 0;min-height:4px;transition:height .5s ease}
.si-cycle-item .yr{font-size:10px;color:#9ca3af}
.si-cycle-item.current .yr{color:#818cf8;font-weight:700}
.si-cycle-item.current .bar{box-shadow:0 0 10px rgba(99,102,241,.5)}

/* Monthly */
.si-month-tabs{display:flex;gap:4px;overflow-x:auto;padding-bottom:8px;-webkit-overflow-scrolling:touch}
.si-month-tab{background:#242837;border:1px solid #2e3347;color:#9ca3af;padding:7px 13px;border-radius:16px;font-size:12px;cursor:pointer;white-space:nowrap;font-family:inherit;transition:all .2s}
.si-month-tab.active{background:rgba(99,102,241,.15);border-color:#6366f1;color:#818cf8;font-weight:600}
.si-month-panel{display:none;background:#242837;border-radius:10px;padding:16px;margin-top:8px}
.si-month-panel.active{display:block}
.si-month-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.si-month-header span:first-child{font-weight:600;font-size:15px}
.si-phase-tag{font-size:12px;padding:3px 10px;border-radius:10px;background:rgba(99,102,241,.1);color:#818cf8}
.si-phase-tag.danger{background:rgba(248,113,113,.1);color:#f87171}
.si-phase-tag.caution{background:rgba(251,191,36,.1);color:#fbbf24}
.si-phase-tag.great{background:rgba(52,211,153,.1);color:#34d399}
.si-phase-tag.good{background:rgba(99,102,241,.1);color:#818cf8}
.si-month-narrative{font-size:12px;color:#9ca3af;line-height:1.6;margin-bottom:12px}
.si-domains{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.si-domain{display:flex;justify-content:space-between;align-items:center;padding:6px 0}
.domain-label{font-size:13px;font-weight:500}
.domain-stars{font-size:12px;letter-spacing:1px}

/* Footer */
.si-footer{text-align:center;padding:28px 0;border-top:1px solid #2e3347;margin-top:32px}
.si-footer p{font-size:13px;color:#818cf8;font-weight:500}
.si-footer-sub{font-size:11px;color:#555;margin-top:4px}
</style>`;

// ============================================================
// Export
// ============================================================

if (typeof window !== 'undefined') {
  window.SelfInsightRenderer = { renderDashboard };
}
