'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useSession, signOut } from '@/lib/auth-client';
import styles from './Header.module.css';
import { useRouter } from 'next/navigation';
const UserIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 16.7909 18.2091 15 16 15H8C5.79086 15 4 16.7909 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /><path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
);
const SettingsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12.2218 21.8888V19.8288M12.2218 19.8288C14.4148 19.7488 16.1438 18.7988 17.2048 17.1888C18.2658 15.5788 18.5608 13.5988 18.2198 11.6488C17.8788 9.69882 16.8928 7.96882 15.4278 6.79882C13.9628 5.62882 12.1158 5.14882 10.2118 5.48882C8.30783 5.82882 6.56783 6.94882 5.50083 8.54882C4.43383 10.1488 4.14883 12.1088 4.71783 13.9288" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
);
const SignOutIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /><path d="M16 17L21 12L16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /><path d="M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
);


export default function Header() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [dropdownRef]);


  const handleSignOut = async () => {
    await signOut();
    setIsDropdownOpen(false);
    router.push('/');
  };

  const logoHref = session ? "/dashboard" : "/";

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link href={logoHref} className={styles.logo}>Audily</Link>
        <nav className={styles.nav}>
          {isPending ? (
            <div className={styles.skeleton} />
          ) : session ? (
            <div className={styles.userMenuContainer} ref={dropdownRef}>
              <button
                className={styles.userButton}
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                aria-haspopup="true"
                aria-expanded={isDropdownOpen}
              >
                <UserIcon />
              </button>
              {isDropdownOpen && (
                <div className={styles.dropdownMenu}>
                  <div className={styles.dropdownHeader}>
                    <span className={styles.username}>{session.user.name || 'User'}</span>
                    <span className={styles.email}>{session.user.email}</span>
                  </div>
                  <ul>
                    <li>
                      <Link href="/history" className={styles.dropdownItem} onClick={() => setIsDropdownOpen(false)}>
                        <SettingsIcon /> History
                      </Link>
                    </li>
                    <li>
                      <button onClick={handleSignOut} className={styles.dropdownItem}>
                        <SignOutIcon /> Sign Out
                      </button>
                    </li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <Link href="/login" className={styles.loginButton}>Log In</Link>
          )}
        </nav>
      </div>
    </header>
  );
}
