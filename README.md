# Portfolio Chess

Python で実装したチェスアプリです。ルールエンジンを中心に、CLI と Tkinter UI の両方で対局できます。

## 主な機能
- 合法手生成
  - Pawn / Knight / Bishop / Rook / Queen / King
  - Castling（通過・到達マス被攻撃の禁止を含む）
  - En passant
  - Promotion（`q/r/b/n`）
  - 自殺手の禁止（王手放置の禁止）
- 終局判定
  - Checkmate
  - Stalemate
  - Draw by threefold repetition
  - Draw by 50-move rule
  - Draw by insufficient material
  - Draw by agreement（提案/受諾）
  - Resignation
- 棋譜・局面
  - SAN 生成（例: `Nf3`, `exd5`, `O-O`, `Qh4#`）
  - PGN 出力
  - FEN 読み込み / 書き出し
- 対局管理
  - New game
  - Reset
  - 先後交代（次局）

## セットアップ（Windows / PowerShell）
```powershell
cd C:\Users\moons\OneDrive\Documents\Playground\portfolio_chess\portfolio_chess
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install -e ".[dev]"
```

## 使い方
### 1. テスト実行
```powershell
py -m pytest
```

### 2. CLI 起動
```powershell
py -m portfolio_chess
```

CLI では以下のコマンドが使えます。
- `e2e4` など UCI 形式の指し手
- `fen` : 現在局面を FEN で表示
- `pgn` : 現在棋譜を PGN で表示
- `draw` : 合意ドローで終了
- `resign` : 投了
- `new` : 新規対局
- `quit` : 終了

### 3. Tkinter UI 起動
```powershell
py -m portfolio_chess.ui_tk
```

UI ボタン
- `New Game` / `Reset`
- `Swap First (Next)`
- `Resign`
- `Offer Draw` / `Accept Draw`
- `Load FEN` / `Copy FEN` / `Copy PGN`

## テストカバレッジ（現状）
- 初期配置 / 駒ごとの移動 / 取得
- 王手・王手回避・チェックメイト・ステイルメイト
- キャスリング / アンパッサン / 昇格
- pinned piece 制約
- キャスリング不可条件（被攻撃マス）
- en passant が王手回避を壊すケース
- SAN / PGN / FEN
- Draw rules（3fold, 50手, 戦力不足, 合意ドロー）

## 注意事項
- 3fold / 50手は「成立時に自動で引き分け」にしています（claim方式ではありません）。
- PGN タグは最小構成です。必要に応じて Event/Date/Round/Player 名等を拡張してください。

## 今後の拡張候補
- Minimax + 評価関数による簡易AI
- PGN/FEN の入出力UI強化（ファイル保存・読み込み）
- `python-chess` との局面相互検証テスト
- CI（GitHub Actions）と静的解析の自動化
