# Proxy設定のベストプラクティス

## 概要
このプロジェクトでは、開発環境とDocker環境で異なるAPIエンドポイント設定の問題を解決するために、環境変数ベースのアプローチを採用しました。

## 変更内容

### 1. apiService.tsの修正
- 本番環境では環境変数 `REACT_APP_API_URL` をベースURLとして使用
- 開発環境では空文字でpackage.jsonのproxy設定を利用
- Docker環境: `http://backend:8000` (docker-compose.ymlで設定)

### 2. package.jsonのproxy設定修正
- `"proxy": "http://localhost:8000"` に変更
- 開発環境でのみ使用されるため、localhostを指定

## 動作原理

### 開発環境 (npm start)
1. apiService.tsが空文字をベースURLとして使用
2. package.jsonのproxy設定が開発サーバーのプロキシ機能として動作
3. すべてのAPIリクエストがlocalhost:8000にプロキシされる

### Docker環境 (docker-compose up)
1. docker-compose.ymlで `REACT_APP_API_URL=http://backend:8000` を設定
2. apiService.tsがこのURLをベースとしてAPI呼び出し
3. コンテナ間通信でbackendサービスに直接アクセス

## メリット

1. **一貫性**: すべての環境で同じ設定方法を使用
2. **柔軟性**: 環境変数で簡単に設定変更可能
3. **メンテナンス性**: 設定が一元化され管理が容易
4. **拡張性**: 新しい環境の追加が簡単

## 使用方法

### 開発環境で起動
```bash
cd frontend
npm start
```

### Docker環境で起動
```bash
docker-compose up
```

### カスタム環境変数の設定
```bash
# 一時的な環境変数の設定
REACT_APP_API_URL=http://your-custom-api:8000 npm start

# または .env.local ファイルを作成
echo "REACT_APP_API_URL=http://your-custom-api:8000" > frontend/.env.local
```

## トラブルシューティング

### API接続エラーが発生する場合
1. バックエンドサーバーが起動しているか確認
2. 環境変数が正しく設定されているか確認
3. ネットワーク設定を確認

### Docker環境で接続できない場合
1. コンテナ間ネットワークが正しく設定されているか確認
2. backendサービスが正常に起動しているか確認

## 参考資料
- [Create React App環境変数](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [Docker Compose環境変数](https://docs.docker.com/compose/environment-variables/)
