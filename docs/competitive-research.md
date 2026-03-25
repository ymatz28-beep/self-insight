# Self-Insight 競合調査・UX改善統合レポート
Generated: 2026-03-23

## 調査対象サービス
- Co-Star, The Pattern, Yodha, TimePassages, Aura
- CliftonStrengths, 16Personalities, Enneagram Institute
- しいたけ占い, 石井ゆかり, ゲッターズ飯田
- Spotify Wrapped, Apple Music Replay

## Self-Insightの独自価値（競合にないもの）
1. **複数占術×心理学の統合** — 4占術+SF+エニアグラムの統合は世界初クラス
2. **東洋×西洋の横断分析** — 四柱推命+九星+六星+西洋の4体系
3. **Cross Analysis** — 占術×性格の掛け合わせインサイト
4. **運気カーブの重ね表示** — 9年×12年×霊合統合のオーバーレイ

## 最重要テイクアウェイ (Top 5)
1. 初回体験はストーリー形式で段階的に開示（Spotify Wrapped）
2. 全セクションに「だからどうする」のAction Plan（CliftonStrengths）
3. 無料Tier 1で「鳥肌が立つほど正確」な体験（16Personalities）
4. カード型UI+段階的開示でモバイル最適化（The Pattern）
5. シェアラブルカードを標準装備（Spotify Wrapped）

## 優先実装ロードマップ

### P0（即着手）
- 2人称ナラティブ統一（「七赤金星は…」→「あなたの七赤金星は…」）
- スクロール連動フェードインアニメーション（IntersectionObserver）
- 月間運勢と今月ガイダンスの統合（重複排除）
- 統合インサイト・SF解説の折りたたみ化（スマホ対策）
- `--radius-sm` CSSバグ修正

### P1（次フェーズ）
- セクション冒頭の引用文（Co-Star式フック）
- 4ドメインカラーコーディング統一（仕事=青、金運=金、健康=緑、対人=赤）
- 月間adviceの個人化（占術結果×性格特性で修飾）
- 占術プロファイルのアコーディオン化
- 希少性演出（「霊合星人は全人口のX%」「この五行バランスは稀少」）
- Gnavをオプショナル化（クライアントには不要）

### P2（SaaS化時）
- ストーリーモード（初回体験用スワイプUI）
- シェアラブルカード自動生成（SNS用PNG）
- 相性診断（2ユーザー間）
- 月次LINE通知（The Pattern式リピート訪問）
- 音声ナレーション対応
- カレンダー連携（ゲッターズ飯田式）
- Blur内ティーザーテキスト（有料転換）

## 競合の課金モデル比較
| サービス | モデル | 価格帯 |
|---|---|---|
| Co-Star Plus | 月額サブスク | $14.99/月, $99.99/年 |
| The Pattern | 月額サブスク | $14.99/月〜 |
| CliftonStrengths | 買い切り | $24.99〜$59.99 |
| 16Personalities | フリーミアム+買い切り | 無料〜$9 |
| ゲッターズ飯田 | 月額サブスク | ¥350〜¥500/月 |
| しいたけ占い | 月額サブスク(note) | ¥500〜¥980/月 |

## Self-Insight推奨価格
- Tier 1（生年月日のみ）: 無料 → 衝撃的精度で掴む
- Tier 2（+性格診断）: ¥980買い切り or ¥480/月
- Tier 3（全開放+月次更新）: ¥980/月 or ¥7,800/年

## 参考ソース
- Co-Star: costarastrology.com, Wikipedia, Pratt IXD, Medium/DeMagSign
- The Pattern: thepattern.com, screensdesign.com
- CliftonStrengths: gallup.com
- 16Personalities: 16personalities.com
- Spotify Wrapped: newsroom.spotify.com, nogood.io, Fast Company
- Apple Music Replay: growthhq.io
- UX研究: Smashing Magazine, UXPin, Toptal, PMC, Irrational Labs
