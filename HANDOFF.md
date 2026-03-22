# Self-Insight — HANDOFF

## Last Updated
2026-03-22 (session #12 — ダッシュボード書き換え+ナラティブ抽出試行→API障害で中断)

## Project Overview
複数の占術（四柱推命・九星気学・六星占術・西洋占星術・干支）+ 心理学ツール（エニアグラム・HSP/ADHD特性・独自SF/MBTI代替）を統合した、徹底的にパーソナライズされた自己理解ダッシュボードサービス。有料SaaS展開を目指す。

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
- **Phase 0→1移行**: パイプライン基盤構築（generate_profile.py + generate_dashboard.py）← 現在
- **Phase 1**: 友人5人にβテスト（無料）→ PMF検証
- **Phase 2**: 月額980円でローンチ

### Pipeline Architecture (v0.5)
```
入力 → generate_profile.py → profile.yaml → generate_dashboard.py → HTML
```
- **generate_profile.py** (1130行): 生年月日+アンケート → 全占術・性格分析を自動計算 → profile.yaml出力
  - 四柱推命（年柱/月柱/日柱 + 五行バランス）、九星気学（本命星/月命星 + 9年サイクル）
  - 六星占術（運命星 + 霊合判定 + 12年サイクル + 霊合統合スコア）、西洋占星術（太陽星座）
  - 血液型特性、エニアグラム、HSP-6、ADHD ASRS-6、Mini-IPIP Big Five → MBTI換算
  - **3-Tier制**: Tier 1=生年月日のみ、Tier 2=+エニアグラム/HSP/ADHD、Tier 3=+Big Five/MBTI
  - CLI: `python3 generate_profile.py --name "名前" --birth-date "YYYY-MM-DD" --blood-type AB --output path`
- **generate_dashboard.py** (535行): profile.yaml → スタンドアロンHTML（Chart.js内蔵）
  - Tier別機能ゲーティング（Tier 3未達セクションはblur+ロック表示）
  - 運気サイクルチャート（9年/12年/霊合統合）自動生成
  - CLI: `python3 generate_dashboard.py --profile profile.yaml --output output.html --tier 2`
- **Python venv**: `.venv/` (python3.14, PyYAML)
- **ディレクトリ**: `data/users/`, `output/`, `form/`, `docs/`, `users/` (Phase 1スキャフォールド)

### Dashboard IA (v0.4)
```
1. Nav (sticky, horizontal scroll — 6セクション)
2. Hero (compact card, identity chips + stats)
3. ★ Core Identity (timeless — Pillar 1)
   - 統合インサイト (6体系統合の人物像)
   - Summary cards (Core Essence / Strongest Axis / Duality / Watch Out)
4. Personality Profile
   - CliftonStrengths TOP5
   - Domain Distribution (Relationship/Strategic/Executing/Influencing)
   - Typology (Enneagram 4 / AB型 / HSP High / ADHD Leaning)
5. 占術プロファイル (timeless core traits only)
   - 四柱推命 (3柱 + 五行バランス)
   - 九星気学 (七赤金星 × 九紫火星)
   - 六星占術 (木星人− × 金星人− 霊合)
   - 西洋占星術 (蠍座 Water Fixed Pluto)
   - Unlock banner (出生時刻)
6. ★ 2026年運勢 (Pillar 2)
   - Year positioning (past/present/future narrative)
   - 統合運気カーブ 3-line overlay (2020-2032)
   - 3体系一致ポイント分析
   - Year guidance cards (仕事/お金/健康/恋愛)
7. 月間運勢 (Jan-Dec, interactive)
   - Year timeline bar (color-coded)
   - Month selector tabs (horizontal scroll)
   - Monthly panels (4 domains: 仕事/お金/健康/恋愛 with star ratings)
   - Monthly insight synthesizing 九星×六星
8. Cross Analysis (strength × fortune combos)
9. Footer (v0.4)
```

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

## In Progress
- [ ] **generate_dashboard.py書き換え**: index.htmlのフル品質をプログラマティック生成に移行。Agent Bがタイムアウト(52分)で未完了。535行のまま（487→535は session #10の小規模変更）
- [ ] **narratives.yaml作成**: index.htmlからナラティブテキスト（統合インサイト/CliftonStrengths/占術解説等）を構造化YAML化。計画のみで未着手（`data/users/yuma/` に `profile.yaml` のみ存在）
- [ ] **generate_profile.py月間運勢計算**: 964→1130行に拡張済み（+167行差分、未コミット）。月間運勢計算ロジック追加

## Next Actions
1. **未コミット変更のコミット+push**: generate_profile.py(+167行)、generate_dashboard.py(+69行)、index.html(+1行)の差分をコミット
2. **narratives.yaml作成**: index.htmlから全ナラティブテキスト抽出 → `data/users/yuma/narratives.yaml` に構造化保存。ダッシュボードジェネレータがロードして使う設計
3. **generate_dashboard.py強化**: 現535行をindex.html（1296行相当）のフル品質に段階的強化。セクション単位のEdit分割方式で実施（フルリライトはタイムアウトするため禁止）
4. **パイプラインE2Eテスト**: `generate_profile.py → profile.yaml → generate_dashboard.py → HTML` の一気通貫動作確認
5. **月運データの精度向上**: 九星気学の月別宮位置を正確に計算（OSSライブラリ or 暦テーブル）
6. **ユニットテスト**: 占術計算の正確性検証（test_calculations.py 存在するが未確認）
7. **独自診断フレームワーク設計**: MBTI/SF/エニアグラムの代替となる独自性格診断の設計
8. **入力ページ設計**: 生年月日→血液型→性格診断→結果出力のUXフロー
9. **改善アイデア: ナラティブ自動生成**: 新規ユーザー向けに、profile.yamlからLLM APIでナラティブテキストを自動生成するパイプライン追加（Yumaはindex.htmlから抽出、他ユーザーは自動生成）

## Key Decisions
- 2ピラー構造: Timeless Identity + Year Forecast
- 月間運勢: 仕事/お金/健康/恋愛の4ドメイン
- 占術ロジックはLLM生成禁止。OSSライブラリ使用 + ユニットテスト必須
- Edit分割方式でHTML変更（フルリライト禁止）
- デプロイ先: GitHub Pages（Cloudflareではない。session #8で切替）。Cloudflareパスもdeploy_private.py SSoTに統合済み（fallback）
- gnav SSoT = `lib/renderer.py` の `_private_nav`/`_public_nav`。ハードコードgnavは `check_gnav_consistency` で毎晩自動検証
- Nav順序: Stock → Market Intel → Insight → Wealth → Action → Self-Insight → Health → Property → Travel
- Self-InsightはGitHub Pages公開だが、Private navにのみ掲載（個人データのため）
- Public→Private nav隔離: 2026-03-21監査で全Public HTML（12ファイル）にPrivate URL混入ゼロを実証。`renderer.py` の `scope` パラメータで自動分離される設計
- **ナラティブ分離設計**: profile.yaml（計算データ）+ narratives.yaml（テキストコンテンツ）を分離。Yumaはindex.htmlから抽出、新規ユーザーはLLM API自動生成の予定

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
| 12 | 2026-03-22 | generate_profile.py月間運勢計算追加(964→1130行)+generate_dashboard.py小規模拡張(487→535行)。Agent Bダッシュボード書き換えタイムアウト(52分)。narratives.yaml計画策定→API 502障害(08:44-10:17)でユーザー中断。全変更未コミット |
