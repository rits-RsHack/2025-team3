'use client';

import { useState, ChangeEvent, FormEvent } from 'react';
import { useSession } from '@/lib/auth-client';
import styles from './page.module.css';

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
);
const SpinnerIcon = () => (
  <svg className={styles.spinner} viewBox="0 0 50 50"><circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle></svg>
);

export default function SeparatorPage() {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResultUrl(null);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedFile || !session) {
      setError(!session ? 'You must be logged in to use this feature.' : 'Please select a file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResultUrl(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', session.user.id);

    try {
      const response = await fetch(`${API_BASE_URL}/api/element_divide`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Processing failed.');
      }

      // ★★★ 変更点: ダウンロードURLをstateに保存 ★★★
      setResultUrl(`${API_BASE_URL}/api/download-zip/${data.download_filename}`);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setIsLoading(false);
    setError(null);
    setResultUrl(null);
  };

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>Audio Source Separation</h1>
        <p className={styles.description}>
          Separate your audio into vocals, drums, bass, and other instruments.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label htmlFor="file-upload" className={`${styles.fileLabel} ${isLoading ? styles.disabled : ''}`}>
            <UploadIcon />
            <span>{selectedFile ? selectedFile.name : 'Select an audio file'}</span>
          </label>
          <input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            accept="audio/*"
            className={styles.fileInput}
            disabled={isLoading || isSessionLoading || !session}
          />
          <button
            type="submit"
            disabled={!selectedFile || isLoading || isSessionLoading || !session}
            className={styles.actionButton}
          >
            {isLoading ? <SpinnerIcon /> : 'Separate Audio'}
          </button>
        </form>

        {/* --- 結果表示エリア --- */}
        <div className={styles.statusArea}>
          {isSessionLoading && <p>Loading session...</p>}
          {!session && !isSessionLoading && <p className={styles.errorText}>Please log in to use this feature.</p>}
          {error && <p className={styles.errorText}>{error}</p>}

          {resultUrl && !isLoading && (
            <div className={styles.resultContainer}>
              <p>Processing complete! Your file is ready.</p>
              <a href={resultUrl} className={styles.actionButton} download>
                Download ZIP
              </a>
              <button onClick={handleReset} className={styles.secondaryButton}>Separate Another File</button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
