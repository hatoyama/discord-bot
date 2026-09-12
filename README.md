# Discord Bot (Hello World & 東京の天気予報通知)

Python と `discord.py` を使用した Discord Bot です。
挨拶機能に加え、**毎朝7時（JST）に東京の今日の天気予報を自動通知** します。

---

## 機能一覧

- **/weather (スラッシュコマンド)**: 今日の東京の天気予報（天気・最高最低気温・降水確率・傘アドバイス）を即座に表示します。
- **/set_weather_channel (スラッシュコマンド)**: コマンドを実行したチャンネルを毎朝7時の天気通知先に登録します。
- **/hello (スラッシュコマンド)**: `Hello World!` と返答します。
- **!weather / !set_weather_channel / !hello**: プレフィックス `!` によるテキストコマンドにも対応しています。
- **毎朝7:00 (JST) 自動通知**: 登録されたチャンネルに東京の天気予報カードを毎朝自動送信します。

---

## セットアップ手順

### 1. 前提条件の準備 (Discord Developer Portal)

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、ログインします。
2. アプリケーションを選択（または作成）し、左メニューの **Bot** を選択します。
3. **Token** セクションで **Reset Token** をクリックし、Botトークンをコピーします。
4. 同じページの **Privileged Gateway Intents** セクションで以下を有効（ON）にします:
   - **Message Content Intent** (テキストコマンド等を受信するために必要)
5. 左メニューの **OAuth2** > **OAuth2 URL Generator** を開きます:
   - **SCOPES**: `bot`, `applications.commands` にチェック
   - **BOT PERMISSIONS**: `Send Messages`, `Embed Links`, `Read Messages/View Channels` 等にチェック
6. ページ下部の **Generated URL** をブラウザで開き、Botをサーバーに招待します。

---

### 2. 環境設定 (.env)

プロジェクト直下の `.env` ファイルに、取得したBotトークンを設定します。

```env
DISCORD_TOKEN=ここに取得したBotトークンを貼り付け

# (任意) 事前に通知先チャンネルIDを固定したい場合
# DISCORD_CHANNEL_ID=123456789012345678
```

※ チャンネルIDは、後からDiscord上で `/set_weather_channel` コマンドを使って手軽に設定することも可能です。

---

### 3. ライブラリのインストール

```powershell
# 仮想環境の有効化 (未作成の場合は python -m venv .venv を実行)
.\.venv\Scripts\Activate.ps1

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

### 4. Botの起動

```powershell
.\.venv\Scripts\python main.py
```

#### 期待される起動ログ
```text
[INFO] discord.client: logging in using static token
[INFO] discord.gateway: Shard ID None has connected to Gateway ...
[INFO] discord_bot: ログイン完了: <Bot名> (ID: <BotID>)
[INFO] discord_bot: スラッシュコマンド同期完了: 3 件のコマンドを同期しました。
[INFO] discord_bot: 朝7時定期通知タスクを開始しました (設定時刻: 07:00 JST)。
[INFO] discord_bot: Botは現在待機中です。メッセージまたはコマンドを受信できます。
```

---

### 5. 動作確認

1. **即時天気確認**:
   - サーバー内のチャンネルで `/weather` を送信します。
   - 期待結果: 東京の今日の天気予報（天気・気温・降水確率・傘のアドバイス）がカード（Embed）で返信されます。
2. **毎朝7時の通知先チャンネル登録**:
   - 毎朝通知を受け取りたいチャンネルで `/set_weather_channel` を送信します。
   - 期待結果: 「✅ 毎朝7時の東京天気通知先を **#チャンネル名** に設定しました！」と返答され、設定が保存されます。
3. **挨拶コマンド**:
   - `/hello` を送信すると `Hello World!` と返信されます。
