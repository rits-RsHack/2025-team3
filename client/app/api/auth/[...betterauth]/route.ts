import { auth } from "@/lib/auth"; // lib/auth.ts から auth インスタンスをインポート

// authインスタンスのhandlerプロパティをGETとPOSTに割り当てる
export const GET = auth.handler;
export const POST = auth.handler;
