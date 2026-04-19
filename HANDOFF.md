# Self-Insight — HANDOFF

## [Constancy] 2026-04-19
- [WARN] structural_reform: generate_dashboard.py is 3584 lines (threshold: 800). Consider splitting.
- [WARN] gnav_consistency: Missing gnav link: Trading (/trading/)
- [WARN] post_change_testing: self-insight: 直近13時間以内に変更あり、テスト証跡なし（self-insight/.test_ok）

## Last Updated
2026-04-16 Session — 家族3名反映 + iuma-private/insight/ 統合 + 競合127件調査 + 占い師型トーン統一 Phase 1

## Completed (2026-04-16 Session — 大規模刷新)

### 家族ユーザー追加
- **data/users/shizuka/**: 手嶋 静（1944-09-25・AB型）Tier 1
- **data/users/ayako/**: 太田 亜也子（1978-05-26・A型・霊合星人）Tier 1
- **user_mapping.yaml**: shizuka=8c858d57 / ayako=11cf4757

### 配信アーキテクチャ確定
- 当初 `iuma-insight.pages.dev` を新規作成 → 越権として即削除
- 正式配置: **iuma-private.pages.dev/insight/users/{public_id}/**（self-insight プロジェクトの一環として統合）
- **stock-analyzer/scripts/deploy_private.py** に `build_insight()` 関数追加（`setup_dirs()` の subdir list に `"insight"` 追加、`build_insight()` で users/form/ を copytree、`main()` に呼び出し）

### Tier 1 ダッシュボード機能 大幅拡張
- **干支 × 血液型カード**: 12 動物アーキタイプ × 4 血液型のクロス narrative
- **5 体系整合マップ**: 内向⇄外向 / 安定⇄変化 / 思考⇄情動 の 3 軸で各体系の投票を可視化（どの体系がどちらに票を入れるか明記版）
- **強み × 裏返しの罠カード**: Gallup CliftonStrengths Shadow Side を日主×本命星で再現
- **クロスリファレンス・インサイト**: 多体系の一致点 + 普遍的二層構造（本命星×日主、干支×日主、血液型×欠五行、今年のフェーズ）+ 揺らぎ（内向日主×外向血液型、霊合星人、欠元素の構造的盲点）
- **希少性統計バー** → **Japan/World dual-geo 表示**（血液型 × 干支 × 日主 × 太陽星座 = 5,760 通り → 「X人に1人 = 日本に約 N 人 / 世界に約 M 人」）

### 希少性計算の誠実化
- 旧: "超レア"演出（バーナム効果）+ 計算 1 桁バグ
- 新: 事実ベース表示 + 出典明記（日本赤十字社: A 38.1/O 30.7/B 21.8/AB 9.4% / 総務省統計局 人口推計 1.238 億 / ARC 世界分布 O 46/A 31/B 16/AB 7% / UN WPP 81.5 億）
- 「実生活スケール換算」(トヨタ/新宿駅等)は **出典不正確・意味不明瞭として削除**

### 専門用語ガイド統合
- Hero 直下に `<details class="glossary-details">` で 11 主要用語（日主・本命星・運命星・霊合星人・太陽星座・五行・陰陽・干支・四柱推命・九星気学・六星占術）を折りたたみ表示
- 本文中の用語に `<abbr class="term">` 点線下線 + ホバー/タップ tooltip

### データ不整合6件修正
1. BT_NARRATIVE_LONG の "日本人口10%" 文法崩壊 → 正しい文に書き直し
2. クロスリファレンス narrative の DM_GIST 切り捨て `[:10]+'…'` 除去
3. Summary cards の `—` と `エニアグラム ?` → Tier 1 フォールバック追加
4. Core Essence / Strongest Axis / Duality / Watch Out 等の英語ラベル → 日本語化
5. `<div class="archetype-en">` を Tier 2 以上のみ表示に（母・妹の "The Deep Current" 等削除）
6. `essence_sub` の「献身と安定」が整合マップ軸「変化」と衝突 → 「母なる支える力」に変更

### 競合調査 127件（5チーム並列）
- **A 西洋占星術 25+**: Co-Star/CHANI/Pattern/Sanctuary/Nebula 等
- **B 東洋占術 25+**: 水晶玉子/動物占い/六星占術/ZAPPALLAS/MIROR 等
- **C 性格診断 25+**: 16Personalities/Enneagram/CliftonStrengths/Human Design 等
- **D ライフログ 25+**: Reflectly/Finch/Moodfit/Calm/Rosebud 等
- **E バイラル無料診断 25+**: BuzzFeed/エムグラム/姓名判断/ShindanMaker 等
- 合計 **127件** をダッシュボードに反映

### 占い師型 ③ トーン統一 Phase 1
- 選定理由: 7 候補文体（勝間型/中島聡型/占い師型/コーチング型/心理学レポート型/文学詩的/取扱説明書型/箇条書き）を比較。ユーザー判断で「③ 占い師型 → A 読者別切替」順で採用
- 置換対象: DM_NARRATIVE_LONG（10 干）/ NS_NARRATIVE（9 星）/ ROKUSEI_NARRATIVE（6 星）/ BT_NARRATIVE_LONG（4 型）/ ETO_PROFILES narrative（12 支）/ 統合インサイト 4 段落 / クロスリファレンス Agreement 6 件 + Tension 6 件 / 整合マップ verdict 3 分岐 / 強み×罠 intro + extras / 確度バッジ 4 箇所 / Hero synthesis
- 未適用（Phase 1.5 候補）: DM_GIST / ETO_GIST 短縮版 / DM_STRENGTHS / 整合マップ left_desc・right_desc / _generate_monthly_narrative / generate_compatibility.py

### 相性診断エンジン作成（未デプロイ）
- **generate_compatibility.py** 新規作成: 血液型マトリクス + 西洋占星術（元素×アスペクト）+ 四柱推命（日主五行×陰陽）+ 干支（三合/六合/冲）の Tier 1 4体系統合スコア
- 重み: bt 15% / 西洋 30% / 四柱推命 30% / 干支 25%
- Tier 2（エニアグラム/HSP/ADHD/24SF/16A）はプレースホルダ
- **実行・デプロイは未完**

### 切替タイミング決定
- A（読者別文体）への切替トリガー: ①フィードバック異議 ②β配布直前 ③多様性15人突破 ④有料化前
- β配布前 MUST: A 完成

## Next Actions（優先順）

1. **3 名フィードバック収集**（1 週間窓）: 母・妹・Yuma がそれぞれ読み、占い師型トーンの違和感・内容精度・UI を評価
2. **相性診断デプロイ**: generate_compatibility.py 動作確認 → 3 家族ペア（yuma↔shizuka, yuma↔ayako, shizuka↔ayako）生成 → `/insight/compat/{a}-{b}/` 配置 → 各個人ダッシュボードからリンク
3. **Phase 1.5 占い師型残し**: DM_GIST / ETO_GIST / DM_STRENGTHS / 月間 narrative / compatibility narrative
4. **16 Archetypes / 24 Strengths 自前開発**: 16P（NERIS）/ CliftonStrengths（Gallup）権利回避。VIA Character Strengths と Jungian Archetypes ベースで独自命名
5. **シェアカード自動生成**（Canvas/CSS）: アーキタイプ名+希少性+キャッチ+ロゴ。バイラル装置 #1
6. **A（読者別文体切替）実装**: profile.yaml に `tone_preference: fortune_teller / manual / report` 追加。generate_dashboard.py が切り替え
7. **Cloudflare Access 保護確認**: iuma-private で既に Yuma only。母・妹がアクセスするなら allowlist 追加必要（現状未確認）
8. **git commit + push**: 未コミット変更が大量（generate_dashboard.py 3500+行、generate_compatibility.py 新規、data/users/{shizuka,ayako}/）

## Key Decisions
- **配置**: self-insight プロジェクト内（iuma-private.pages.dev/insight/ 配下）。独立サイト化しない
- **希少性表示**: バーナム効果演出廃止、公式データ（日本赤十字・総務省・UN）ベースの事実表示のみ
- **トーン**: 占い師型③を一旦標準、フィードバック次第で読者別切替(A) へ。β配布前に A 完成必須
- **Tier 2 personality 自前開発**: 16P/SF は商標権利回避のため独自分類設計（VIA+Jungian ベース）

## Blockers
- generate_dashboard.py 3,500+ 行で肥大化（ファイル分割が必要。現在 [WARN]）
- 相性診断機能 generate_compatibility.py は作成済みだが未実行・未デプロイ
- 母・妹が iuma-private を見るなら Access 設定確認が必要
- Tier 2 用 16 Archetypes / 24 Strengths は未開発
- 占い師型 Phase 1.5（残ナラ）未完

## Environment
- **venv**: `.venv/` (python3.14, PyYAML, Jinja2)
- **Deploy staging**: `/tmp/iuma-private-project/public/insight/`
- **Deploy target**: `iuma-private.pages.dev/insight/` (Cloudflare Pages, main branch)
- **Legacy GH Pages**: `gh-pages` branch (ymatz28-beep/self-insight.git) — 旧配置として残存
- **Deploy flow**: `stock-analyzer/scripts/deploy_private.py` の `build_insight()` が users/ + form/ を copytree
- **CLI**:
  - Profile gen: `python3 generate_profile.py --name "名前" --birth-date "YYYY-MM-DD" --blood-type AB --output data/users/{name}/profile.yaml`
  - Dashboard gen: `python3 generate_dashboard.py --profile data/users/{name}/profile.yaml --output users/{pub_id}/index.html --tier 1|2 [--gnav]`
  - Compatibility gen (未テスト): `python3 generate_compatibility.py --a profile_a.yaml --b profile_b.yaml --output users/compat/{pair}/index.html`

## History (last 20)
- **2026-04-16 session**: 家族3名追加 + iuma-private/insight/ 統合 + 競合127件調査 + 占い師型トーン統一 Phase 1 + データ不整合6件修正 + 相性診断エンジン作成（未デプロイ）+ 専門用語ガイド + Japan/World dual-geo 希少性表示 + クロスリファレンス/整合マップ/強み罠/干支×血液型 カード追加
- **2026-04-09**: フォント修正+CSS変数化+gnav nav-more（未コミット）
- **2026-03-29**: renderer.js本番品質化 + story/share-card「取扱説明書」ブランディング（self-insight `e80268e`, Projects root `ed3dd9a`）

## Legacy History

## Completed (横断監査: フォント修正+CSS変数化+gnav nav-more 2026-04-09)
- **Before**: form/story.htmlの.essence-kanjiがfont-family `'Noto Sans JP',serif`（禁止フォールバック）。index.htmlに5箇所のハードコードカラー（#f87171, #4ade80×2, #9ca3af）。gnavが13項目フラット表示のまま（nav-more未適用）
- **After**: story.html serif→sans-serif修正。index.htmlの5色をCSS変数化（var(--red-light), var(--green-light)×3, var(--text-secondary)）。gnav nav-more overflow構造追加（Primary 5項目+⋯ドロップダウン8項目、Self-InsightはOverflowに配置）
- **Commits**: 未コミット

## Completed (renderer.js本番品質化 + story/share-card「取扱説明書」ブランディング 2026-03-29)
- **Before**: renderer.jsがMVP品質（辞書データ・ナラティブ・セクション引用句なし）。generate_dashboard.pyレベルの本番品質に未到達。story.htmlのブランド名が「AI Self-Insight」のままでスライドラベルが「SLIDE 1/5」等の番号表示。share-card.jsのSNS共有機能が限定的
- **After**: renderer.js +397行net（659ins/262del）。PALACE_DESC(九星9宮)+PHASE_DESC(六星12フェーズ)+DM_NARRATIVE(日主10パターン)+WESTERN_NARRATIVE+SECTION_QUOTES辞書を追加し、generate_dashboard.py同等の本番品質に到達。story.htmlブランド名を「あなたの取扱説明書」に変更+スライドラベルをセマンティック化（YOUR ESSENCE/FIVE ELEMENTS/DESTINY STARS等）。share-card.js +33行改善。generate_dashboard.py -28行クリーンアップ。計6ファイル変更（693ins/262del）
- **Commits**: self-insight `e80268e`, Projects root `ed3dd9a`（session recovery）

## Project Overview
複数の占術（四柱推命・九星気学・六星占術・西洋占星術・干支）+ 独自性格分析SIPS（Big Five基盤の16 Archetypes+24 Strengths+Sensitivity Score）を統合した、徹底的にパーソナライズされた自己理解ダッシュボードサービス。有料SaaS展開を目指す。

### Core Concept
- 「占い」ではなく「AI Self-Insight」— データ駆動のパーソナル・インサイト
- **2ピラー構造**: Pillar 1（Core Identity = 不変の人物像）+ Pillar 2（年間運勢 = 時期別フォーキャスト）
- **統合インサイト first**: 個別占術の結果より先に、全システムを統合した「あなたはこういう人」を提示
- 年間運気予測（九星気学×六星占術の運気カーブ重ね表示）+ **月間4ドメイン運勢**
- **過去の振り返り + 長期フォーキャスト**: 良い時・悪い時をフィーチャーし、具体的アクション提案

### Why（3つのWhy）
- **個人的Why**: 自分がユーザー1号。identity.mdの延長で自己理解を深化
- **市場的Why**: 占い市場997億円。「複数占術 × 心理学 × ダッシュボード可視化」の統合サービスは空白
- **タイミングWhy**: 生成AIで占術アルゴリズム化コストが激減。Co-Star（占星術×AI）が500万DL

### Phase Plan
- **Phase 0**: Yuma自身のダッシュボードとして構築（identity.mdの延長）✅ 完了
- **Phase 0→1移行**: パイプライン基盤構築（generate_profile.py + generate_dashboard.py + process_submission.py）+ UXオーバーホール ← 現在
- **Phase 1**: 友人5人にβテスト（無料）→ PMF検証
- **Phase 2**: 月額980円でローンチ

### Pipeline Architecture (v0.5)
```
入力 → generate_profile.py → profile.yaml → generate_dashboard.py → HTML
```
- **generate_profile.py** (1,130行): 生年月日+アンケート → 全占術・性格分析を自動計算 → profile.yaml出力
  - 四柱推命（年柱/月柱/日柱 + 五行バランス）、九星気学（本命星/月命星 + 9年サイクル）
  - 六星占術（運命星 + 霊合判定 + 12年サイクル + 霊合統合スコア）、西洋占星術（太陽星座）
  - 血液型特性、エニアグラム、HSP-6、ADHD ASRS-6、Mini-IPIP Big Five → MBTI換算
  - **3-Tier制**: Tier 1=生年月日のみ、Tier 2=+エニアグラム/HSP/ADHD、Tier 3=+Big Five/MBTI
  - CLI: `python3 generate_profile.py --name "名前" --birth-date "YYYY-MM-DD" --blood-type AB --output path`
- **generate_dashboard.py** (2,084行): profile.yaml → スタンドアロンHTML（Chart.js内蔵）— session #16フルリライト→#18-19で大幅拡張
  - Gnav+2ピラー骨格、月間運勢、Cross Analysis、CSS仕上げ全ステップ完了
  - リッチナラティブ自動生成（profile.yamlからテンプレート+ロジック）
  - 日本語翻訳+専門用語グロサリー、アクション提案（今月/年間テーマ/行動ブループリント）
  - Tier別機能ゲーティング（Tier 3未達セクションはblur+ロック表示）
  - 運気サイクルチャート（統合オーバーレイ1枚に集約）
  - Hub+Detail Architecture: 全セクションを折りたたみカード化（デフォルト閉）
  - アーキタイプシステム: 日主+TOP強み→動的アーキタイプ名生成（例: 静かな炎の共鳴者）
  - `--gnav`フラグ: 個人用のみ。クライアント向けはデフォルトOFF
  - `--no-gnav`フラグ: クライアント向けダッシュボードでiUMA Private navをスキップ
  - CLI: `python3 generate_dashboard.py --profile profile.yaml --output output.html --tier 2`
- **Python venv**: `.venv/` (python3.14, PyYAML)
- **process_submission.py** (155行): submission JSON → generate_profile.py → generate_dashboard.py の自動E2Eパイプライン
- **scripts/apps-script.gs** (61行): Google Apps Script Web App — フォームPOST → Google Sheets蓄積
- **ディレクトリ**: `data/users/`, `output/`, `form/`, `docs/`, `scripts/`, `users/` (Phase 1スキャフォールド)

### Dashboard IA (v0.5 — Hub Architecture)
```
1. Hero (アーキタイプ名 glow + tagline + particle animation + hub card shortcuts)
   - 動的アーキタイプ名 (day_master + top strength → 例: 静かな炎の共鳴者)
2. Hub Cards (全セクションへのショートカット、Section Nav廃止)
3. ★ あなたの本質 (= Core Identity, timeless — Pillar 1) [折りたたみカード]
   - 統合インサイト (6体系統合の人物像, 折りたたみ展開)
   - Summary cards (Core Essence / Strongest Axis / Duality / Watch Out)
4. Personality Profile [折りたたみカード]
   - Self-Insight Strengths TOP5 (tap展開)
   - Domain Distribution
   - Typology + レアリティバッジ
5. 占術プロファイル [折りたたみカード, アコーディオン]
   - 四柱推命 (デフォルト展開) / 九星気学 / 六星占術 / 西洋占星術
   - レアリティバッジ (霊合10%, 日主10%, 欠落五行コンボ)
6. ★ 2026年運勢 (Pillar 2) [折りたたみカード]
   - Year positioning + 統合運気カーブ + Year guidance cards
7. 月間運勢 (Jan-Dec) [折りたたみカード]
   - 当月パネルに「今月のガイダンス」統合
   - パーソナライズ助言 (SF TOP強み + 日主五行参照)
   - Domain color coding (blue/gold/green/pink)
8. ★ 才能×運命 (= Cross Analysis) [折りたたみカード]
9. Footer ("Self-Insight — Powered by AI × 東洋占術 × 心理学")
```
- 全セクション: Co-Star風evocative引用句、IntersectionObserver fade-in
- デフォルト全閉（Hub体験）、各カードtap/clickで展開

### Monthly Fortune Data Sources
- **九星気学 月運**: 八雲院データ（月別エネルギーレベル 0-100）
- **六星占術 月運**: hosokikazuko.com確認済み
  - 1月:安定, 2月:陰影(大殺界), 3月:停止(大殺界), 4月:減退(大殺界)
  - 5月:種子, 6月:緑生, 7月:立花, 8月:健弱(小殺界)
  - 9月:達成, 10月:乱気(中殺界), 11月:再会, 12月:財成

### Key Design Decisions
- **2ピラー構造**: Timeless Identity + Year-Specific Forecast の明確な分離
- **月間運勢4ドメイン**: 仕事/お金/健康/恋愛 — Co-Star/The Pattern型のドメイン分割
- 占術ロジックはLLM生成禁止。OSSライブラリ使用 + ユニットテスト必須
- ブランディング: 「占い」ではなく「パーソナル・インサイト」
- Phase 0はGitHub Pages。デプロイ基盤はPhase 1以降で検討
- **Edit分割方式**: セクション単位のEdit呼び出しが安定（フルリライトはタイムアウト）

### Lesson Learned
- **九星気学計算エラー**: LLMが定数を10ではなく11で記憶していた → OSSライブラリ必須
- **フルHTML一括リライトのハング**: 3セッション連続失敗 → Edit分割で解決（セッション#7で成功）
- **月運データの重要性**: 年運だけでは「今月どうすべきか」がわからない → 月間4ドメイン運勢を追加
- **Agent一括リライト禁止**: Agent Bがgenerate_dashboard.py書き換えで52分タイムアウト（session #12）。Edit分割方式+段階的強化が唯一の安定手法
- **Agentタイムアウト**: 大規模ファイル書き換えAgentが52分でタイムアウト。原因: index.html全体読み込み→分析→書き換えが重すぎる → 具体的な構造指示を与えるか、Edit分割で直接変更すべき

### Market Research Summary
- 占い市場: 997億円（2023年度、矢野経済研究所）
- Co-Star: 500万DL、UX参考（daily forecast + domain breakdown）
- The Pattern: テーマカード型、音声ナレーション、暗色UI
- 差別化: 複数占術×心理学×月間4ドメインダッシュボード可視化の統合サービスはゼロ

## Completed
- [x] 市場調査・競合分析（2026-03-19）
- [x] WWH分析（2026-03-19）
- [x] プロジェクト初期設計（2026-03-19）
- [x] Phase 0プロファイルデータ構築: profile.yaml（2026-03-19）
- [x] 九星気学計算修正: 八白土星→七赤金星（2026-03-19）
- [x] 六星占術データ調査・追加: 木星人(-) 霊合星 + 12年サイクル（2026-03-19）
- [x] **ダッシュボードv0.3 大規模リストラクチャ**（2026-03-20 session #7）
  - 2ピラー構造（Core Identity + 2026 Forecast）に再編
  - 月間運勢（1-12月、4ドメイン）追加 — インタラクティブ月セレクタ
  - 占術プロファイルを1セクションに統合（四柱推命/九星/六星/西洋）
  - 年間運気カーブ（3線）をPillar 2に移動
  - 年タイムラインバー（色分け）追加
  - ナビ更新（6セクション）
- [x] **v0.4 デザインシステム準拠 + コンテンツ増量**（2026-03-20 session #8）
  - Gnav追加（`<header class="site-header">` — 全Privateダッシュボード共通、ハンバーガーメニュー付き）
  - Section Nav修正: `top: 52px`（Gnav下配置）、背景fill方式に変更
  - `--bg` 統一: `#050507` → `#0f1117`（他ダッシュボードと統一）
  - デザイントークン追加: `--gnav-height`, `--z-nav`, `--z-subnav`
  - Core Identity: 4段落目「弱点と成長領域」追加
  - Personality Profile: CliftonStrengths解説追加、TOP5各資質に実践的説明追加、Typology行動文脈追加
  - 占術プロファイル: 各柱の意味解説、九星二層構造深掘り、霊合星人概念詳説、Pluto解釈追加
  - 2026年運勢: 大殺界歴史的文脈追加、「2026年のキーワード」5項目追加、Guidance Cards 3→5項目、恋愛カード追加
  - 月間運勢: 全12ヶ月の4ドメインテキスト2-3行に拡充、月間インサイト3-4行に拡充
  - Cross Analysis: 全5ボックスを2段落化（分析+実践ガイド）
  - Cloudflare Pages（iuma-private.pages.dev/insight/）にデプロイ → 後にGitHub Pagesに切替
- [x] **クロスダッシュボードgnav QA & 修正**（2026-03-20 session #8）
  - Self-InsightリンクURL修正（Cloudflare→GitHub Pages）
  - Health リンク欠落を追加
  - 全ダッシュボードのgnav統一（7ファイル更新: renderer.py×3, self-insight, wealth-strategy×3, iuma-hub）
  - iuma-hubの5リンク欠落修正（Market Intel, Insight, Self-Insight, Health, Travel）
  - wealth-strategyのラベル修正（Intel→Insight）+ nav順序統一
  - GitHub Pagesデプロイ（`bcfd199`）
- [x] **gnav整合性チェック自動化**（2026-03-20 session #8）
  - `check_gnav_consistency` を constancy_checks.py に実装
  - config.yamlにハードコードgnavファイル5件を宣言
  - renderer.pyのSSoTと比較: リンク欠落/余分/順序ズレを自動検出
  - 毎晩のkaizen-patrolで自動実行
  - design-system.mdにNav順序ルール・新規ダッシュボード追加手順を追記
- [x] **deploy_private.py SSoT化でinsight/パスを統合**（2026-03-20 session #8後半）
  - deploy_private.pyが全7パス（insight含む）+ functions + hubをカバー
  - デプロイマーカー書き込み → constancy_checksが毎晩検知
  - 正常系テスト（マーカーあり=PASS）・異常系テスト（マーカー削除=warn検知）共にPASS
  - infra-manifest.yamlにdeploymentsセクション追加
  - stock-analyzerマージコンフリクト解決（signal_report.json）、kaizen-agent push完了

- [x] **Public→Private nav隔離監査**（2026-03-21 session #9 — kaizen-agentから実行）
  - 全Public HTMLファイル（trip-planner 5件, property-report 7件）を走査
  - `iuma-private.pages.dev` への参照がゼロであることを確認
  - `renderer.py _public_nav` にPrivate URLが含まれないことを確認
  - report-dashboard の Intel リンクは意図的例外（Cloudflare Access保護済み）
  - Self-Insightは `_private_nav` のみ掲載 → Public側から到達不可を実証
- [x] **Phase 1パイプライン基盤構築**（2026-03-22 session #10）
  - `generate_profile.py` (964行): 全占術+性格分析の自動計算パイプライン
    - 四柱推命/九星気学/六星占術/西洋占星術/血液型をPure Pythonで実装（OSSライブラリ不使用で自前計算）
    - エニアグラム/HSP-6/ADHD ASRS-6/Mini-IPIP Big Five スコアリング
    - 3-Tier機能ゲーティング設計
    - 霊合統合スコア（メイン70%+サブ30%加重 → ラベル自動分類）
  - `generate_dashboard.py` (487行): profile.yaml → HTML自動生成
    - Chart.js統合（9年/12年/霊合統合チャート）
    - Tier別ロック表示（blur+unlock CTA）
  - Python venv (`.venv/`, python3.14) + ディレクトリスキャフォールド
  - ダッシュボードHTML（index.html 1296行）レビュー: CSS/構造+Personality Profile+占術プロファイル+月間運勢データ（2-6月の4ドメイン詳細テキスト+九星×六星統合インサイト）確認
  - form/index.html (v3) + generate_dashboard.py (v2) の編集あり（ファイルバックアップ記録）
  - API障害が長時間継続: 502×複数回 → ConnectionRefused/FailedToOpenSocket×10回リトライ上限×3サイクル以上。ユーザー「続けて」「止まってる？」「続き」で再試行するも全て失敗。最終的に/clearで終了
- [x] **session #12 未コミット変更のコミット+push**（2026-03-22 session #12→cf2240b）
  - generate_profile.py(+167行), generate_dashboard.py(+69行), index.html(+1行), test_calculations.py(+214行), data/users/shuhei/profile.yaml, data/users/yuma/profile.yaml, docs/form_questions.md, .gitignore 計+1752行
- [x] **narratives.yaml作成**（2026-03-22 session #15→8ff378c）
  - index.htmlからBash grep+Pythonパーサで全ナラティブテキスト抽出 → `data/users/yuma/narratives.yaml` (44KB, 391行)
  - 6セクション: core_identity / personality / divination / forecast_2026 / monthly_2026 / cross_analysis
  - 全12ヶ月×4ドメイン+インサイト、Cross Analysis 5件、CliftonStrengths TOP5、Typology 4種、占術4体系
- [x] **generate_dashboard.py --narratives対応**（2026-03-22 session #15→ec4ee39）
  - CLI引数 `--narratives` 追加（省略可能、後方互換性OK）
  - 全セクションへのナラティブテキスト注入: CliftonStrengths/Typology/Core Identity/占術4体系/2026運勢/月別運勢/Cross Analysis
  - narrativesなし実行も正常動作（fallback対応）
- [x] **E2Eパイプラインテスト**（2026-03-22 session #15）
  - generate_profile.py → profile.yaml → generate_dashboard.py → HTML の全工程PASS
  - テストユーザー(Tier 1) + Yuma(Tier 3) + narratives統合 全パターン検証OK
- [x] **周平ダッシュボード再生成**（2026-03-22 session #15→336c760）
  - 最新パイプラインでTier 2ダッシュボード再生成（470行）
  - 外部リンクゼロ（ページ内アンカーのみ）確認
  - PDF化: ~/Desktop/shuhei_self_insight.pdf (1.1MB)
  - Gmail下書き作成（PDF手動添付して送信）
- [x] **generate_dashboard.py フルリライト完了**（2026-03-22〜23 session #16→d9783d8〜c84bac0）
  - Step 1: Gnav+2ピラー骨格リライト（d9783d8）
  - Step 2: 月間運勢セクション追加（8c9da3c）
  - Step 3: Cross Analysisセクション追加（318a879）
  - Step 4: CSS仕上げ — heroアニメーション、noiseテクスチャ、chartイージング（c84bac0）
  - 535行→1,677行。index.htmlのフル品質をプログラマティック生成に移行完了
- [x] **ナラティブ充実化+UX改善**（2026-03-23 session #17→32da1d9〜a741ec7）
  - リッチナラティブテキスト全セクション追加（32da1d9）
  - 周平プロファイル更新+チャートfill area修正（ec9e948）
  - 統合オーバーレイチャート1枚に集約+フォーキャストナラティブ（083a782）
  - 西洋占星術拡充、ドメインメッセージ、HSP/ADHDリフレーム（41dd078）
  - Hero再デザイン — 非専門家の読みやすさ向上（2bb1eb3）
  - 日本語翻訳+専門用語グロサリー追加（0281b49）
  - ナラティブ生成方針ドキュメント更新（89837da）
  - アクション提案追加: 今月ガイダンス、年間テーマ、行動ブループリント（c322056）
  - Likertスケール統一（1-5表示、ADHD内部0-4変換）（5673a95）
  - 「今月」ガイダンス配置修正 — 月間運勢の後、Core Identity先頭（a741ec7）

- [x] **P0改善: CSS修正+2nd-person化+フェードイン+折りたたみ**（2026-03-23 session #18→83a5fb5）
  - `var(--radius-sm)` → `var(--r-sm)` CSS変数修正
  - 全解釈テキストを2人称（あなた）視点に変更（両プロファイル）
  - IntersectionObserver scroll-triggered fade-inアニメーション追加
  - 「今月のガイダンス」を月間運勢の当月パネルに統合（別セクション削除）
  - 統合インサイト折りたたみ（1段落表示+展開）、SF TOP5説明もtap展開化
- [x] **P1改善: セクション引用句+ドメインカラー+パーソナライズ助言+レアリティバッジ**（2026-03-23 session #18→38930c3）
  - Co-Star風セクション引用句（各主要セクション頭）
  - ドメインカラーコーディング統一（blue/gold/green/pink）
  - 月間アドバイスにユーザーのSF TOP強み+日主五行を反映
  - 占術アコーディオン（4サブセクション折りたたみ、四柱推命がデフォルト展開）
  - レアリティバッジ: 霊合10%、日主10%、欠落五行コンボ
  - `--no-gnav`フラグ追加（クライアント向けダッシュボード用）
- [x] **フォームバックエンドパイプライン構築**（2026-03-23 session #19→2a2a8f6）
  - Google Apps Script Web App (`scripts/apps-script.gs`): フォーム → Google Sheets蓄積
  - `scripts/process_submission.py` (155行): submission JSON → generate_profile.py → generate_dashboard.py E2Eパイプライン
  - `form/index.html` 非同期POST送信対応（SUBMIT_URL設定可能、LINE/clipboard fallback）
  - UUIDベースのユーザーパス（`users/{uuid}/`）
  - E2Eテスト済: テスト太郎 Tier 2 → profile.yaml + index.html生成成功
- [x] **UXオーバーホール — Hub Architecture+アーキタイプシステム**（2026-03-23 session #19→6a91657）
  - **Hub+Detail Architecture**: 全セクションを折りたたみカード化（デフォルト閉）
  - **アーキタイプシステム**: day_master + top strength → 動的アーキタイプ名（例: 静かな炎の共鳴者）
  - Hero再デザイン: アーキタイプ名グロー、タグライン、パーティクルアニメ、hubカードショートカット
  - 感情的セクション名: Core Identity→あなたの本質、Cross Analysis→才能×運命 等
  - Section Nav削除（stickyナビバー廃止）
  - Gnav デフォルトOFF（`--gnav`フラグで個人用のみ表示）
  - generate_dashboard.py: 1,677→2,084行（+407行）
- [x] **Cloudflare Accessセッション延長**（2026-03-23 session #20）
  - Zero Trust → iuma-private アプリのセッション期間を**1 month**に変更
  - スマホからも月1回のOTP認証で済む
- [x] **月間テキスト個別化+二重表示修正+CSS chevron+フォーム接続**（2026-03-24 session #21→951ca29, 60d0410, eb98bdc, 82e71eb, 405e1ec, d8ebed4）
  - 月間ナラティブ/アドバイス: 12/12ユニーク化（九星の宮+六星フェーズ+西洋テーマを直接組み込み）
  - SF強みローテーション: Top5を月ごとに回す（月1=Empathy, 月2=Intellection, ...）
  - 推奨ドメイン: 全スコア同一月は六星フェーズで決定（財成→お金, 立花→人間関係等）
  - PALACE_DESC / PHASE_DESC辞書追加（九星9宮+六星12フェーズの意味解説）
  - 二重タイトル表示修正: 全セクションの内部pillar-header/section-title/section-desc除去（Hub cardヘッダーに一本化）
  - 折りたたみ記号: テキスト文字(+/−)→CSSボーダーchevron（フォント依存排除）
  - Hero名スタイリング: フォントサイズ拡大+明度アップ+装飾線追加（82e71eb）
  - フォーム→Apps Script接続: form/index.htmlにSUBMIT_URL設定+非同期POST送信（405e1ec）
  - CORS修正: Apps Script POSTのリダイレクト問題をno-corsモードで解決（d8ebed4）

## Completed (session #23)
- [x] **nav SSoT enforcement — generate_dashboard.py**（2026-03-24 session #23→f5f8209）
  - ハードコードGNAV_LINKSリスト → `from lib.renderer import get_nav_html` SSoT関数呼び出しに切替
  - kaizen-agent QA config: nav_python_filesを空配列に更新（false positive 2件解消、33→31）
  - 3層防御完成: ①SSoT関数 ②デプロイ時inject_gnav()自動注入 ③毎晩patrol.pyが乖離検知

## Completed (story mode + share card + 相性診断ページ新規作成 2026-03-28)
- **Before**: フォームは入力→結果の1方向のみ。ストーリーモード・シェアカード・相性診断ページが存在しなかった
- **After**: story.html（物語風の性格紹介ページ）新規作成、share-card.js（OGP風シェアカード生成）新規作成、compatibility.html（5軸相性診断：五行30%+九星25%+六星15%+西洋占星15%+血液型15%、レーダーチャート+スコアリング+招待リンク機能付き）新規作成
- **Commits**: self-insight b60af71

## Completed (compatibility.html const重複エラー修正 + share-card SNSボタン追加 2026-03-28)
- **Before**: compatibility.htmlの`<script>`内でengine.jsと同名のconst（ELEMENT_JP, NINE_STAR_ELEMENTS, NINE_STAR_NAMES）を再宣言 → スクリプト全体がSyntaxErrorで死亡し相性診断が完全に動作しない。share-card.jsはWeb Share API非対応のデスクトップでシェアボタンが非表示
- **After**: 重複const 3件を削除（engine.js側を参照）→ nodeで結合構文チェックOK・重複ゼロ確認済み。share-card.jsにX・LINE・コピーの3ボタンを常時表示（デスクトップ対応）。index.htmlに`#continue=`ハッシュハンドラ追加、story.htmlのCTA遷移を`#r=`→`#continue=`に変更
- **Commits**: self-insight cdf2cba

## In Progress
- [ ] **generate_dashboard.py / generate_profile.py 構造分割**: constancy警告（両ファイル500行超過）への対応。generate_dashboard.py 2,348行、generate_profile.py 1,130行

## Next Actions
1. **renderer.js動作テスト**: Tier 1即時体験（生年月日のみ→リッチ結果表示）の本番品質化は完了。ブラウザ実機テストで全辞書・ナラティブ・チャートが正常表示されるか確認
2. **相性診断の動作テスト+バイラル機能強化**: compatibility.htmlのconst重複修正済み → 動作確認 + シェアカード→招待リンク→友達流入のバイラルループ検証
3. **E2Eフロー完成**: フォーム送信→Google Sheets蓄積が未確認（no-cors修正済み、再テスト必要）
4. **engine.js検証**: Yumaプロファイルで計算結果をPython版と照合（差異がないか）
5. **SIPS実装**: Big Five 40問→16 Archetypes+24 Strengths導出ロジック、アーキタイプ/強みテーマ名称設計
6. **短縮URL設計**: `form/#r=base64...`（長い）→ `/results/{uuid}`（短い）への移行
7. **ファイル分割**: generate_dashboard.py（2,348行）/ generate_profile.py（1,130行）のモジュール分割

## Key Decisions
- 2ピラー構造: Timeless Identity + Year Forecast
- 月間運勢: 仕事/お金/健康/恋愛の4ドメイン
- 占術ロジックはLLM生成禁止。OSSライブラリ使用 + ユニットテスト必須
- Edit分割方式でHTML変更（フルリライト禁止）
- デプロイ先: GitHub Pages（Cloudflareではない。session #8で切替）。Cloudflareパスもdeploy_private.py SSoTに統合済み（fallback）
- gnav SSoT = `lib/renderer.py` の `_private_nav`/`_public_nav`。ハードコードgnavは `check_gnav_consistency` で毎晩自動検証
- Nav順序（2026-04-06更新）: Primary: Stock → Market Intel → Cisco → Action → Property / Overflow: Wealth → Insight → Health → Travel → Newsletter → Bookmarks → SNS → Self-Insight
- Self-InsightはGitHub Pages公開だが、Private navにのみ掲載（個人データのため）
- Public→Private nav隔離: 2026-03-21監査で全Public HTML（12ファイル）にPrivate URL混入ゼロを実証。`renderer.py` の `scope` パラメータで自動分離される設計
- **ナラティブ生成方針（session #17で確定）**: narratives.yamlは不要。generate_dashboard.pyがprofile.yamlの計算結果からプログラマティックにナラティブ（解説・インサイト・Cross Analysis）を生成する。どのユーザーでもYumaのindex.html相当のリッチな出力がゴール。LLM API依存なしで、テンプレート+ロジックで実現する
- 周平への共有はPDFでなくURL提供（`users/shuhei/index.html`）。外部リンクゼロで単体完結
- **ユーザーパス方式**: `users/{uuid}/index.html`（UUID 8桁）。名前衝突回避+プライバシー保護
- **フォームバックエンド**: Google Apps Script Web App → Google Sheets蓄積。`scripts/apps-script.gs` + `scripts/process_submission.py`（E2Eテスト済み）。LINE/clipboardはfallback
- **クライアントサイド即時表示**: `form/engine.js`（全計算ロジックJS移植）+ `form/renderer.js`（ダッシュボード描画）。フォーム送信後にサーバー不要で即時結果表示
- **管理者ページ**: `form/admin.html` — Google Sheetsの回答一覧表示、UUID/Tier/ステータス管理、URLコピー機能
- **結果URL永続化**: フォーム送信後にURLハッシュ（`#r=base64data`）に結果データを埋め込み。リロード/ブックマーク/共有対応。ローンチ時は`/results/{uuid}`に移行予定
- **レンダラー統一方針（session #21で確定）**: renderer.js（JS）をgenerate_dashboard.py（Python）レベルに品質向上し、最終的にPython版を廃止。即時表示=本番品質=永続URLの一気通貫を実現。Yumaは友人と同じ結果URLで確認する（admin.htmlは結果確認用ではなく管理台帳）
- **日本語化方針**: 全英語用語に日本語訳を併記 + 専門用語グロサリー。非専門家でも理解できるUI
- **Likertスケール統一**: 全スケール1-5表示（ADHDは内部0-4で計算、表示時に1-5変換）
- **アクション提案構成**: 「今月のガイダンス」（月間運勢後）+ 「年間テーマ」+ 「行動ブループリント」の3層
- **IP/著作権戦略（session #17で確定）**:
  - **Big Five (IPIP)**: 科学的基盤。完全パブリックドメイン、制限なし → 全性格分析の土台
  - **CliftonStrengths**: 全34テーマ名がGallup登録商標 → 商用利用不可 → 独自「Self-Insight Strengths 24」に置換
  - **MBTI**: ブランド名は商標だがJung由来16タイプ体系はパブリックドメイン → 独自「Self-Insight Archetypes」16型に置換
  - **HSP Scale**: Aron商用ライセンス必要 → Big Five Factor 5（Sensitivity & Awareness）8問+補助6問に統合
  - **ADHD ASRS-6**: WHOが無料提供、帰属表示のみ → そのまま使用可
  - **エニアグラム**: 型番号は自由利用可 → そのまま使用可
  - **SIPS設計（Self-Insight Personality System）**: Big Five 40問（Mini-IPIP）→ 16 Archetypes + 24 Strengths + Sensitivity Score を導出。HSP 6問+ADHD 6問=12問をBig Five Factor 5の8問+補助6問に統合し、総質問数削減＆情報量増
  - アーキタイプ/強みテーマの具体名称は後続セッションで設計
- **Hub+Detail Architecture（session #19で確定）**: 全セクションを折りたたみカードに。デフォルト閉。データレポート→プレミアムパーソナル体験への転換
- **動的アーキタイプ名**: day_master + top strength から自動生成（例: 静かな炎の共鳴者）。Hero中央にグロー表示
- **感情的セクション名**: 技術的名称→感情的ラベル（Core Identity→あなたの本質、Cross Analysis→才能×運命 等）
- **Section Nav廃止**: stickyナビバー削除。Heroのhubカードがショートカット機能を代替
- **Gnav制御**: デフォルトOFF（クライアント向け）。`--gnav`フラグで個人用表示。`--no-gnav`は明示的スキップ
- **Nav SSoT enforcement（session #23で確定）**: generate_dashboard.pyのハードコードGNAV_LINKS → `get_nav_html()` 関数呼び出し。renderer.pyのPRIVATE_NAVが全ナビの唯一の定義元。変更は1箇所で全ページに自動反映
- **Cloudflare Accessセッション**: iuma-private の認証期間を1 monthに延長（月1回OTP）
- **ファネル転換（session #27ブレスト 2026-03-28）**: 12分フォーム入口 → 「30秒で鳥肌体験→シェアカード→友達流入」バイラルループ。生年月日だけで即Tier 1結果表示。相性診断でバイラル係数>1を狙う
- **ポジショニング転換（session #27ブレスト 2026-03-28）**: 「統合ダッシュボード」→「あなたの取扱説明書をAIが作ります」。機能ではなくメタファーで売る
- **価格転換（session #27ブレスト 2026-03-28）**: 全部サブスク → Tier 2は買い切り¥980（16Personalities $9が証明済み）。月額サブスクはTier 3のみに集中

## Blockers
- **API 502障害**: session #10, #12で計5時間以上の障害。大規模ファイル生成（Agent）が特に脆弱。回避策: Agent使用を最小化し、Edit分割方式で段階的変更

## Environment Setup
- GitHub Pages: `https://ymatz28-beep.github.io/self-insight/`
- profile.yaml: `self-insight/data/profile.yaml`
- ローカル確認: `open /Users/yumatejima/Documents/Projects/self-insight/index.html`
- デプロイブランチ: `gh-pages`

## History
| # | Date | Summary |
|---|---|---|
| 1 | 2026-03-19 | プロジェクト発足。市場調査・WWH分析・HANDOFF作成 |
| 2 | 2026-03-19 | Phase 0: profile.yaml構築、ダッシュボードv1作成、CXフィードバック、九星気学修正、六星占術追加、v2リライト開始 |
| 3 | 2026-03-19 | v2リライト着手: v1の4問題特定、dashboard-rules.md確認、frontend-designスキル起動→API 502+中断で未完了 |
| 4 | 2026-03-19 | ルートリポ一括sync: self-insight/含む全プロジェクトをステージング・コミット（self-insight固有の変更なし） |
| 5 | 2026-03-20 | v2リライト再試行: API 502×10回+セッション強制終了。index.html未変更 |
| 6 | 2026-03-20 | v2リライト3回目: API 502×3回+セッション終了。3連続失敗 |
| 7 | 2026-03-20 | **v0.3大規模リストラクチャ成功**: 2ピラー構造+月間4ドメイン運勢。Edit分割方式で安定実装。1147行。UXリサーチ(Co-Star/The Pattern)+月運データ調査(八雲院/hosokikazuko.com)実施 |
| 8 | 2026-03-20 | **v0.4デザイン準拠+コンテンツ2-3倍増量+gnav QA+deploy SSoT**: Gnav/SectionNav/--bg修正、全セクション文章拡充、Cloudflare→GitHub Pages切替、gnav統一、`check_gnav_consistency`実装、deploy_private.py SSoT化（insight含む全パス統合+constancy検証PASS） |
| 9 | 2026-03-21 | **Public→Private nav隔離監査**: kaizen-agentから全Public HTML（trip-planner 5件+property-report 7件）走査、Private URL混入ゼロを確認。renderer.py scope設計の正常動作を実証 |
| 10 | 2026-03-22 | Phase 1パイプライン基盤構築(generate_profile.py 964行+generate_dashboard.py 487行+form/index.html)+ダッシュボードHTML全体レビュー → API障害(502/ConnectionRefused/FailedToOpenSocket)が3時間以上継続、10回リトライ上限×3サイクル到達。/clearで終了 |
| 11 | 2026-03-22 | ステータス確認のみ。Phase 0→1移行中で止まっていることを確認。別セッションで対応中とのこと。コード変更なし |
| 12 | 2026-03-22 | generate_profile.py月間運勢計算追加(964→1130行)+generate_dashboard.py小規模拡張(487→535行)。Agent Bダッシュボード書き換えタイムアウト(52分)。narratives.yaml計画策定→API 502障害(08:44-10:17)でユーザー中断。全変更コミット済み(cf2240b) |
| 13 | 2026-03-22 | index.html月間運勢データ(8-12月)+JS描画コード読み取り中にAPI障害→/clearで終了。コード変更なし |
| 14 | 2026-03-22 | generate_dashboard.py(536行)読み取り中にAPI 502障害→「別セッションと重複してないよね？」確認後/clearで終了。コード変更なし |
| 15 | 2026-03-22 | **narratives.yaml作成+--narratives対応+E2E全パス+周平再生成**: Bash grep+Pythonで index.html→narratives.yaml(44KB)抽出。generate_dashboard.pyに--narratives引数追加(全セクション注入)。E2Eテスト全パターンPASS。周平ダッシュボード再生成(470行)+PDF化+Gmail下書き。commits: 8ff378c, ec4ee39, 336c760 |
| 16 | 2026-03-22 | **generate_dashboard.pyフルリライト完了**: Gnav+2ピラー骨格→月間運勢→Cross Analysis→CSS仕上げ(heroアニメ/noiseテクスチャ/chartイージング)。535→1,677行。commits: d9783d8〜c84bac0 |
| 17 | 2026-03-23 | **ナラティブ充実+日本語化+UX改善+アクション提案+IP戦略確定**: 全セクションリッチテキスト、統合チャート1枚化、Hero再デザイン、全英語→日本語併記+グロサリー、Likert1-5統一、今月/年間テーマ/行動ブループリント追加。IP/著作権調査→SIPS設計方針確定。commits: 32da1d9〜a741ec7 |
| 18 | 2026-03-23 | **P0+P1改善**: CSS修正、2人称化、fade-inアニメ、ガイダンス月間運勢統合、折りたたみUI、Co-Star風引用句、ドメインカラー統一、パーソナライズ助言(SF+日主)、占術アコーディオン、レアリティバッジ、--no-gnavフラグ。commits: 83a5fb5, 38930c3 |
| 19 | 2026-03-23 | **フォームバックエンド+UXオーバーホール**: Apps Script+process_submission.py E2Eパイプライン構築。Hub+Detail Architecture（全セクション折りたたみカード化）、動的アーキタイプ名（day_master+強み）、感情的セクション名、Section Nav廃止、Gnav制御。generate_dashboard.py 1,677→2,084行。commits: 2a2a8f6, 6a91657 |
| 20 | 2026-03-23 | **Cloudflare Accessセッション延長**: Zero Trust iuma-privateのセッション期間を1 monthに変更。Reminder↔アクション同期設計確認（iCloud即時同期、launchd 30分毎、スマホ入力OK）。コード変更なし |
| 21 | 2026-03-24 | **月間テキスト個別化+UXバグ修正+フォーム接続**: 月間ナラティブ12/12ユニーク化（PALACE_DESC/PHASE_DESC辞書+SF強みローテーション+六星フェーズ別ドメイン推奨）。全セクション二重タイトル除去。折りたたみ→CSS chevron（フォント非依存）。Hero名スタイリング改善（大きく明るく+装飾線）。フォーム→Apps Script POST接続（SUBMIT_URL）+no-corsモード修正。commits: 951ca29, 60d0410, eb98bdc, 82e71eb, 405e1ec, d8ebed4 |
| 22 | 2026-03-24 | **アクションアイテム登録**: si-sheets-test(フォーム→Sheets再テスト/high)をaction_tracker登録。newsletter-digest側セッションの一環。self-insightコード変更なし |
| 23 | 2026-03-24 | **nav SSoT enforcement**: generate_dashboard.pyのハードコードGNAV_LINKS→get_nav_html()関数呼び出しに統一。kaizen-agent QAのfalse positive 2件解消(33→31)。全ジェネレータがrenderer.py SSoTを参照する3層防御完成。commit: f5f8209 |
| 24 | 2026-03-25 | **cross-project session (dotfiles/kaizen-agent)**: Brewfile更新(deno/mlx/tesseract/zeromq/python@3.14追加)+setup.sh 8ステップ化+launchd plistバックアップ+kaizen-agent環境drift自動検出(check_brewfile_drift)。self-insightコード変更なし |
| 25 | 2026-03-26 | **kaizen-agent QA改革セッション**: action_items.yaml確認 — self-insight関連3件(si-e2e/si-admin/si-sheets-test)がhigh/pendingで残存を確認。全125件中self-insight固有タスクの優先度変更なし。self-insightコード変更なし |
| 26 | 2026-03-27 | **Projects CLAUDE.md Skill Routing追加**: Before: スキル発火ルールが暗黙知 → After: Skill Routing表(8ルール)をCLAUDE.mdに明文化+story-intakeトリガーに「インタビューして」追加。self-insightコード変更なし |
| 27 | 2026-03-28 | **story mode+share card+相性診断+バグ修正**: Before: ストーリー/シェア/相性診断が未実装+const重複でスクリプト全死亡 → After: 3ページ新規作成+重複修正+SNSボタン追加。commits: b60af71, cdf2cba |
| 28 | 2026-03-28 | **cross-project: section_nav migration**: self-insight変更なし（lib/scripts側でsection_navコンポーネント化） |
| 29 | 2026-03-28 | **cross-project: 全HANDOFF履歴→SNSネタ一括生成**: 14プロジェクトのHANDOFF History抽出→topic_candidates.yaml 21件追加(027-047)。self-insight関連: topic-038(占いSaaS 3週間MVP), topic-040(Cloudflare Access OTP)。self-insightコード変更なし |
| 30 | 2026-03-29 | **renderer.js本番品質化+取扱説明書ブランディング**: Before: renderer.jsがMVP品質(辞書/ナラティブなし)+story.htmlが「AI Self-Insight」ブランド → After: renderer.js +397行(PALACE/PHASE/DM辞書+SECTION_QUOTES追加)+story.html「あなたの取扱説明書」+セマンティックスライドラベル。commit: e80268e |
| 31 | 2026-03-30 | **ステータス確認のみ**: Before: 前回セッション強制終了でcommit/push状態不明 → After: session-endフックがed3dd9aで全変更コミット済みを確認。未コミット変更なし。コード変更なし |
| 32 | 2026-03-31 | **cross-project: property-analyzer HANDOFF更新**: property-analyzerのマーケット品質改善セッション結果をHANDOF更新(bcbc99a)。self-insightコード変更なし |
| 33 | 2026-04-06 | **cross-project: Gnav Pattern B + Nav順序変更**: Before: Self-Insightはgnav全13項目フラット表示 → After: overflow ⋯ドロップダウンに配置(Primary 5: Stock/Market Intel/Cisco/Action/Property、Overflow 8にSelf-Insight含む)。iuma-privateトップページBento Gridリデザイン計画でSelf-Insight=Tier3(compact)。self-insightコード変更なし |
| 35 | 2026-04-09 | **cross-project: 横断監査フォント+CSS変数+gnav**: Before: story.html serif fallback+index.html 5色ハードコード+gnav nav-more未適用 → After: sans-serif修正+CSS変数化5箇所+nav-more overflow追加 |
| 34 | 2026-04-07 | **cross-project: ローカルファースト化+idle_guard+Dead Man's Switch**: Before: property-patrol GHA実質Primary+kaizen-patrol plist 2日停止 → After: ローカルファースト+GHA条件付きフォールバック+idle_guard(lib新設)+Digest Status Bar+全ジョブ_NAME_JA日本語化。4リポ(property-analyzer/kaizen-agent/lib/scripts)HANDOFF更新。self-insightコード変更なし |