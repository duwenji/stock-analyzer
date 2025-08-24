FROM node:18-alpine

WORKDIR /app

# パッケージファイルのコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install --legacy-peer-deps

# ソースコードのコピー
COPY . .

# ビルド
RUN npm run build

# ポートの公開
EXPOSE 3000

# アプリケーションの起動
CMD ["npm", "start"]
