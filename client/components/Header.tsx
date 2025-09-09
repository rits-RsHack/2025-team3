import Link from 'next/link';
import styles from './Header.module.css';

// 簡略化したロゴ
const AudilyLogo = () => (
  <Link href="/" className={styles.logo}>
    Audily
  </Link>
);

// ユーザーアイコン
const UserIcon = () => (
  <svg className={styles.userIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 21V19C20 16.7909 18.2091 15 16 15H8C5.79086 15 4 16.7909 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);


export default function Header() {
  const isLoggedIn = true;

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <AudilyLogo />
        <nav>
          {isLoggedIn ? (
            <div className={styles.userMenu}>
              <UserIcon />
            </div>
          ) : (
            <Link href="/login" className={styles.loginButton}>Log In</Link>
          )}
        </nav>
      </div>
    </header>
  );
}
