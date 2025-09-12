'use client';

import { useState, useEffect } from 'react';
import { useSession } from '@/lib/auth-client';
import styles from './page.module.css';
import Link from 'next/link';

interface HistoryItem {
  id: number;
  operation_type: string;
  source_filename: string;
  status: string;
  created_at: string;
}

const SpinnerIcon = () => (
  <svg className={styles.spinner} viewBox="0 0 50 50"><circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle></svg>
);

const formatDateTime = (isoString: string) => {
  if (!isoString) return 'N/A';

  try {
    const date = new Date(isoString);
    const formatter = new Intl.DateTimeFormat('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'Asia/Tokyo',
      hour12: false,
    });
    return formatter.format(date).replace(/\//g, '/');
  } catch (error) {
    console.error("Invalid date format:", isoString);
    return 'Invalid Date';
  }
};


export default function HistoryPage() {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!isSessionLoading && session) {
      const fetchHistory = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const response = await fetch(`${API_BASE_URL}/api/history/${session.user.id}`);
          if (!response.ok) {
            throw new Error('Failed to fetch history data.');
          }
          const data = await response.json();
          setHistory(data);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        } finally {
          setIsLoading(false);
        }
      };
      fetchHistory();
    } else if (!isSessionLoading && !session) {
      setIsLoading(false);
    }
  }, [session, isSessionLoading, API_BASE_URL]);

  const renderContent = () => {
    if (isLoading || isSessionLoading) {
      return <div className={styles.centered}><SpinnerIcon /></div>;
    }

    if (error) {
      return <div className={`${styles.centered} ${styles.errorText}`}>{error}</div>;
    }

    if (!session) {
      return (
        <div className={styles.centered}>
          <p>Please <Link href="/login" className={styles.loginLink}>log in</Link> to view your history.</p>
        </div>
      );
    }

    if (history.length === 0) {
      return <div className={styles.centered}><p>No operation history found.</p></div>;
    }

    return (
      <div className={styles.historyList}>
        {history.map((item) => (
          <div key={item.id} className={styles.historyItem}>
            <div className={styles.itemHeader}>
              <span className={styles.operationType}>{item.operation_type.replace(/_/g, ' ')}</span>
              <span className={`${styles.status} ${styles[`status_${item.status.split(':')[0]}`]}`}>
                {item.status.split(':')[0]}
              </span>
            </div>
            <p className={styles.filename}>{item.source_filename}</p>
            <p className={styles.timestamp}>
              {formatDateTime(item.created_at)}
            </p>
          </div>
        ))}
      </div>
    );
  };

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>Operation History</h1>
        {renderContent()}
      </div>
    </main>
  );
}
