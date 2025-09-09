'use client';

import { createAuthClient } from 'better-auth/react';

const authClient = createAuthClient();

// 必要な関数とフックのみをエクスポートします
export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
