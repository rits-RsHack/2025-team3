import { betterAuth } from "better-auth";
import Database from "better-sqlite3";

// データベースに接続 (ファイルがなければ自動作成される)
const db = new Database("./audily.db");

// betterAuthのインスタンスを作成し、'auth'という名前でエクスポート
export const auth = betterAuth({
  database: db,
  emailAndPassword: {
    enabled: true, // メール・パスワード認証を有効化
  },
});

