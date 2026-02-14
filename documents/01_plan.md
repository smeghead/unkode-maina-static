# Plan: ウンコード・マニアの静的サイト化

TwitterのAPIを利用できなくなった関係で動的機能が動作しない状態となっている。
静的サイト化して、GitHub Pagesに切り替えたい。

## Steps

1. wgetで、現行サイトからコンテンツを original ディレクトリ配下に取得する。
2. original から、docs にコピーした後、不要機能部分のHTMLを一括編集することで消していく。
3. GitHub Pages で公開する。
4. DNSの変更とSSLの設定


## Implementation status

- original HTMLの取得
- docs へコピー
- docs 配下のHTMLを一括変換することで、不要機能を削除する。(未着手)
