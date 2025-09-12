'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signIn } from '@/lib/auth-client';
import styles from './page.module.css';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      const result = await signIn.email({ email, password });

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
        <h1 className={styles.title}>Welcome Back</h1>
        <p className={styles.subtitle}>Log in to your Audily account.</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* ... input fields for email and password ... */}
          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.label}>Email Address</label>
            <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} className={styles.input} required />
          </div>
          <div className={styles.inputGroup}>
            <div className={styles.passwordHeader}>
              <label htmlFor="password" className={styles.label}>Password</label>
            </div>
            <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} className={styles.input} required />
          </div>

          {error && <p className={styles.errorText}>{error}</p>}
          <button type="submit" className={styles.submitButton}>Log In</button>
        </form>
        <p className={styles.signupLink}>
          Don&apos;t have an account? <Link href="/signup">Sign Up</Link>
        </p>
      </div>
    </div>
  );
}
