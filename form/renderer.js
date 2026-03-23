/**
 * Self-Insight Dashboard Renderer
 * Renders profile data as an inline dashboard after form submission.
 * Matches generate_dashboard.py output style.
 */

const ELEMENT_EMOJI = {'木':'🌳','火':'🔥','土':'⛰️','金':'⚔️','水':'💧'};
const DOMAIN_LABELS = { work:'仕事', money:'お金', health:'健康', romance:'恋愛' };
const DOMAIN_COLORS = { work:'#6366f1', money:'#eab308', health:'#34d399', romance:'#f472b6' };
const MONTH_NAMES = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];

function starRating(n) { return '★'.repeat(n) + '☆'.repeat(5 - n); }

function renderDashboard(profile, container) {
  const p = profile;
  const fp = p.four_pillars;
  const ns = p.nine_star_ki;
  const rk = p.rokusei;
  const wa = p.western_astrology;
  const bt = p.blood_type;
  const pers = p.personality;
  const monthly = p.monthly_fortune;
  const currentMonth = new Date().getMonth() + 1;

  // Archetype name
  const dmEl = fp.day_master.element;
  const elJP = {'Wood':'木','Fire':'火','Earth':'土','Metal':'金','Water':'水'};
  const elNames = {'Wood':'樹','Fire':'炎','Earth':'大地','Metal':'剣','Water':'海'};
  const archetype = `${fp.day_master.yin_yang === 'Yin' ? '静かな' : '燃える'}${elNames[dmEl] || dmEl}の探求者`;

  container.innerHTML = `
<div class="si-dashboard">
  <!-- Hero -->
  <section class="si-hero">
    <div class="si-archetype-glow">${archetype}</div>
    <h1>${p.identity.name}</h1>
    <div class="si-tagline">
      ${wa.sun_sign.jp} ${wa.sun_sign.symbol} · ${ns.year_star.name} · ${rk.main_star.name}${rk.main_star.polarity}${rk.reigou ? ' 霊合' : ''} · ${bt.type}型
    </div>
  </section>

  <!-- Core Identity -->
  <section class="si-section">
    <h2>✦ あなたの本質</h2>
    <div class="si-card">
      <h3>日主: ${fp.day_master.char}（${elJP[dmEl]}の${fp.day_master.yin_yang === 'Yang' ? '陽' : '陰'}）</h3>
      <p>${fp.day_master.description}</p>
    </div>
    <div class="si-card">
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
      <p class="si-insight">${fp.element_insight}</p>
    </div>
  </section>

  <!-- Four Pillars -->
  <section class="si-section">
    <h2>四柱推命</h2>
    <div class="si-pillars">
      ${[['年柱', fp.year_pillar], ['月柱', fp.month_pillar], ['日柱', fp.day_pillar]].map(([label, pillar]) =>
        `<div class="si-pillar-card">
          <div class="pillar-label">${label}</div>
          <div class="pillar-chars">${pillar.full}</div>
          <div class="pillar-reading">${pillar.stem.reading}${pillar.branch.reading}</div>
          <div class="pillar-element">${elJP[pillar.stem.element]}/${elJP[pillar.branch.element]}</div>
        </div>`
      ).join('')}
    </div>
  </section>

  <!-- Nine Star Ki -->
  <section class="si-section">
    <h2>九星気学</h2>
    <div class="si-card">
      <p><strong>本命星:</strong> ${ns.year_star.name}（${ns.year_star.element}）</p>
      <p><strong>月命星:</strong> ${ns.month_star.name}（${ns.month_star.element}）</p>
      ${ns.year_cycle ? `<p><strong>${new Date().getFullYear()}年:</strong> ${ns.year_cycle.position.palace}（${ns.year_cycle.position.meaning}）</p>` : ''}
    </div>
  </section>

  <!-- Rokusei -->
  <section class="si-section">
    <h2>六星占術</h2>
    <div class="si-card">
      <p><strong>運命星:</strong> ${rk.main_star.name}${rk.main_star.polarity}${rk.reigou ? ' <span class="si-badge">霊合星人</span>' : ''}</p>
      ${rk.reigou && rk.sub_star ? `<p><strong>副星:</strong> ${rk.sub_star.name}${rk.sub_star.polarity}</p>` : ''}
      ${rk.twelve_year_cycle ? (() => {
        const current = rk.twelve_year_cycle.find(e => e.current);
        return current ? `<p><strong>${new Date().getFullYear()}年:</strong> ${current.phase}${current['殺界'] ? ` <span class="si-badge danger">${current['殺界']}</span>` : ''}</p>` : '';
      })() : ''}
    </div>
  </section>

  <!-- Western Astrology -->
  <section class="si-section">
    <h2>西洋占星術</h2>
    <div class="si-card">
      <p><strong>太陽星座:</strong> ${wa.sun_sign.jp}（${wa.sun_sign.sign}） ${wa.sun_sign.symbol}</p>
      <p><strong>エレメント:</strong> ${wa.sun_sign.element} · ${wa.sun_sign.quality}</p>
      <p><strong>守護星:</strong> ${wa.ruling_planet}</p>
    </div>
  </section>

  <!-- Blood Type -->
  <section class="si-section">
    <h2>血液型</h2>
    <div class="si-card">
      <p><strong>${bt.type}型</strong>（日本人の${bt.pct || BLOOD_TYPE_DATA[bt.type]?.pct || '?'}%）</p>
      ${bt.strengths ? `<p>✦ ${bt.strengths.join(' · ')}</p>` : ''}
      ${bt.challenges ? `<p>△ ${bt.challenges.join(' · ')}</p>` : ''}
    </div>
  </section>

  ${pers.enneagram ? `
  <!-- Enneagram -->
  <section class="si-section">
    <h2>エニアグラム</h2>
    <div class="si-card">
      <p><strong>タイプ ${pers.enneagram.type}: ${pers.enneagram.name}</strong></p>
      <p>${pers.enneagram.description}</p>
      ${pers.enneagram.wing ? `<p>ウイング: ${pers.enneagram.wing}</p>` : ''}
      <p>成長方向: → タイプ${pers.enneagram.growth_direction} / ストレス方向: → タイプ${pers.enneagram.stress_direction}</p>
    </div>
  </section>` : ''}

  ${pers.hsp ? `
  <!-- HSP -->
  <section class="si-section">
    <h2>HSP感受性</h2>
    <div class="si-card">
      <p><strong>レベル:</strong> ${pers.hsp.score === 'high' ? '高感受性' : pers.hsp.score === 'medium' ? '中程度' : '低感受性'}（${pers.hsp.total}/30）</p>
      <div class="si-bar-group">
        <div class="si-bar-item"><span>感覚</span><div class="si-bar"><div style="width:${pers.hsp.subscales.sensory/10*100}%"></div></div><span>${pers.hsp.subscales.sensory}/10</span></div>
        <div class="si-bar-item"><span>感情</span><div class="si-bar"><div style="width:${pers.hsp.subscales.emotional/10*100}%"></div></div><span>${pers.hsp.subscales.emotional}/10</span></div>
        <div class="si-bar-item"><span>社会</span><div class="si-bar"><div style="width:${pers.hsp.subscales.social/10*100}%"></div></div><span>${pers.hsp.subscales.social}/10</span></div>
      </div>
    </div>
  </section>` : ''}

  ${pers.adhd ? `
  <!-- ADHD -->
  <section class="si-section">
    <h2>注意特性</h2>
    <div class="si-card">
      <p><strong>傾向:</strong> ${pers.adhd.tendency === 'significant' ? '顕著' : pers.adhd.tendency === 'leaning' ? '傾向あり' : '低い'}</p>
      <p>閾値超過: ${pers.adhd.above_threshold_count}/${pers.adhd.total_items}項目</p>
    </div>
  </section>` : ''}

  ${pers.big_five ? `
  <!-- Big Five -->
  <section class="si-section">
    <h2>Big Five性格特性${pers.mbti ? ` → ${pers.mbti}` : ''}</h2>
    <div class="si-card">
      <div class="si-bar-group">
        ${Object.entries({Extraversion:'外向性',Agreeableness:'協調性',Conscientiousness:'誠実性',Neuroticism:'神経症傾向',Openness:'開放性'}).map(([k,label]) =>
          `<div class="si-bar-item"><span>${label}</span><div class="si-bar"><div style="width:${(pers.big_five[k]||0)/20*100}%"></div></div><span>${pers.big_five[k]||0}/20</span></div>`
        ).join('')}
      </div>
    </div>
  </section>` : ''}

  <!-- Year Forecast -->
  <section class="si-section">
    <h2>✦ ${new Date().getFullYear()}年の運勢</h2>
    ${ns.nine_year_cycle ? `
    <div class="si-card">
      <h3>運気サイクル</h3>
      <div class="si-cycle-bar">
        ${ns.nine_year_cycle.map(y => {
          const h = Math.round(y.energy / 100 * 60);
          return `<div class="si-cycle-item ${y.current ? 'current' : ''}">
            <div class="bar" style="height:${h}px;background:${y.energy >= 70 ? '#34d399' : y.energy >= 40 ? '#eab308' : '#f87171'}"></div>
            <span class="yr">${String(y.year).slice(2)}</span>
          </div>`;
        }).join('')}
      </div>
    </div>` : ''}
  </section>

  <!-- Monthly Fortune -->
  <section class="si-section">
    <h2>月間運勢</h2>
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
            <span class="si-phase">${m.rokusei.phase}${m.rokusei.satsukai ? ` · ${m.rokusei.satsukai}` : ''}</span>
          </div>
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
    </div>
  </section>

  <!-- Footer -->
  <footer class="si-footer">
    <p>Self-Insight — Powered by AI × 東洋占術 × 心理学</p>
  </footer>
</div>

<style>
.si-dashboard{max-width:640px;margin:0 auto;padding:0 16px 40px;color:#e8e9ed;font-family:Inter,'Noto Sans JP',sans-serif}
.si-hero{text-align:center;padding:32px 0 24px}
.si-archetype-glow{font-size:clamp(16px,3vw,20px);color:#818cf8;text-shadow:0 0 20px rgba(99,102,241,.4);margin-bottom:8px}
.si-hero h1{font-size:clamp(24px,5vw,32px);font-weight:700;margin:0}
.si-tagline{color:#9ca3af;font-size:13px;margin-top:8px}
.si-section{margin-top:28px}
.si-section h2{font-size:16px;font-weight:600;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #2e3347}
.si-card{background:#1a1d27;border:1px solid #2e3347;border-radius:12px;padding:16px;margin-bottom:12px}
.si-card h3{font-size:14px;font-weight:600;color:#818cf8;margin-bottom:8px}
.si-card p{font-size:13px;color:#d1d5db;line-height:1.6;margin:4px 0}
.si-insight{font-size:12px;color:#9ca3af;margin-top:8px;font-style:italic}
.si-badge{background:rgba(99,102,241,.15);color:#818cf8;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.si-badge.danger{background:rgba(248,113,113,.15);color:#f87171}

/* Elements */
.si-elements{display:flex;gap:8px;margin:8px 0}
.si-element{flex:1;text-align:center;padding:8px 4px;background:#242837;border-radius:8px}
.si-element.missing{opacity:.4}
.si-element .emoji{font-size:18px;display:block}
.si-element .label{font-size:12px;display:block;margin:2px 0}
.si-element .pct{font-size:11px;color:#9ca3af}

/* Pillars */
.si-pillars{display:flex;gap:8px}
.si-pillar-card{flex:1;text-align:center;background:#1a1d27;border:1px solid #2e3347;border-radius:12px;padding:12px 8px}
.pillar-label{font-size:11px;color:#9ca3af}
.pillar-chars{font-size:22px;font-weight:700;margin:4px 0}
.pillar-reading{font-size:11px;color:#9ca3af}
.pillar-element{font-size:11px;color:#818cf8;margin-top:4px}

/* Bars */
.si-bar-group{display:flex;flex-direction:column;gap:8px}
.si-bar-item{display:flex;align-items:center;gap:8px;font-size:12px}
.si-bar-item>span:first-child{width:48px;text-align:right;color:#9ca3af}
.si-bar-item>span:last-child{width:40px;color:#9ca3af}
.si-bar{flex:1;height:8px;background:#242837;border-radius:4px;overflow:hidden}
.si-bar>div{height:100%;background:linear-gradient(90deg,#6366f1,#818cf8);border-radius:4px}

/* Cycle */
.si-cycle-bar{display:flex;align-items:flex-end;gap:4px;height:80px;padding-top:8px}
.si-cycle-item{flex:1;display:flex;flex-direction:column;align-items:center;gap:4px}
.si-cycle-item .bar{width:100%;border-radius:4px 4px 0 0;min-height:4px}
.si-cycle-item .yr{font-size:10px;color:#9ca3af}
.si-cycle-item.current .yr{color:#818cf8;font-weight:700}
.si-cycle-item.current .bar{box-shadow:0 0 8px rgba(99,102,241,.5)}

/* Monthly */
.si-month-tabs{display:flex;gap:4px;overflow-x:auto;padding-bottom:8px;-webkit-overflow-scrolling:touch}
.si-month-tab{background:#242837;border:1px solid #2e3347;color:#9ca3af;padding:6px 12px;border-radius:16px;font-size:12px;cursor:pointer;white-space:nowrap;font-family:inherit}
.si-month-tab.active{background:rgba(99,102,241,.15);border-color:#6366f1;color:#818cf8;font-weight:600}
.si-month-panel{display:none;background:#1a1d27;border:1px solid #2e3347;border-radius:12px;padding:16px;margin-top:8px}
.si-month-panel.active{display:block}
.si-month-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.si-month-header span:first-child{font-weight:600;font-size:15px}
.si-phase{font-size:12px;color:#9ca3af}
.si-domains{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.si-domain{display:flex;justify-content:space-between;align-items:center;padding:6px 0}
.domain-label{font-size:13px;font-weight:500}
.domain-stars{font-size:12px;letter-spacing:1px}

/* Footer */
.si-footer{text-align:center;padding:24px 0;font-size:11px;color:#555;border-top:1px solid #2e3347;margin-top:32px}
</style>
`;

  // Month tab interaction
  container.querySelectorAll('.si-month-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      container.querySelectorAll('.si-month-tab').forEach(t => t.classList.remove('active'));
      container.querySelectorAll('.si-month-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      container.querySelector(`.si-month-panel[data-month="${tab.dataset.month}"]`)?.classList.add('active');
    });
  });
}

if (typeof window !== 'undefined') {
  window.SelfInsightRenderer = { renderDashboard };
}
