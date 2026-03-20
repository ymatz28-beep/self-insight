# Self-Insight — HANDOFF

## Last Updated
2026-03-20 (session #7)

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
- **Phase 0**: Yuma自身のダッシュボードとして構築（identity.mdの延長）← 現在
- **Phase 1**: 友人5人にβテスト（無料）→ PMF検証
- **Phase 2**: 月額980円でローンチ

### Dashboard IA (v0.3)
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
   - Year guidance cards (仕事/お金/健康)
7. 月間運勢 (Jan-Dec, interactive)
   - Year timeline bar (color-coded)
   - Month selector tabs (horizontal scroll)
   - Monthly panels (4 domains: 仕事/お金/健康/恋愛 with star ratings)
   - Monthly insight synthesizing 九星×六星
8. Cross Analysis (strength × fortune combos)
9. Footer (v0.3)
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
- Phase 0はローカルHTML。デプロイ基盤はPhase 1以降で検討
- **Edit分割方式**: セクション単位のEdit呼び出しが安定（フルリライトはタイムアウト）

### Lesson Learned
- **九星気学計算エラー**: LLMが定数を10ではなく11で記憶していた → OSSライブラリ必須
- **フルHTML一括リライトのハング**: 3セッション連続失敗 → Edit分割で解決（セッション#7で成功）
- **月運データの重要性**: 年運だけでは「今月どうすべきか」がわからない → 月間4ドメイン運勢を追加

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

## In Progress
- なし

## Next Actions
1. **UXレビュー**: ブラウザで実際に操作し、月セレクタの動作確認・モバイル表示チェック
2. **月運データの精度向上**: 九星気学の月別宮位置を正確に計算（OSSライブラリ or 暦テーブル）
3. **霊合サブ星の月運追加**: 金星人(−)の月フェーズも統合し、霊合月次合成スコアを算出
4. **占術ロジック調査**: Python/JSで四柱推命・九星気学・西洋占星術を計算するOSSライブラリの選定
5. **独自診断フレームワーク設計**: MBTI/SF/エニアグラムの代替となる独自性格診断の設計
6. **入力ページ設計**: 生年月日→血液型→性格診断→結果出力のUXフロー
7. **ユニットテスト**: 占術計算の正確性検証

## Key Decisions
- 2ピラー構造: Timeless Identity + Year Forecast
- 月間運勢: 仕事/お金/健康/恋愛の4ドメイン
- 占術ロジックはLLM生成禁止。OSSライブラリ使用 + ユニットテスト必須
- Edit分割方式でHTML変更（フルリライト禁止）

## Blockers
- なし（v0.3リストラクチャ完了）

## Environment Setup
- ローカルHTML（Phase 0）
- profile.yaml: `self-insight/data/profile.yaml`
- 確認: `open /Users/yumatejima/Documents/Projects/self-insight/index.html`

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
