import Link from 'next/link';
import styles from './page.module.css';

// --- 各機能のアイコンをSVGコンポーネントとして定義 ---

const ConverterIcon = () => (
  <svg className={styles.cardIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M12 18L15 15L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M9 15H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const SeparatorIcon = () => (
  <svg className={styles.cardIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M3 6H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M12 3V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="4 4" />
  </svg>
);

const RecommendIcon = () => (
  <svg className={styles.cardIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);


export default function HomePage() {
  return (
    <div className={styles.container}>


      <main className={styles.main}>
        <div className={styles.cardGrid}>
          {/* Card 1: MP4 to MP3 Converter */}
          <Link href="/tools/converter" className={styles.card}>
            <ConverterIcon />
            <h2 className={styles.cardTitle}>MP4 to MP3</h2>
            <p className={styles.cardDescription}>
              Extract audio from your video files quickly and easily.
            </p>
          </Link>

          {/* Card 2: Source Separation */}
          <Link href="/tools/separator" className={styles.card}>
            <SeparatorIcon />
            <h2 className={styles.cardTitle}>Source Separation</h2>
            <p className={styles.cardDescription}>
              Split songs into vocals, drums, bass, and other instruments.
            </p>
          </Link>

          {/* Card 3: Recommendations */}
          <Link href="/tools/analyzer" className={styles.card}>
            <RecommendIcon />
            <h2 className={styles.cardTitle}>Music Recommendation</h2>
            <p className={styles.cardDescription}>
              Discover new music based on your favorite tracks and artists.
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}
