import Link from 'next/link';
import styles from './page.module.css';

// SVGコンポーネントとしてロゴを定義（ファイルをインポートしても良い）
const AudilyLogo = () => (
  <svg width="120" height="40" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="30" fontFamily="'Inter', sans-serif" fontSize="32" fontWeight="900" fill="white">
      Audily
    </text>
  </svg>
);

export default function LandingPage() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <AudilyLogo />
      </header>

      <main className={styles.main}>
        <div className={styles.heroContent}>
          <h1 className={styles.title}>
            Your sound, <br />
            reimagined.
          </h1>
          <p className={styles.subtitle}>
            Dive into a seamless audio experience. Join millions of listeners
            and creators on Audily today.
          </p>
          <div className={styles.ctaContainer}>
            <Link href="/signup" className={`${styles.button} ${styles.buttonPrimary}`}>
              Sign Up for Free
            </Link>
            <Link href="/login" className={`${styles.button} ${styles.buttonSecondary}`}>
              Log In
            </Link>
          </div>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>&copy; {new Date().getFullYear()} Audily Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}
