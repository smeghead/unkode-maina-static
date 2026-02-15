# 静的化作業 引き継ぎメモ（運用手順）

## 目的
新しいチャットでも、同じ流れで安全にHTML一括修正を進めるための手順書。

---

## 基本フロー（毎回共通）

スクリプトの実行タイミングは、ユーザーから指示のあった時のみ実行してください。
スクリプトの実行結果を報告してから先に進むようにしてください。

1. **対象を明確化**
   - 削除/変換したいHTML要素を具体的に定義する（タグ、class、id、文言など）。
2. **専用スクリプトを作成**
   - `scripts/` 配下に「1対象1スクリプト」で作る。
   - `check` と `delete`（または `convert`）を実装する。
3. **check を先に実行**
   - まず小範囲（例: `docs/*.html`）で件数確認。
   - 問題なければ `docs/lang`、`docs/view` へ拡大。
4. **delete / convert を実行**
   - 期待どおりの件数であることを確認してから実行。
5. **事後checkで検証**
   - 削除対象が `0` になったか、変換対象が `0` になったかを確認。
6. **コミット**
   - 1タスクごとにコミットして履歴を分ける。

---

## スクリプト設計ルール（統一）
- 対象: **単一ファイル**（引数でHTMLファイルを1つ受ける）
- コマンド: `check` / `delete`（変換の場合は `convert`）
- 終了コード（標準）
  - `0`: 成功
  - `1`: 対象なし（0件）
  - `2`: 想定外の複数件（2件以上）
  - `3`: 処理エラー
- 方針:
  - 0件をエラーにしないタスクは、仕様で明示して `0` 扱いにしてよい。
  - セレクタだけで不安定な場合は、**リンク文言**や属性を併用して誤検出を防ぐ。

---

## 実行テンプレート

### 1) docs直下でcheck
```bash
for f in /app/docs/*.html; do python3 scripts/<script_name>.py check "$f"; done
```

### 2) docs/langでcheck
```bash
for f in /app/docs/lang/*.html; do python3 scripts/<script_name>.py check "$f"; done
```

### 3) docs/viewでcheck（件数が多いので集計）
```bash
total=0 && ok=0 && missing=0 && ambiguous=0 && errors=0 && \
while IFS= read -r -d '' f; do
  out=$(python3 scripts/<script_name>.py check "$f" 2>&1); code=$?
  total=$((total+1))
  if [ $code -eq 0 ]; then ok=$((ok+1));
  elif [ $code -eq 1 ]; then missing=$((missing+1));
  elif [ $code -eq 2 ]; then ambiguous=$((ambiguous+1));
  else errors=$((errors+1)); echo "$out";
  fi
done < <(find /app/docs/view -type f -name '*.html' -print0)
echo "SUMMARY total=$total ok=$ok missing=$missing ambiguous=$ambiguous errors=$errors"
```

### 4) 再帰delete（docs全体）
```bash
while IFS= read -r -d '' f; do
  python3 scripts/<script_name>.py delete "$f"
done < <(find /app/docs -type f -name '*.html' -print0)
```

### 5) 事後check（docs全体）
```bash
while IFS= read -r -d '' f; do
  python3 scripts/<script_name>.py check "$f"
done < <(find /app/docs -type f -name '*.html' -print0)
```

---

## これまで作成したスクリプト
- `scripts/remove_login_block.py`
  - 右上ログインブロック削除
- `scripts/remove_sidebar_recent_menu_items.py`
  - サイドメニュー「人気ウンコード / 新着ウンコード / 新着コメント」削除
- `scripts/convert_fqdn_links_to_local_html.py`
  - `https://unkode-mania.net/...` を `/...html` に変換
- `scripts/remove_more_code_button.py`
  - 「もっと読む」ボタン削除
- `scripts/remove_sidebar_write_menu_items.py`
  - 「ウンコードを書く」ヘッダ + 「投稿する」項目削除

---

## 新規タスクを依頼するときのテンプレート（チャット貼り付け用）
```md
次の要素を削除したいです。
- （対象HTML断片）

要件:
1. scripts 配下に専用スクリプトを作成
2. 単一ファイル入力、check/delete を実装
3. 先に docs直下でcheck
4. その後 docs/lang, docs/view をcheck
5. 問題なければ delete 実行
6. 事後checkまで実施
```

---

## 注意点
- BeautifulSoupで保存すると、対象以外のインデント差分が発生する場合がある。
- 変換対象の判定は、URL一致よりも文言一致の方が安定するケースがある。
- `docs/view` は件数が多いため、**全文出力ではなく集計出力**を基本とする。
