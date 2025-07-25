# アクティブコンテキスト

## プロジェクト
株式分析システム

## 現在の作業
- プロトタイプの安定化と改善
- 日本語フォント表示問題の解決
- レポート自動更新システムの設計

## 直近の変更
- stock_data_importer.py: データ取得ロジックの最適化
- stock_analyzer.py: RSI指標の追加実装
- レポート生成: 複数銘柄比較機能の追加
- メモリバンクファイルの整合性向上
- requirements.txt: 依存関係の更新（certifi, fonttools, multitasking, numpy）

## 次のステップ
1. matplotlibの日本語フォント設定を修正
2. タスクスケジューラによる定期実行機能の実装
3. 新しいテクニカル指標（MACD）の追加
4. レポートテンプレートのカスタマイズ機能開発

## 検討事項
- データ更新戦略（リアルタイム vs バッチ）
- 追加データソースの統合（Alpha Vantageなど）
- クラウドストレージへのバックアップ実装

## 重要な決定
- 本番環境DBとしてPostgreSQLを継続採用
- Yahoo Finance APIを主要データソースとして維持
- 対象銘柄を拡大（任天堂(7974.T)を追加予定）

## 学習事項
- Matplotlibの詳細なカスタマイズ方法
- PostgreSQLのバックアップと復旧戦略
- pandasを使った大規模データ処理の最適化
- テクニカル指標計算の数学的基礎
- Windows環境での依存関係管理のベストプラクティス

## 2025-07-26
### 課題
- フロントエンドの株式一覧テーブルが中央寄せにならない問題が発生中
- 複数の修正を試みたが未解決

### 次のアクション
- テーブル中央寄せ問題の調査を継続
