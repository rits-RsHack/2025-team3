import { auth } from "@/lib/auth"; // lib/auth.ts から auth インスタンスをインポート

export const GET = auth.handler;
export const POST = auth.handler;
