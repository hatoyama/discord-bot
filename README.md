# Discord Bot (Hello World)

Python と `discord.py` を使用した Discord Bot です。
スラッシュコマンド `/hello` またはテキストコマンド `!hello` を送信すると、「Hello World!」と返答します。

---

## 機能一覧

- **/hello (スラッシュコマンド)**: `Hello World!` と返答します。
- **!hello (テキストコマンド)**: `Hello World!` と返答します。

---

## セットアップ手順

### 1. 前提条件の準備 (Discord Developer Portal)

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、ログインします。
2. 右上の **New Application** をクリックし、アプリケーション名を入力して作成します。
3. 左メニューの **Bot** を選択します。
4. **Token** セクションで **Reset Token** をクリックし、表示されたトークンをコピーして控えておきます。
5. 同じページの **Privileged Gateway Intents** セクションで、以下の設定を有効（ON）にします:
   - **Message Content Intent** (テキストコマンド `!hello` 等を受信するために必要)
6. 左メニューの **OAuth2** > **OAuth2 URL Generator** を開きます:
   - **SCOPES**: `bot`, `applications.commands` にチェック
   - **BOT PERMISSIONS**: `Send Messages`, `Read Messages/View Channels` など必要な権限にチェック
7. ページ下部に生成された **Generated URL** をブラウザで開き、Botを追加したいDiscordサーバーに招待します。

---

### 2. 環境設定 (.env)

プロジェクトルートの `.env` ファイルに、先ほど取得したBotトークンを設定します。

```env
DISCORD_TOKEN=ここに取得したBotトークンを貼り付け
```

※ テンプレートとして `.env.example` が用意されています。

---

### 3. ライブラリのインストール

仮想環境を作成し、必要なライブラリをインストールします。

```powershell
# 仮想環境の作成 (未作成の場合)
python -m venv .venv

# 仮想環境の有効化 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

### 4. Botの起動

```powershell
python main.py
```

#### 期待される結果 (コンソール表示)
```text
[YYYY-MM-DD HH:MM:SS] [INFO] discord.client: logging in using static token
[YYYY-MM-DD HH:MM:SS] [INFO] discord.gateway: Shard ID None has connected to Gateway ...
[YYYY-MM-DD HH:MM:SS] [INFO] discord_bot: ログイン完了: <Botの名前> (ID: <BotのID>)
[YYYY-MM-DD HH:MM:SS] [INFO] discord_bot: スラッシュコマンド同期完了: 1 件のコマンドを同期しました。
[YYYY-MM-DD HH:MM:SS] [INFO] discord_bot: Botは現在待機中です。メッセージまたはコマンドを受信できます。
```

---

### 5. 動作確認

Botがオンラインになったら、招待したDiscordサーバーのテキストチャンネルで以下の操作を行います:

1. **スラッシュコマンド**:
   - `/hello` と入力して送信
   - 期待結果: Botが `Hello World!` と返信します。
2. **プレフィックスコマンド**:
   - `!hello` と入力して送信
   - 期待結果: Botが `Hello World!` と返信します。
