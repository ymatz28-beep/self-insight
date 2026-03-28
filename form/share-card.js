/**
 * Self-Insight Share Card Generator
 * Generates shareable PNG cards using pure HTML5 Canvas API.
 * Two sizes: 'story' (1080x1920 IG Stories) and 'ogp' (1200x675 X/OGP)
 */

// ============================================================
// Constants
// ============================================================

const SC_ELEMENT_COLORS = {
  Wood:  '#4ade80',
  Fire:  '#f87171',
  Earth: '#facc15',
  Metal: '#94a3b8',
  Water: '#60a5fa',
};

const SC_ELEMENT_JP = { Wood:'木', Fire:'火', Earth:'土', Metal:'金', Water:'水' };

const SC_ARCHETYPE_PREFIX = {
  Wood:  ['静かな森の', '風を読む'],
  Fire:  ['炎を宿す', '灯火の'],
  Earth: ['大地に立つ', '揺るがぬ'],
  Metal: ['刃を磨く', '光を放つ'],
  Water: ['流れを知る', '深淵の'],
};

const SC_ARCHETYPE_SUFFIX = ['共鳴者', '探究者', '創造者', '守護者', '開拓者'];

// ============================================================
// Archetype Name Generator
// ============================================================

function buildArchetypeName(profile) {
  const fp = profile.four_pillars;
  const dmEl = fp.day_master.element; // e.g. 'Fire'
  const dmYY = fp.day_master.yin_yang; // 'Yang' | 'Yin'

  // Pick prefix based on yin/yang: Yin → first option, Yang → second option
  const prefixes = SC_ARCHETYPE_PREFIX[dmEl] || SC_ARCHETYPE_PREFIX.Water;
  const prefix = dmYY === 'Yin' ? prefixes[0] : prefixes[1];

  // Pick suffix based on dominant personality data if available
  // Fall back to mapping from element
  const elToSuffixIdx = { Wood: 0, Fire: 1, Earth: 3, Metal: 2, Water: 4 };
  const suffixIdx = elToSuffixIdx[dmEl] ?? 0;
  const suffix = SC_ARCHETYPE_SUFFIX[suffixIdx];

  return prefix + suffix;
}

// ============================================================
// Font Loading
// ============================================================

let fontsLoaded = false;

async function loadShareCardFonts() {
  if (fontsLoaded) return;
  try {
    const interFont = new FontFace(
      'Inter',
      "url('https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2')",
      { weight: '400 700' }
    );
    const notoFont = new FontFace(
      'Noto Sans JP',
      "url('https://fonts.gstatic.com/s/notosansjp/v52/-F6jfjtqLzI2JPCgQBnw7HFyzSD-AsregP8VFJEk.woff2')",
      { weight: '400 700' }
    );
    await Promise.allSettled([
      interFont.load().then(f => document.fonts.add(f)),
      notoFont.load().then(f => document.fonts.add(f)),
    ]);
    fontsLoaded = true;
  } catch (e) {
    // Non-fatal: fall back to system fonts
    fontsLoaded = true;
  }
}

// ============================================================
// Canvas Helpers
// ============================================================

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function drawGradientBackground(ctx, w, h) {
  const grad = ctx.createLinearGradient(0, 0, w, h);
  grad.addColorStop(0,   '#1e1b4b');
  grad.addColorStop(0.4, '#312e81');
  grad.addColorStop(0.7, '#1e1b4b');
  grad.addColorStop(1,   '#0f0e2a');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);
}

function drawNoiseOverlay(ctx, w, h) {
  // Subtle noise dots for texture
  ctx.save();
  for (let i = 0; i < 1200; i++) {
    const x = Math.random() * w;
    const y = Math.random() * h;
    ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.025})`;
    ctx.fillRect(x, y, 1, 1);
  }
  ctx.restore();
}

function drawGlowCircle(ctx, cx, cy, radius, color) {
  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
  grad.addColorStop(0, color + '18');
  grad.addColorStop(1, 'transparent');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.fill();
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const chars = [...text];
  let line = '';
  let lines = [];
  for (const ch of chars) {
    const testLine = line + ch;
    const m = ctx.measureText(testLine);
    if (m.width > maxWidth && line.length > 0) {
      lines.push(line);
      line = ch;
    } else {
      line = testLine;
    }
  }
  if (line) lines.push(line);
  lines.forEach((l, i) => {
    ctx.fillText(l, x, y + i * lineHeight);
  });
  return lines.length;
}

// ============================================================
// Story Card (1080 x 1920)
// ============================================================

function drawStoryCard(ctx, profile, w, h) {
  const fp = profile.four_pillars;
  const ns = profile.nine_star_ki;
  const rk = profile.rokusei;
  const wa = profile.western_astrology;
  const dmEl = fp.day_master.element;
  const elementColor = SC_ELEMENT_COLORS[dmEl] || '#a5b4fc';
  const elementJP = SC_ELEMENT_JP[dmEl] || '?';

  const pad = 64;
  const midX = w / 2;

  // -- Background --
  drawGradientBackground(ctx, w, h);
  drawNoiseOverlay(ctx, w, h);

  // Decorative glow circles
  drawGlowCircle(ctx, w * 0.8, h * 0.15, 400, elementColor);
  drawGlowCircle(ctx, w * 0.2, h * 0.7,  350, '#6366f1');

  // Subtle grid lines
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.03)';
  ctx.lineWidth = 1;
  for (let gx = 0; gx < w; gx += 80) {
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, h); ctx.stroke();
  }
  for (let gy = 0; gy < h; gy += 80) {
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(w, gy); ctx.stroke();
  }
  ctx.restore();

  let y = 0;

  // -- Top brand mark --
  y = 90;
  ctx.fillStyle = 'rgba(255,255,255,0.35)';
  ctx.font = '500 30px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('✦  AI Self-Insight', midX, y);

  // Thin horizontal separator
  y += 28;
  ctx.save();
  const sepGrad = ctx.createLinearGradient(pad, 0, w - pad, 0);
  sepGrad.addColorStop(0,   'transparent');
  sepGrad.addColorStop(0.3, 'rgba(255,255,255,0.15)');
  sepGrad.addColorStop(0.7, 'rgba(255,255,255,0.15)');
  sepGrad.addColorStop(1,   'transparent');
  ctx.strokeStyle = sepGrad;
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(w - pad, y); ctx.stroke();
  ctx.restore();

  // -- Archetype name box --
  y += 64;
  const archetypeName = buildArchetypeName(profile);

  // Box background
  const boxW = w - pad * 2;
  const boxH = 160;
  const boxX = pad;
  const boxY = y;

  // Box gradient fill
  const boxGrad = ctx.createLinearGradient(boxX, boxY, boxX + boxW, boxY + boxH);
  boxGrad.addColorStop(0, 'rgba(99,102,241,0.18)');
  boxGrad.addColorStop(1, 'rgba(139,92,246,0.08)');
  roundRect(ctx, boxX, boxY, boxW, boxH, 20);
  ctx.fillStyle = boxGrad;
  ctx.fill();

  // Box border glow using element color
  ctx.save();
  ctx.strokeStyle = elementColor + '55';
  ctx.lineWidth = 1.5;
  roundRect(ctx, boxX, boxY, boxW, boxH, 20);
  ctx.stroke();
  ctx.restore();

  // Archetype label small
  ctx.fillStyle = elementColor;
  ctx.font = '500 22px Inter, "Noto Sans JP", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('あなたのアーキタイプ', midX, boxY + 40);

  // Archetype name large
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 52px "Noto Sans JP", Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(archetypeName, midX, boxY + 112);

  y = boxY + boxH + 60;

  // -- Day Master row --
  const dmChar = fp.day_master.char;
  const dmYY   = fp.day_master.yin_yang === 'Yang' ? '陽' : '陰';
  const dmDesc  = fp.day_master.description || '';

  // Three chip boxes: kanji, element, yin/yang
  const chipW = 130;
  const chipH = 110;
  const chipGap = 20;
  const totalChipW = chipW * 3 + chipGap * 2;
  const chipStartX = midX - totalChipW / 2;

  [dmChar, elementJP, dmYY].forEach((label, i) => {
    const cx = chipStartX + i * (chipW + chipGap);
    roundRect(ctx, cx, y, chipW, chipH, 14);
    ctx.fillStyle = 'rgba(255,255,255,0.06)';
    ctx.fill();
    ctx.save();
    ctx.strokeStyle = elementColor + '40';
    ctx.lineWidth = 1;
    roundRect(ctx, cx, y, chipW, chipH, 14);
    ctx.stroke();
    ctx.restore();
    ctx.fillStyle = elementColor;
    ctx.font = '700 56px "Noto Sans JP", Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, cx + chipW / 2, y + 76);
  });

  // Day Master label beneath chips
  y += chipH + 18;
  ctx.fillStyle = 'rgba(255,255,255,0.45)';
  ctx.font = '400 26px Inter, "Noto Sans JP", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('日主（Day Master）', midX, y);

  y += 60;

  // -- Nine Star · Western sign · Rokusei row --
  const nineStarName = ns.year_star.name;
  const sunSignJP    = wa.sun_sign.jp;
  const sunSymbol    = wa.sun_sign.symbol;
  const rokuseiName  = rk.main_star.name;
  const rokuseiPol   = rk.main_star.polarity === '+' ? '(＋)' : '(−)';
  const isReigou     = rk.reigou;

  ctx.fillStyle = '#e8e9ed';
  ctx.font = '600 36px "Noto Sans JP", Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`${nineStarName}  ·  ${sunSignJP} ${sunSymbol}`, midX, y);

  y += 52;
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.font = '400 30px "Noto Sans JP", Inter, sans-serif';
  ctx.fillText(`${rokuseiName}${rokuseiPol}${isReigou ? ' 霊合' : ''}`, midX, y);

  // -- Separator --
  y += 58;
  ctx.save();
  const sep2Grad = ctx.createLinearGradient(pad * 2, 0, w - pad * 2, 0);
  sep2Grad.addColorStop(0,   'transparent');
  sep2Grad.addColorStop(0.5, 'rgba(255,255,255,0.12)');
  sep2Grad.addColorStop(1,   'transparent');
  ctx.strokeStyle = sep2Grad;
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(pad * 2, y); ctx.lineTo(w - pad * 2, y); ctx.stroke();
  ctx.restore();

  y += 52;

  // -- 2026 forecast --
  const forecastYear = new Date().getFullYear();
  let palaceName = '';
  let rokuseiPhase = '';

  if (ns.year_cycle?.position?.palace) {
    palaceName = ns.year_cycle.position.palace;
  } else if (ns.nine_year_cycle) {
    const cur = ns.nine_year_cycle.find(e => e.current);
    if (cur) palaceName = cur.palace;
  }

  if (rk.twelve_year_cycle) {
    const cur = rk.twelve_year_cycle.find(e => e.current);
    if (cur) rokuseiPhase = cur.phase;
  }

  ctx.fillStyle = '#a5b4fc';
  ctx.font = '500 28px Inter, "Noto Sans JP", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`${forecastYear}年`, midX, y);

  y += 48;
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 46px "Noto Sans JP", Inter, sans-serif';
  ctx.fillText(
    [palaceName, rokuseiPhase].filter(Boolean).join('  ×  ') || '運勢詳細はダッシュボードで',
    midX, y
  );

  // Peak Year (best energy year from rokusei cycle)
  let peakYear = forecastYear;
  let peakEnergy = 0;
  if (rk.twelve_year_cycle) {
    for (const entry of rk.twelve_year_cycle) {
      if (entry.energy > peakEnergy && entry.year >= forecastYear) {
        peakEnergy = entry.energy;
        peakYear = entry.year;
      }
    }
  }

  y += 52;
  ctx.fillStyle = 'rgba(255,255,255,0.45)';
  ctx.font = '400 26px Inter, "Noto Sans JP", sans-serif';
  ctx.fillText(`Peak Year: ${peakYear}`, midX, y);

  y += 70;

  // -- Rarity badge section --
  const badgeW = boxW;
  const badgeH = isReigou ? 160 : (fp.missing_elements && fp.missing_elements.length > 0 ? 160 : 0);

  if (badgeH > 0) {
    roundRect(ctx, boxX, y, badgeW, badgeH, 16);
    if (isReigou) {
      const badgeGrad = ctx.createLinearGradient(boxX, y, boxX + badgeW, y + badgeH);
      badgeGrad.addColorStop(0, 'rgba(201,168,76,0.18)');
      badgeGrad.addColorStop(1, 'rgba(234,179,8,0.08)');
      ctx.fillStyle = badgeGrad;
      ctx.fill();
      ctx.save();
      ctx.strokeStyle = 'rgba(201,168,76,0.45)';
      ctx.lineWidth = 1.5;
      roundRect(ctx, boxX, y, badgeW, badgeH, 16);
      ctx.stroke();
      ctx.restore();

      ctx.fillStyle = '#facc15';
      ctx.font = '600 30px "Noto Sans JP", Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('⭐ Rarity', midX, y + 44);

      ctx.fillStyle = '#fde68a';
      ctx.font = '700 38px "Noto Sans JP", Inter, sans-serif';
      ctx.fillText('霊合星人（全人口の10%）', midX, y + 106);
    } else if (fp.missing_elements && fp.missing_elements.length > 0) {
      const missingGrad = ctx.createLinearGradient(boxX, y, boxX + badgeW, y + badgeH);
      missingGrad.addColorStop(0, 'rgba(99,102,241,0.18)');
      missingGrad.addColorStop(1, 'rgba(139,92,246,0.06)');
      ctx.fillStyle = missingGrad;
      ctx.fill();
      ctx.save();
      ctx.strokeStyle = 'rgba(99,102,241,0.35)';
      ctx.lineWidth = 1;
      roundRect(ctx, boxX, y, badgeW, badgeH, 16);
      ctx.stroke();
      ctx.restore();

      ctx.fillStyle = '#a5b4fc';
      ctx.font = '600 28px Inter, "Noto Sans JP", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('欠け五行', midX, y + 44);

      ctx.fillStyle = '#e8e9ed';
      ctx.font = '700 38px "Noto Sans JP", Inter, sans-serif';
      ctx.fillText(fp.missing_elements.join('・') + ' が欠如', midX, y + 104);
    }
    y += badgeH + 56;
  }

  // -- Five elements mini bars --
  const barZoneW = w - pad * 2;
  const barH = 14;
  const barGap = 22;
  const elements = ['木', '火', '土', '金', '水'];
  const elColorMap = {
    '木': SC_ELEMENT_COLORS.Wood,
    '火': SC_ELEMENT_COLORS.Fire,
    '土': SC_ELEMENT_COLORS.Earth,
    '金': SC_ELEMENT_COLORS.Metal,
    '水': SC_ELEMENT_COLORS.Water,
  };

  // Label
  ctx.fillStyle = 'rgba(255,255,255,0.35)';
  ctx.font = '400 24px Inter, "Noto Sans JP", sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('五行バランス', pad, y);
  y += 36;

  elements.forEach(el => {
    const b = fp.five_elements_balance[el];
    const pct = b?.pct ?? 0;
    const fillW = Math.round(barZoneW * pct / 100);

    // Track
    roundRect(ctx, pad, y, barZoneW, barH, barH / 2);
    ctx.fillStyle = 'rgba(255,255,255,0.07)';
    ctx.fill();

    // Fill
    if (fillW > 0) {
      roundRect(ctx, pad, y, fillW, barH, barH / 2);
      ctx.fillStyle = elColorMap[el] || '#a5b4fc';
      ctx.fill();
    }

    // Label
    ctx.fillStyle = elColorMap[el] || '#a5b4fc';
    ctx.font = '600 22px "Noto Sans JP", Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${el} ${pct}%`, pad - 10, y + 12);

    y += barGap;
  });

  y += 30;

  // -- Footer --
  // Separator
  ctx.save();
  const footSepGrad = ctx.createLinearGradient(pad, 0, w - pad, 0);
  footSepGrad.addColorStop(0,   'transparent');
  footSepGrad.addColorStop(0.3, 'rgba(255,255,255,0.12)');
  footSepGrad.addColorStop(0.7, 'rgba(255,255,255,0.12)');
  footSepGrad.addColorStop(1,   'transparent');
  ctx.strokeStyle = footSepGrad;
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(w - pad, y); ctx.stroke();
  ctx.restore();

  y += 44;
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '500 28px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('selfinsight.app', midX, y);

  y += 46;
  ctx.fillStyle = '#a5b4fc';
  ctx.font = '400 26px "Noto Sans JP", Inter, sans-serif';
  ctx.fillText('あなたも診断する →', midX, y);
}

// ============================================================
// OGP Card (1200 x 675)
// ============================================================

function drawOgpCard(ctx, profile, w, h) {
  const fp = profile.four_pillars;
  const ns = profile.nine_star_ki;
  const rk = profile.rokusei;
  const wa = profile.western_astrology;
  const dmEl = fp.day_master.element;
  const elementColor = SC_ELEMENT_COLORS[dmEl] || '#a5b4fc';
  const elementJP = SC_ELEMENT_JP[dmEl] || '?';

  const pad = 56;
  const midX = w / 2;
  const midY = h / 2;

  // Background
  drawGradientBackground(ctx, w, h);
  drawNoiseOverlay(ctx, w, h);

  // Glow orbs
  drawGlowCircle(ctx, w * 0.85, h * 0.2, 300, elementColor);
  drawGlowCircle(ctx, w * 0.15, h * 0.8, 280, '#6366f1');

  let y = 0;

  // -- Left column: identity --
  const colW = w * 0.55;

  // Brand mark
  y = 64;
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  ctx.font = '500 20px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('✦  AI Self-Insight', pad, y);

  // Archetype name
  y += 52;
  const archetypeName = buildArchetypeName(profile);
  ctx.fillStyle = elementColor;
  ctx.font = '400 18px "Noto Sans JP", Inter, sans-serif';
  ctx.fillText('あなたのアーキタイプ', pad, y);

  y += 48;
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 46px "Noto Sans JP", Inter, sans-serif';
  ctx.textAlign = 'left';
  const archnLines = wrapText(ctx, archetypeName, pad, y, colW - pad, 56);
  y += archnLines * 56;

  // Day master chips
  y += 16;
  const chipSize = 72;
  const chipGap = 10;
  const dmChar = fp.day_master.char;
  const dmYY   = fp.day_master.yin_yang === 'Yang' ? '陽' : '陰';

  [dmChar, elementJP, dmYY].forEach((label, i) => {
    const cx = pad + i * (chipSize + chipGap);
    roundRect(ctx, cx, y, chipSize, chipSize, 10);
    ctx.fillStyle = 'rgba(255,255,255,0.07)';
    ctx.fill();
    ctx.save();
    ctx.strokeStyle = elementColor + '45';
    ctx.lineWidth = 1;
    roundRect(ctx, cx, y, chipSize, chipSize, 10);
    ctx.stroke();
    ctx.restore();

    ctx.fillStyle = elementColor;
    ctx.font = '700 36px "Noto Sans JP", Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, cx + chipSize / 2, y + 50);
  });

  y += chipSize + 20;

  // Sign row
  const nineStarName = ns.year_star.name;
  const sunSignJP    = wa.sun_sign.jp;
  const sunSymbol    = wa.sun_sign.symbol;
  const rokuseiName  = rk.main_star.name;
  const rokuseiPol   = rk.main_star.polarity === '+' ? '(＋)' : '(−)';
  const isReigou     = rk.reigou;

  ctx.fillStyle = '#e8e9ed';
  ctx.font = '500 22px "Noto Sans JP", Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`${nineStarName}  ·  ${sunSignJP} ${sunSymbol}`, pad, y);

  y += 36;
  ctx.fillStyle = 'rgba(255,255,255,0.55)';
  ctx.font = '400 20px "Noto Sans JP", Inter, sans-serif';
  ctx.fillText(`${rokuseiName}${rokuseiPol}${isReigou ? ' 霊合' : ''}`, pad, y);

  // -- Right column: data panel --
  const rightX = colW + pad;
  const rightW = w - rightX - pad;
  const panelH = h - pad * 2;

  // Panel background
  roundRect(ctx, rightX - 8, pad, rightW + 8, panelH, 16);
  const panelGrad = ctx.createLinearGradient(rightX, pad, rightX + rightW, pad + panelH);
  panelGrad.addColorStop(0, 'rgba(99,102,241,0.12)');
  panelGrad.addColorStop(1, 'rgba(30,27,75,0.35)');
  ctx.fillStyle = panelGrad;
  ctx.fill();
  ctx.save();
  ctx.strokeStyle = elementColor + '30';
  ctx.lineWidth = 1;
  roundRect(ctx, rightX - 8, pad, rightW + 8, panelH, 16);
  ctx.stroke();
  ctx.restore();

  let ry = pad + 32;

  // 2026 header
  const forecastYear = new Date().getFullYear();
  let palaceName = '';
  let rokuseiPhase = '';

  if (ns.year_cycle?.position?.palace) {
    palaceName = ns.year_cycle.position.palace;
  } else if (ns.nine_year_cycle) {
    const cur = ns.nine_year_cycle.find(e => e.current);
    if (cur) palaceName = cur.palace;
  }

  if (rk.twelve_year_cycle) {
    const cur = rk.twelve_year_cycle.find(e => e.current);
    if (cur) rokuseiPhase = cur.phase;
  }

  ctx.fillStyle = elementColor;
  ctx.font = '600 18px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`${forecastYear}年の運勢`, rightX + rightW / 2, ry);

  ry += 36;
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 28px "Noto Sans JP", Inter, sans-serif';
  const phaseText = [palaceName, rokuseiPhase].filter(Boolean).join(' × ');
  wrapText(ctx, phaseText || '運勢詳細はアプリで', rightX, ry, rightW, 36);
  ry += 72;

  // Peak Year
  let peakYear = forecastYear;
  let peakEnergy = 0;
  if (rk.twelve_year_cycle) {
    for (const entry of rk.twelve_year_cycle) {
      if (entry.energy > peakEnergy && entry.year >= forecastYear) {
        peakEnergy = entry.energy;
        peakYear = entry.year;
      }
    }
  }

  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '400 16px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`Peak Year: ${peakYear}`, rightX + rightW / 2, ry);

  ry += 36;

  // Separator
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(rightX + 16, ry);
  ctx.lineTo(rightX + rightW - 16, ry);
  ctx.stroke();
  ctx.restore();

  ry += 28;

  // Rarity badge
  if (isReigou) {
    roundRect(ctx, rightX, ry, rightW, 76, 10);
    const badgeGrad = ctx.createLinearGradient(rightX, ry, rightX + rightW, ry + 76);
    badgeGrad.addColorStop(0, 'rgba(201,168,76,0.22)');
    badgeGrad.addColorStop(1, 'rgba(234,179,8,0.08)');
    ctx.fillStyle = badgeGrad;
    ctx.fill();
    ctx.save();
    ctx.strokeStyle = 'rgba(201,168,76,0.5)';
    ctx.lineWidth = 1;
    roundRect(ctx, rightX, ry, rightW, 76, 10);
    ctx.stroke();
    ctx.restore();

    ctx.fillStyle = '#fde68a';
    ctx.font = '600 18px "Noto Sans JP", Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('⭐ 霊合星人（全人口の10%）', rightX + rightW / 2, ry + 46);
    ry += 96;
  }

  // Five elements mini
  const elements = ['木','火','土','金','水'];
  const elColorMap = {
    '木': SC_ELEMENT_COLORS.Wood,
    '火': SC_ELEMENT_COLORS.Fire,
    '土': SC_ELEMENT_COLORS.Earth,
    '金': SC_ELEMENT_COLORS.Metal,
    '水': SC_ELEMENT_COLORS.Water,
  };
  const miniBarW = rightW - 32;
  const miniBarH = 8;

  elements.forEach(el => {
    const b = fp.five_elements_balance[el];
    const pct = b?.pct ?? 0;
    const fillW = Math.round(miniBarW * pct / 100);

    // Label + percent
    ctx.fillStyle = elColorMap[el];
    ctx.font = '500 14px "Noto Sans JP", Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`${el}`, rightX + 16, ry + 10);

    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '400 12px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${pct}%`, rightX + rightW - 16, ry + 10);

    // Track
    roundRect(ctx, rightX + 16, ry + 16, miniBarW, miniBarH, miniBarH / 2);
    ctx.fillStyle = 'rgba(255,255,255,0.07)';
    ctx.fill();

    // Fill
    if (fillW > 0) {
      roundRect(ctx, rightX + 16, ry + 16, fillW, miniBarH, miniBarH / 2);
      ctx.fillStyle = elColorMap[el];
      ctx.fill();
    }

    ry += 38;
  });

  // Bottom footer on right panel
  ry = h - pad - 32;
  ctx.fillStyle = 'rgba(255,255,255,0.25)';
  ctx.font = '400 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('selfinsight.app  ·  あなたも診断する →', rightX + rightW / 2, ry);
}

// ============================================================
// Main: generateShareCard
// ============================================================

/**
 * Generate a share card canvas.
 * @param {Object} profile - Profile from SelfInsightEngine.generateProfile()
 * @param {'story'|'ogp'} size - 'story' = 1080x1920, 'ogp' = 1200x675
 * @returns {HTMLCanvasElement}
 */
function generateShareCard(profile, size = 'story') {
  const canvas = document.createElement('canvas');
  const ctx    = canvas.getContext('2d');

  if (size === 'story') {
    canvas.width  = 1080;
    canvas.height = 1920;
    drawStoryCard(ctx, profile, canvas.width, canvas.height);
  } else {
    canvas.width  = 1200;
    canvas.height = 675;
    drawOgpCard(ctx, profile, canvas.width, canvas.height);
  }

  return canvas;
}

// ============================================================
// Export: downloadShareCard
// ============================================================

/**
 * Download the share card as a PNG file.
 * @param {Object} profile
 * @param {'story'|'ogp'} size
 */
async function downloadShareCard(profile, size = 'story') {
  await loadShareCardFonts();

  // Small delay to let fonts settle in canvas
  await new Promise(r => setTimeout(r, 100));

  const canvas = generateShareCard(profile, size);
  const filename = size === 'story'
    ? 'self-insight-story.png'
    : 'self-insight-ogp.png';

  canvas.toBlob(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }, 'image/png');
}

// ============================================================
// Export: getShareCardBlob (for Web Share API)
// ============================================================

/**
 * Get the share card as a Blob (for Web Share API).
 * @param {Object} profile
 * @param {'story'|'ogp'} size
 * @returns {Promise<Blob>}
 */
async function getShareCardBlob(profile, size = 'story') {
  await loadShareCardFonts();
  await new Promise(r => setTimeout(r, 100));

  const canvas = generateShareCard(profile, size);
  return new Promise((resolve, reject) => {
    canvas.toBlob(blob => {
      if (blob) resolve(blob);
      else reject(new Error('Canvas toBlob failed'));
    }, 'image/png');
  });
}

// ============================================================
// Export: showShareModal — opens a preview modal in the page
// ============================================================

async function showShareModal(profile) {
  await loadShareCardFonts();
  await new Promise(r => setTimeout(r, 100));

  // Remove existing modal
  const existing = document.getElementById('sc-modal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'sc-modal';
  modal.style.cssText = `
    position:fixed;inset:0;z-index:9999;
    background:rgba(0,0,0,0.88);
    display:flex;flex-direction:column;align-items:center;justify-content:flex-start;
    overflow-y:auto;padding:24px 16px 48px;
    backdrop-filter:blur(8px);
  `;

  // Close on backdrop click
  modal.addEventListener('click', e => {
    if (e.target === modal) modal.remove();
  });

  const inner = document.createElement('div');
  inner.style.cssText = `
    background:#1a1d27;border:1px solid #2e3347;border-radius:16px;
    padding:20px;max-width:540px;width:100%;
  `;

  // Header
  const header = document.createElement('div');
  header.style.cssText = `
    display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;
  `;
  header.innerHTML = `
    <span style="font-size:16px;font-weight:700;color:#e8e9ed;">結果をシェア</span>
    <button id="sc-close" style="background:none;border:none;color:#9ca3af;font-size:24px;cursor:pointer;line-height:1;">×</button>
  `;
  inner.appendChild(header);
  header.querySelector('#sc-close').onclick = () => modal.remove();

  // Tab bar
  const tabBar = document.createElement('div');
  tabBar.style.cssText = `
    display:flex;gap:8px;margin-bottom:16px;
  `;
  tabBar.innerHTML = `
    <button data-size="story" class="sc-tab sc-tab-active" style="
      flex:1;padding:10px;border-radius:8px;border:1px solid #6366f1;
      background:rgba(99,102,241,0.12);color:#a5b4fc;
      font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;
    ">IG Stories (縦)</button>
    <button data-size="ogp" class="sc-tab" style="
      flex:1;padding:10px;border-radius:8px;border:1px solid #2e3347;
      background:#242837;color:#9ca3af;
      font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;
    ">X / OGP (横)</button>
  `;
  inner.appendChild(tabBar);

  // Canvas preview container
  const previewWrap = document.createElement('div');
  previewWrap.style.cssText = `
    border-radius:10px;overflow:hidden;border:1px solid #2e3347;margin-bottom:16px;
    display:flex;align-items:center;justify-content:center;
    background:#0f1117;
  `;
  inner.appendChild(previewWrap);

  // Action buttons
  const actionBar = document.createElement('div');
  actionBar.style.cssText = `display:flex;gap:10px;`;
  actionBar.innerHTML = `
    <button id="sc-download" style="
      flex:1;padding:14px;border-radius:8px;border:none;
      background:#6366f1;color:#fff;
      font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;
    ">ダウンロード</button>
    <button id="sc-share-api" style="
      flex:1;padding:14px;border-radius:8px;border:1px solid #2e3347;
      background:#242837;color:#e8e9ed;
      font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;
      display:${navigator.share ? 'block' : 'none'};
    ">シェア</button>
  `;
  inner.appendChild(actionBar);

  // SNS share buttons (always visible, works on desktop)
  const shareText = encodeURIComponent('AI Self-Insightで占術×心理学の統合分析をしました！');
  const shareUrl = encodeURIComponent(location.origin + location.pathname);
  const snsBar = document.createElement('div');
  snsBar.style.cssText = `display:flex;gap:8px;margin-top:8px;`;
  const snsBtnStyle = `
    flex:1;padding:12px 8px;border-radius:8px;border:1px solid #2e3347;
    background:#242837;color:#e8e9ed;
    font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;
    display:flex;align-items:center;justify-content:center;gap:6px;
    transition:background 0.2s;
  `;
  snsBar.innerHTML = `
    <button class="sc-sns" data-platform="x" style="${snsBtnStyle}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      X
    </button>
    <button class="sc-sns" data-platform="line" style="${snsBtnStyle}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="#06C755"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg>
      LINE
    </button>
    <button class="sc-sns" data-platform="copy" style="${snsBtnStyle}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      コピー
    </button>
  `;
  inner.appendChild(snsBar);

  modal.appendChild(inner);
  document.body.appendChild(modal);

  let currentSize = 'story';

  function renderPreview(size) {
    previewWrap.innerHTML = '';
    const canvas = generateShareCard(profile, size);

    // Scale canvas to fit preview (max 500px wide)
    const maxW = Math.min(500, window.innerWidth - 64);
    const scale = maxW / canvas.width;
    canvas.style.width  = Math.round(canvas.width  * scale) + 'px';
    canvas.style.height = Math.round(canvas.height * scale) + 'px';
    canvas.style.display = 'block';
    previewWrap.appendChild(canvas);
  }

  // Tab switching
  tabBar.querySelectorAll('.sc-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      tabBar.querySelectorAll('.sc-tab').forEach(b => {
        b.style.borderColor = '#2e3347';
        b.style.background  = '#242837';
        b.style.color       = '#9ca3af';
      });
      btn.style.borderColor = '#6366f1';
      btn.style.background  = 'rgba(99,102,241,0.12)';
      btn.style.color       = '#a5b4fc';
      currentSize = btn.dataset.size;
      renderPreview(currentSize);
    });
  });

  // Download
  actionBar.querySelector('#sc-download').addEventListener('click', () => {
    downloadShareCard(profile, currentSize);
  });

  // Web Share API
  const shareApiBtn = actionBar.querySelector('#sc-share-api');
  if (shareApiBtn) {
    shareApiBtn.addEventListener('click', async () => {
      try {
        const blob = await getShareCardBlob(profile, currentSize);
        const file = new File([blob], 'self-insight.png', { type: 'image/png' });
        await navigator.share({
          title: 'AI Self-Insight — 私のパーソナル分析',
          text: 'AI Self-Insightで占術×心理学の統合分析をしました！',
          files: [file],
        });
      } catch (e) {
        if (e.name !== 'AbortError') {
          alert('シェアに失敗しました。ダウンロードしてSNSに投稿してください。');
        }
      }
    });
  }

  // SNS platform share handlers
  snsBar.querySelectorAll('.sc-sns').forEach(btn => {
    btn.addEventListener('mouseenter', () => { btn.style.background = '#2e3347'; });
    btn.addEventListener('mouseleave', () => { btn.style.background = '#242837'; });
    btn.addEventListener('click', () => {
      const platform = btn.dataset.platform;
      const pageUrl = location.origin + location.pathname;
      const text = 'AI Self-Insightで占術×心理学の統合分析をしました！';
      if (platform === 'x') {
        window.open(`https://x.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(pageUrl)}`, '_blank');
      } else if (platform === 'line') {
        window.open(`https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(pageUrl)}&text=${encodeURIComponent(text)}`, '_blank');
      } else if (platform === 'copy') {
        navigator.clipboard.writeText(`${text}\n${pageUrl}`).then(() => {
          btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> コピー済み`;
          setTimeout(() => {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> コピー`;
          }, 2000);
        });
      }
    });
  });

  renderPreview(currentSize);
}

// Expose to window
if (typeof window !== 'undefined') {
  window.SelfInsightShareCard = {
    generateShareCard,
    downloadShareCard,
    getShareCardBlob,
    showShareModal,
  };
}
