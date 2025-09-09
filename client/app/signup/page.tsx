'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signUp } from '@/lib/auth-client';
import styles from './page.module.css';

export default function SignUpPage() {
  const router = useRouter();
  const [username, setUsername] = useState(''); // このstateを使います
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      // ★★★★★ ここを修正 ★★★★★
      // 'username' stateの値を 'name' プロパティとして渡す
      const result = await signUp.email({
        email: email,
        password: password,
        name: username,
      });

      if (result.error) {
        setError(result.error.message ?? 'An unknown error occurred.');
      } else {
        router.push('/dashboard');
      }

    } catch (e) {
      console.error(e);
      setError('An unexpected network error occurred.');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.formContainer}>
        <h1 className={styles.title}>Create Your Account</h1>
        <p className={styles.subtitle}>Join Audily and start listening.</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Usernameの入力欄 (この値が 'username' state に保存される) */}
          <div className={styles.inputGroup}>
            <label htmlFor="username" className={styles.label}>Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.input}
              required
            />
          </div>

          {/* ... email, password, confirmPassword の input は変更なし ... */}
          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.label}>Email Address</label>
            <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} className={styles.input} required />
          </div>
          <div className={styles.inputGroup}>
            <label htmlFor="password" className={styles.label}>Password</label>
            <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} className={styles.input} minLength={8} required />
          </div>
          <div className={styles.inputGroup}>
            <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
            <input type="password" id="confirmPassword" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className={styles.input} minLength={8} required />
          </div>

          {error && <p className={styles.errorText}>{error}</p>}

          <button type="submit" className={styles.submitButton}>
            Sign Up
          </button>
        </form>

        <p className={styles.loginLink}>
          Already have an account?{' '}
          <Link href="/login">Log In</Link>
        </p>
      </div>
    </div>
  );
}
