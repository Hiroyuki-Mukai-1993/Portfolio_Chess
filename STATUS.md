# STATUS

最終更新: 2026-02-10

## いま動くもの（動作確認済み）
- 盤面初期化: `Board()` / `Board.from_start_position()`
- Move（着手データ）: UCI形式（Universal Chess Interface：例 `e2e4`）をパース
  - promotion suffix（例 `e7e8q`）のパースは実装済み（※ただしプロモーション全条件の実装は未完）
- Board.apply_move(): 合法手チェックなしで着手適用（手番反転含む）
  - キャスリング権の更新、およびキャスリング時のルーク移動まで反映
  - promotion 指定がある場合の駒の置換（昇格）まで反映
- Rules（ルール）:
  - 合法手生成（pawn / knight / bishop / rook / queen / king）
  - チェック回避（自玉がチェックになる手を除外）
  - キャスリング（条件チェック含む）

## テスト（pytest: Python testing framework）
- `tests/test_board_init.py` ✅
- `tests/test_apply_move.py` ✅
- `tests/test_pawn_moves.py` ✅
- `tests/test_pawn_captures.py` ✅
- `tests/test_knight_moves.py` ✅
- `tests/test_bishop_moves.py` ✅
- `tests/test_rook_moves.py` ✅
- `tests/test_queen_moves.py` ✅
- `tests/test_king_moves.py` ✅
- `tests/test_check_legality.py` ✅
- `tests/test_castling.py` ✅
- `tests/test_promotion.py` ✅（※ただし「全条件のプロモーション」は未完扱いの方針）
- 合計: **31 tests passed**

## 実装済みの仕様（MVP方針）
- 2人対局（同一端末）
- 合法手判定（擬似合法手 → 自玉チェック回避のフィルタ）
- チェック回避
- キャスリング（権利・経路の空き・通過マス攻撃チェックなど）
- メイト/ステイルメイト（終局判定）
- アンパッサン（en passant）

## 未対応 / 方針上まだ [x] にしないもの

## 既知の課題 / メモ
- Python 3.14 環境で pytest 実行は安定
- CLI（コンソール）での簡易対局は起動・着手・盤表示まで確認済み
- tiinterで盤駒表示

## 次に追加する予定（短く）
