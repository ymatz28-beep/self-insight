/**
 * Self-Insight Calculation Engine
 * Port of generate_profile.py — all divination + personality scoring in pure JS
 * No external dependencies.
 */

// ============================================================
// Constants
// ============================================================

const HEAVENLY_STEMS = '甲乙丙丁戊己庚辛壬癸'.split('');
const EARTHLY_BRANCHES = '子丑寅卯辰巳午未申酉戌亥'.split('');

const STEM_READINGS = [
  'きのえ','きのと','ひのえ','ひのと','つちのえ',
  'つちのと','かのえ','かのと','みずのえ','みずのと',
];
const BRANCH_READINGS = [
  'ね','うし','とら','う','たつ','み',
  'うま','ひつじ','さる','とり','いぬ','い',
];
const BRANCH_ANIMALS = [
  'Rat','Ox','Tiger','Rabbit','Dragon','Snake',
  'Horse','Goat','Monkey','Rooster','Dog','Pig',
];

const STEM_ELEMENTS = ['Wood','Wood','Fire','Fire','Earth','Earth','Metal','Metal','Water','Water'];
const STEM_YINYANG = ['Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin','Yang','Yin'];
const BRANCH_ELEMENTS = ['Water','Earth','Wood','Wood','Earth','Fire','Fire','Earth','Metal','Metal','Earth','Water'];

const ELEMENT_JP = { Wood:'木', Fire:'火', Earth:'土', Metal:'金', Water:'水' };

const SOLAR_MONTH_BRANCH = { 2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10,11:11,12:0,1:1 };

const NINE_STAR_NAMES = {
  1:'一白水星',2:'二黒土星',3:'三碧木星',4:'四緑木星',
  5:'五黄土星',6:'六白金星',7:'七赤金星',8:'八白土星',9:'九紫火星',
};
const NINE_STAR_ELEMENTS = {1:'Water',2:'Earth',3:'Wood',4:'Wood',5:'Earth',6:'Metal',7:'Metal',8:'Earth',9:'Fire'};
const NINE_STAR_DIRECTIONS = {1:'N',2:'SW',3:'E',4:'SE',5:'C',6:'NW',7:'W',8:'NE',9:'S'};

const MONTH_STAR_TABLE = {
  A: [8,7,6,5,4,3,2,1,9,8,7,6],
  B: [2,1,9,8,7,6,5,4,3,2,1,9],
  C: [5,4,3,2,1,9,8,7,6,5,4,3],
};

const PALACE_NAMES = {1:'坎宮',2:'坤宮',3:'震宮',4:'巽宮',5:'中宮',6:'乾宮',7:'兌宮',8:'艮宮',9:'離宮'};
const PALACE_DIRECTIONS = {1:'N',2:'SW',3:'E',4:'SE',5:'C',6:'NW',7:'W',8:'NE',9:'S'};
const PALACE_THEMES = {
  1:'厄・試練',2:'変化・準備',3:'発展・始動',4:'整備・信用',5:'絶頂・転機',
  6:'充実・実り',7:'悦び・収穫',8:'停滞・自己改革',9:'注目・離別',
};
const PALACE_ENERGY = {1:30,2:45,3:65,4:75,5:100,6:90,7:80,8:40,9:70};

// Rokusei
const ROKUSEI_STARS = {1:'土星人',2:'金星人',3:'火星人',4:'天王星人',5:'木星人',6:'水星人'};
const ROKUSEI_SUB_MAP = {
  '土星人':'天王星人','金星人':'木星人','火星人':'水星人',
  '天王星人':'土星人','木星人':'金星人','水星人':'火星人',
};
const ROKUSEI_REIGOU_BRANCH = {
  '土星人':{'+':'戌','-':'亥'},'金星人':{'+':'申','-':'酉'},
  '火星人':{'+':'午','-':'未'},'天王星人':{'+':'辰','-':'巳'},
  '木星人':{'+':'寅','-':'卯'},'水星人':{'+':'子','-':'丑'},
};
const ROKUSEI_PHASES = ['種子','緑生','立花','健弱','達成','乱気','再会','財成','安定','陰影','停止','減退'];
const ROKUSEI_PHASE_SATSUKAI = {'陰影':'大殺界','停止':'大殺界','減退':'大殺界','健弱':'小殺界','乱気':'中殺界'};
const ROKUSEI_PHASE_ENERGY = {
  '種子':50,'緑生':65,'立花':80,'健弱':35,'達成':90,'乱気':25,
  '再会':70,'財成':85,'安定':95,'陰影':15,'停止':10,'減退':20,
};
const ROKUSEI_SEED_YEARS = {
  '土星人':{'+':2018,'-':2019},'金星人':{'+':2020,'-':2019},
  '火星人':{'+':2022,'-':2023},'天王星人':{'+':2016,'-':2017},
  '木星人':{'+':2014,'-':2025},'水星人':{'+':2016,'-':2015},
};
const ROKUSEI_PHASE_TYPE = {
  '立花':'great','達成':'great','安定':'great','財成':'great',
  '種子':'good','緑生':'good','再会':'good',
  '健弱':'caution','乱気':'caution',
  '陰影':'danger','停止':'danger','減退':'danger',
};

// Western astrology
const WESTERN_SIGNS = [
  {sign:'Aries',symbol:'♈',element:'Fire',quality:'Cardinal',ruler:'Mars',start:[3,21],end:[4,19],jp:'牡羊座'},
  {sign:'Taurus',symbol:'♉',element:'Earth',quality:'Fixed',ruler:'Venus',start:[4,20],end:[5,20],jp:'牡牛座'},
  {sign:'Gemini',symbol:'♊',element:'Air',quality:'Mutable',ruler:'Mercury',start:[5,21],end:[6,20],jp:'双子座'},
  {sign:'Cancer',symbol:'♋',element:'Water',quality:'Cardinal',ruler:'Moon',start:[6,21],end:[7,22],jp:'蟹座'},
  {sign:'Leo',symbol:'♌',element:'Fire',quality:'Fixed',ruler:'Sun',start:[7,23],end:[8,22],jp:'獅子座'},
  {sign:'Virgo',symbol:'♍',element:'Earth',quality:'Mutable',ruler:'Mercury',start:[8,23],end:[9,22],jp:'乙女座'},
  {sign:'Libra',symbol:'♎',element:'Air',quality:'Cardinal',ruler:'Venus',start:[9,23],end:[10,22],jp:'天秤座'},
  {sign:'Scorpio',symbol:'♏',element:'Water',quality:'Fixed',ruler:'Pluto',start:[10,23],end:[11,21],jp:'蠍座'},
  {sign:'Sagittarius',symbol:'♐',element:'Fire',quality:'Mutable',ruler:'Jupiter',start:[11,22],end:[12,21],jp:'射手座'},
  {sign:'Capricorn',symbol:'♑',element:'Earth',quality:'Cardinal',ruler:'Saturn',start:[12,22],end:[1,19],jp:'山羊座'},
  {sign:'Aquarius',symbol:'♒',element:'Air',quality:'Fixed',ruler:'Uranus',start:[1,20],end:[2,18],jp:'水瓶座'},
  {sign:'Pisces',symbol:'♓',element:'Water',quality:'Mutable',ruler:'Neptune',start:[2,19],end:[3,20],jp:'魚座'},
];

// Blood type
const BLOOD_TYPE_DATA = {
  A: {pct:40, strengths:['真面目で責任感が強い','計画性がある','協調性が高い','几帳面'], challenges:['心配性','融通が利かない','ストレスを溜めやすい']},
  B: {pct:20, strengths:['マイペース','好奇心旺盛','柔軟な発想','行動力がある'], challenges:['飽きっぽい','集中にムラがある','周囲と歩調を合わせにくい']},
  O: {pct:30, strengths:['おおらか','リーダーシップ','社交的','大胆な決断力'], challenges:['大雑把','頑固','感情的になりやすい']},
  AB:{pct:10, strengths:['合理的思考と感性の共存','冷静な分析力','多角的視点','適応力'], challenges:['二面性による迷い','感情の複雑さ','他者から理解されにくい']},
};

// Enneagram
const ENNEAGRAM_NAMES = {
  1:'完璧主義者',2:'援助者',3:'達成者',4:'個性派',5:'観察者',
  6:'忠実家',7:'楽天家',8:'挑戦者',9:'調停者',
};
const ENNEAGRAM_DESCRIPTIONS = {
  1:'原則と改善への情熱。正しさと秩序を求める',
  2:'人への奉仕と愛情。他者のニーズを察知する',
  3:'達成と成功への邁進。効率と実績を重視',
  4:'自己表現とアイデンティティの探求。深い感情と独自性',
  5:'知識と理解への探求。観察と分析を重視',
  6:'安全と所属への希求。忠誠心と慎重さ',
  7:'自由と楽しさの追求。可能性と多様な体験',
  8:'力と自律への追求。正義感と決断力',
  9:'平和と調和の希求。包容力と安定',
};
const ENNEAGRAM_GROWTH = {1:7,2:4,3:6,4:1,5:8,6:9,7:5,8:2,9:3};
const ENNEAGRAM_STRESS = {1:4,2:8,3:9,4:2,5:7,6:3,7:1,8:5,9:6};

// Big Five Mini-IPIP: [itemIndex(0-based), isReverse]
const BIG_FIVE_ITEMS = {
  Extraversion: [[0,false],[5,true],[10,false],[15,true]],
  Agreeableness: [[1,true],[6,false],[11,true],[16,false]],
  Conscientiousness: [[2,false],[7,true],[12,false],[17,true]],
  Neuroticism: [[3,false],[8,true],[13,false],[18,true]],
  Openness: [[4,false],[9,true],[14,false],[19,true]],
};

const ASRS_THRESHOLDS = [2,2,2,2,3,3];

// Day master descriptions
const DM_DESCRIPTIONS = {
  'Wood_Yang':'陽木 — 大樹。真っ直ぐに伸びる力強さ',
  'Wood_Yin':'陰木 — 草花。柔軟でしなやか',
  'Fire_Yang':'陽火 — 太陽。明るく力強い照射',
  'Fire_Yin':'陰火 — ロウソクの炎。静かで温かく、人を照らす',
  'Earth_Yang':'陽土 — 山。安定感と包容力',
  'Earth_Yin':'陰土 — 田畑。育て受け入れる力',
  'Metal_Yang':'陽金 — 刀剣。鋭い決断力',
  'Metal_Yin':'陰金 — 宝石。洗練された美しさ',
  'Water_Yang':'陽水 — 大海。広大な知恵と包容力',
  'Water_Yin':'陰水 — 雨露。繊細で浸透する力',
};


// ============================================================
// Date Utilities
// ============================================================

function julianDayNumber(year, month, day) {
  const a = Math.floor((14 - month) / 12);
  const y = year + 4800 - a;
  const m = month + 12 * a - 3;
  return day + Math.floor((153 * m + 2) / 5) + 365 * y
    + Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
}

function isBeforeRisshun(month, day) {
  return month < 2 || (month === 2 && day < 4);
}

function solarYear(year, month, day) {
  return isBeforeRisshun(month, day) ? year - 1 : year;
}


// ============================================================
// Four Pillars (四柱推命)
// ============================================================

function makePillar(stemIdx, branchIdx) {
  return {
    stem: {
      char: HEAVENLY_STEMS[stemIdx],
      element: STEM_ELEMENTS[stemIdx],
      yin_yang: STEM_YINYANG[stemIdx],
      reading: STEM_READINGS[stemIdx],
    },
    branch: {
      char: EARTHLY_BRANCHES[branchIdx],
      animal: BRANCH_ANIMALS[branchIdx],
      element: BRANCH_ELEMENTS[branchIdx],
      reading: BRANCH_READINGS[branchIdx],
    },
    full: HEAVENLY_STEMS[stemIdx] + EARTHLY_BRANCHES[branchIdx],
  };
}

function calcYearPillar(year, month, day) {
  const sy = solarYear(year, month, day);
  return makePillar(((sy - 4) % 10 + 10) % 10, ((sy - 4) % 12 + 12) % 12);
}

function calcMonthPillar(year, month, day) {
  const sy = solarYear(year, month, day);
  const yearStemIdx = ((sy - 4) % 10 + 10) % 10;
  const monthBranchIdx = SOLAR_MONTH_BRANCH[month];
  const monthStemIdx = (yearStemIdx * 2 + monthBranchIdx) % 10;
  return makePillar(monthStemIdx, monthBranchIdx);
}

function calcDayPillar(year, month, day) {
  const jdn = julianDayNumber(year, month, day);
  const cycleIdx = ((jdn + 49) % 60 + 60) % 60;
  return makePillar(cycleIdx % 10, cycleIdx % 12);
}

function calcFiveElements(pillars) {
  const sources = {'木':[],'火':[],'土':[],'金':[],'水':[]};
  const labels = ['年','月','日'];
  pillars.forEach((p, i) => {
    const stemEl = ELEMENT_JP[p.stem.element];
    const branchEl = ELEMENT_JP[p.branch.element];
    sources[stemEl].push(`${p.stem.char}(${labels[i]}干)`);
    sources[branchEl].push(`${p.branch.char}(${labels[i]}支)`);
  });

  const total = Object.values(sources).reduce((s, arr) => s + arr.length, 0);
  const balance = {};
  const missing = [];
  for (const el of ['木','火','土','金','水']) {
    const count = sources[el].length;
    balance[el] = {
      count,
      pct: total > 0 ? Math.round(count / total * 100) : 0,
      source: count > 0 ? sources[el].join('+') : 'なし（時柱で補完の可能性）',
    };
    if (count === 0) missing.push(el);
  }
  return { balance, missing };
}

function calcFourPillars(year, month, day) {
  const yp = calcYearPillar(year, month, day);
  const mp = calcMonthPillar(year, month, day);
  const dp = calcDayPillar(year, month, day);
  const { balance, missing } = calcFiveElements([yp, mp, dp]);

  const dmEl = dp.stem.element;
  const dmYY = dp.stem.yin_yang;
  const elMeanings = {'木':'成長力・発展','火':'情熱・行動力','土':'安定・信頼','金':'決断力・収穫','水':'知恵・柔軟性'};

  let insight;
  if (missing.length) {
    insight = missing.map(el => `${el}(${elMeanings[el]})`).join('と') + 'が欠如。意識的にこれらの要素を補う行動が有効';
  } else {
    insight = '五行がバランス良く分布。総合力が高い';
  }

  return {
    year_pillar: yp, month_pillar: mp, day_pillar: dp, hour_pillar: null,
    day_master: {
      char: dp.stem.char, element: dmEl, yin_yang: dmYY,
      description: DM_DESCRIPTIONS[`${dmEl}_${dmYY}`] || '',
    },
    five_elements_balance: balance, missing_elements: missing, element_insight: insight,
  };
}


// ============================================================
// Nine Star Ki (九星気学)
// ============================================================

function digitSumReduce(n) {
  while (n >= 10) { n = String(n).split('').reduce((s, d) => s + Number(d), 0); }
  return n;
}

function calcNineStarYear(year, month, day) {
  const sy = solarYear(year, month, day);
  const ds = digitSumReduce(sy);
  let star = 11 - ds;
  if (star <= 0) star += 9;
  if (star > 9) star -= 9;
  return star;
}

function calcNineStarMonth(year, month, day) {
  const yearStar = calcNineStarYear(year, month, day);
  const group = [1,4,7].includes(yearStar) ? 'A' : [2,5,8].includes(yearStar) ? 'B' : 'C';
  const monthIdx = isBeforeRisshun(month, day) ? 11 : ((month - 2) % 12 + 12) % 12;
  return MONTH_STAR_TABLE[group][monthIdx];
}

function calcPalacePosition(personStar, centerStar) {
  const offset = centerStar - 5;
  return ((personStar - offset - 1) % 9 + 9) % 9 + 1;
}

function calcNineStarKi(year, month, day, forecastYear) {
  const yearStar = calcNineStarYear(year, month, day);
  const monthStar = calcNineStarMonth(year, month, day);

  const result = {
    year_star: { number: yearStar, name: NINE_STAR_NAMES[yearStar], element: NINE_STAR_ELEMENTS[yearStar], direction: NINE_STAR_DIRECTIONS[yearStar] },
    month_star: { number: monthStar, name: NINE_STAR_NAMES[monthStar], element: NINE_STAR_ELEMENTS[monthStar], direction: NINE_STAR_DIRECTIONS[monthStar] },
  };

  if (forecastYear) {
    const centerStar = calcNineStarYear(forecastYear, 6, 1);
    const palaceNum = calcPalacePosition(yearStar, centerStar);
    result.year_cycle = {
      center_star: { number: centerStar, name: NINE_STAR_NAMES[centerStar] },
      position: { palace: PALACE_NAMES[palaceNum], direction: PALACE_DIRECTIONS[palaceNum], meaning: PALACE_THEMES[palaceNum] },
    };
    result.nine_year_cycle = [];
    for (let offset = -2; offset <= 6; offset++) {
      const yr = forecastYear + offset;
      const cs = calcNineStarYear(yr, 6, 1);
      const pn = calcPalacePosition(yearStar, cs);
      const entry = { year: yr, palace: PALACE_NAMES[pn], theme: PALACE_THEMES[pn], energy: PALACE_ENERGY[pn] };
      if (yr === forecastYear) entry.current = true;
      result.nine_year_cycle.push(entry);
    }
  }

  return result;
}


// ============================================================
// Rokusei Senjutsu (六星占術)
// ============================================================

function rokuseiFateNumber(year, month) {
  const jdn = julianDayNumber(year, month, 1);
  return ((jdn + 49) % 60 + 60) % 60 + 1;
}

function rokuseiStarNumber(year, month, day) {
  let sn = (rokuseiFateNumber(year, month) - 1) + day;
  if (sn >= 61) sn -= 60;
  return sn;
}

function rokuseiStarType(starNumber) {
  const idx = Math.floor((starNumber - 1) / 10) + 1;
  return ROKUSEI_STARS[idx];
}

function rokuseiPolarity(year) {
  const branchIdx = ((year - 4) % 12 + 12) % 12;
  return branchIdx % 2 === 0 ? '+' : '-';
}

function rokuseiCheckReigou(star, polarity, year) {
  const branchIdx = ((year - 4) % 12 + 12) % 12;
  const branchChar = EARTHLY_BRANCHES[branchIdx];
  return branchChar === ROKUSEI_REIGOU_BRANCH[star]?.[polarity];
}

function rokuseiFindSeedYear(star, polarity, refYear) {
  const base = ROKUSEI_SEED_YEARS[star]?.[polarity] || 2020;
  const diff = ((refYear - base) % 12 + 12) % 12;
  return refYear - diff;
}

function rokuseiPhaseForYear(seedYear, targetYear) {
  const idx = ((targetYear - seedYear) % 12 + 12) % 12;
  return ROKUSEI_PHASES[idx];
}

function buildRokuseiCycle(star, polarity, forecastYear) {
  const seed = rokuseiFindSeedYear(star, polarity, forecastYear);
  const cycle = [];
  for (let offset = -2; offset <= 7; offset++) {
    const yr = forecastYear + offset;
    const phase = rokuseiPhaseForYear(seed, yr);
    const satsukai = ROKUSEI_PHASE_SATSUKAI[phase] || null;
    const entry = { year: yr, phase, '殺界': satsukai, energy: ROKUSEI_PHASE_ENERGY[phase] };
    if (yr === forecastYear) entry.current = true;
    cycle.push(entry);
  }
  return cycle;
}

function calcRokusei(year, month, day, forecastYear) {
  const sn = rokuseiStarNumber(year, month, day);
  const star = rokuseiStarType(sn);
  const pol = rokuseiPolarity(year);
  const isReigou = rokuseiCheckReigou(star, pol, year);

  const result = {
    main_star: { name: star, polarity: pol },
    reigou: isReigou,
  };

  if (isReigou) {
    result.sub_star = { name: ROKUSEI_SUB_MAP[star], polarity: pol };
  }

  if (forecastYear) {
    result.twelve_year_cycle = buildRokuseiCycle(star, pol, forecastYear);
    if (isReigou) {
      const sub = ROKUSEI_SUB_MAP[star];
      result.sub_star_cycle = buildRokuseiCycle(sub, pol, forecastYear);
      result.reigou_combined = result.twelve_year_cycle.map((mc, i) => {
        const sc = result.sub_star_cycle[i];
        const score = Math.round(mc.energy * 0.7 + sc.energy * 0.3);
        let label = '好調';
        if (score >= 90) label = '最高潮';
        else if (score >= 78) label = '絶好調';
        else if (score >= 65) label = '好調';
        else if (score >= 50) label = '回復開始';
        else if (score >= 35) label = '要注意';
        else if (score >= 20) label = '危険期';
        else label = '最悪期';
        if ((mc.energy >= 70 && sc.energy <= 25) || (mc.energy <= 25 && sc.energy >= 70)) label = '矛盾期';
        return { year: mc.year, score, label };
      });
    }
  }

  return result;
}


// ============================================================
// Western Astrology
// ============================================================

function calcWesternAstrology(month, day) {
  let found = WESTERN_SIGNS[0];
  for (const sd of WESTERN_SIGNS) {
    const [sm, sDd] = sd.start;
    const [em, ed] = sd.end;
    if (sm === em) {
      if (month === sm && day >= sDd && day <= ed) { found = sd; break; }
    } else if (sm > em) {
      if ((month === sm && day >= sDd) || (month === em && day <= ed)) { found = sd; break; }
    } else {
      if ((month === sm && day >= sDd) || (month === em && day <= ed)) { found = sd; break; }
    }
  }
  return {
    sun_sign: { sign: found.sign, symbol: found.symbol, element: found.element, quality: found.quality, jp: found.jp },
    ruling_planet: found.ruler,
  };
}


// ============================================================
// Personality Scoring
// ============================================================

function calcEnneagram(top3, wingStr, stressVal) {
  if (!top3 || top3.length < 1) return null;
  const primary = top3[0];
  let wing = null;
  if (wingStr && wingStr.includes('w')) {
    wing = parseInt(wingStr.split('w')[1]);
  }
  return {
    type: primary, name: ENNEAGRAM_NAMES[primary], description: ENNEAGRAM_DESCRIPTIONS[primary],
    wing, growth_direction: ENNEAGRAM_GROWTH[primary], stress_direction: ENNEAGRAM_STRESS[primary],
  };
}

function calcHSP(answers) {
  if (!answers || answers.length !== 6) return null;
  const total = answers.reduce((s, v) => s + v, 0);
  const level = total <= 12 ? 'low' : total <= 20 ? 'medium' : 'high';
  return {
    score: level, total, max: 30,
    subscales: { sensory: answers[0]+answers[1], emotional: answers[2]+answers[3], social: answers[4]+answers[5] },
  };
}

function calcADHD(answers) {
  if (!answers || answers.length !== 6) return null;
  const aboveCount = answers.filter((s, i) => s >= ASRS_THRESHOLDS[i]).length;
  const tendency = aboveCount >= 4 ? 'significant' : aboveCount >= 2 ? 'leaning' : 'minimal';
  return { tendency, above_threshold_count: aboveCount, total_items: 6 };
}

function calcBigFive(answers) {
  if (!answers || answers.length !== 20) return null;
  const factors = {};
  for (const [factor, items] of Object.entries(BIG_FIVE_ITEMS)) {
    factors[factor] = items.reduce((sum, [idx, isReverse]) => {
      const raw = answers[idx];
      return sum + (isReverse ? 6 - raw : raw);
    }, 0);
  }
  const ei = factors.Extraversion >= 12 ? 'E' : 'I';
  const sn = factors.Openness >= 12 ? 'N' : 'S';
  const tf = factors.Agreeableness >= 12 ? 'F' : 'T';
  const jp = factors.Conscientiousness >= 12 ? 'J' : 'P';
  return { ocean: factors, mbti_equivalent: `${ei}${sn}${tf}${jp}` };
}


// ============================================================
// Monthly Fortune
// ============================================================

const NINE_STAR_NOTE_MAP = [[90,'大吉・最盛'],[80,'大吉・好調'],[70,'上昇運'],[60,'中吉・回復'],[50,'小吉・転換'],[40,'吉凶混合'],[25,'中凶・注意'],[0,'大凶']];

function nineStarNote(energy) {
  for (const [threshold, note] of NINE_STAR_NOTE_MAP) {
    if (energy >= threshold) return note;
  }
  return '大凶';
}

function domainStars(combined, rokuseiPhase, rokuseiSatsukai) {
  let work = combined >= 81 ? 5 : combined >= 61 ? 4 : combined >= 41 ? 3 : combined >= 21 ? 2 : 1;
  let money = work;
  if (rokuseiSatsukai) money = Math.max(1, money - 1);
  let health = work;
  if (rokuseiPhase === '健弱') health = Math.max(1, health - 1);
  if (combined < 30) health = Math.max(1, health - 1);
  let romance = combined >= 85 ? 5 : combined >= 65 ? 4 : combined >= 45 ? 3 : combined >= 25 ? 2 : 1;
  return { work, money, health, romance };
}

function calcMonthlyFortune(personYearStar, rokuseiData, forecastYear) {
  const forecastCenterStar = calcNineStarYear(forecastYear, 6, 1);
  const prevCenterStar = calcNineStarYear(forecastYear - 1, 6, 1);
  const forecastGroup = [1,4,7].includes(forecastCenterStar) ? 'A' : [2,5,8].includes(forecastCenterStar) ? 'B' : 'C';
  const prevGroup = [1,4,7].includes(prevCenterStar) ? 'A' : [2,5,8].includes(prevCenterStar) ? 'B' : 'C';

  let yearlyPhaseIndex = 0;
  const twelveCycle = rokuseiData.twelve_year_cycle || [];
  for (const entry of twelveCycle) {
    if (entry.current) {
      yearlyPhaseIndex = ROKUSEI_PHASES.indexOf(entry.phase);
      break;
    }
  }

  const monthly = [];
  for (let m = 1; m <= 12; m++) {
    let monthIdx, group, centerStar;
    if (m === 1) {
      monthIdx = 11; group = prevGroup; centerStar = prevCenterStar;
    } else {
      monthIdx = ((m - 2) % 12 + 12) % 12; group = forecastGroup; centerStar = forecastCenterStar;
    }

    const monthlyCenterStar = MONTH_STAR_TABLE[group][monthIdx];
    const palaceNum = calcPalacePosition(personYearStar, monthlyCenterStar);
    const nsEnergy = PALACE_ENERGY[palaceNum];
    const nsNote = nineStarNote(nsEnergy);

    const rkIdx = (yearlyPhaseIndex + 6 + m) % 12;
    const rkPhase = ROKUSEI_PHASES[rkIdx];
    const rkSatsukai = ROKUSEI_PHASE_SATSUKAI[rkPhase] || null;
    const rkEnergy = ROKUSEI_PHASE_ENERGY[rkPhase];
    const rkType = ROKUSEI_PHASE_TYPE[rkPhase];

    const combined = (nsEnergy + rkEnergy) / 2;
    const domains = domainStars(combined, rkPhase, rkSatsukai);

    monthly.push({
      month: m,
      nine_star: { palace: PALACE_NAMES[palaceNum], energy: nsEnergy, note: nsNote },
      rokusei: { phase: rkPhase, satsukai: rkSatsukai, energy: rkEnergy, type: rkType },
      domains,
    });
  }
  return monthly;
}


// ============================================================
// Main Profile Generator
// ============================================================

function generateProfile(formData) {
  const { identity, enneagram: enneaData, hsp: hspAnswers, adhd: adhdAnswers, big_five: bfAnswers, existing } = formData;
  const tier = formData.tier || 1;
  const [year, month, day] = identity.birth_date.split('-').map(Number);
  const forecastYear = new Date().getFullYear();

  const today = new Date();
  let age = forecastYear - year;
  if (month > today.getMonth() + 1 || (month === today.getMonth() + 1 && day > today.getDate())) age--;

  const profile = {
    identity: {
      name: identity.display_name,
      birth_date: identity.birth_date,
      birth_time: identity.birth_time || null,
      birth_place: identity.birth_place || null,
      blood_type: (identity.blood_type || '').toUpperCase(),
      age,
      sex: identity.sex || null,
    },
    personality: {},
    four_pillars: calcFourPillars(year, month, day),
    nine_star_ki: calcNineStarKi(year, month, day, forecastYear),
    rokusei: calcRokusei(year, month, day, forecastYear),
    western_astrology: calcWesternAstrology(month, day),
    blood_type: { type: identity.blood_type, ...(BLOOD_TYPE_DATA[identity.blood_type?.toUpperCase()] || {}) },
  };

  // Tier 2
  if (tier >= 2) {
    if (enneaData?.top3) {
      profile.personality.enneagram = calcEnneagram(enneaData.top3, enneaData.wing, enneaData.stress);
    }
    if (hspAnswers) profile.personality.hsp = calcHSP(hspAnswers);
    if (adhdAnswers) profile.personality.adhd = calcADHD(adhdAnswers);
  }

  // Tier 3
  if (tier >= 3 && bfAnswers) {
    const bf = calcBigFive(bfAnswers);
    if (bf) {
      profile.personality.big_five = bf.ocean;
      profile.personality.mbti = bf.mbti_equivalent;
    }
  }

  if (existing?.mbti) profile.personality.mbti = existing.mbti;

  // Monthly fortune
  profile.monthly_fortune = calcMonthlyFortune(
    profile.nine_star_ki.year_star.number,
    profile.rokusei,
    forecastYear,
  );

  return profile;
}

// Export for use in form
if (typeof window !== 'undefined') {
  window.SelfInsightEngine = { generateProfile };
}
