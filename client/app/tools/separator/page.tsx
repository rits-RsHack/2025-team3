'use client';

import { useState, ChangeEvent, FormEvent } from 'react';
import styles from './page.module.css';

// アイコンコンポーネント (UIの補助として)
const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
);
const SpinnerIcon = () => (
  <svg className={styles.spinner} viewBox="0 0 50 50"><circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle></svg>
);

export default function SeparatorPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('Select an audio file to begin.');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // FastAPIサーバーのURL
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setStatusMessage(`Selected file: ${file.name}`);
      setError(null);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatusMessage('Uploading and processing... This may take several minutes. Please do not close this page.');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/element_divide`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // エラーレスポンスがJSON形式の場合、詳細を取得
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Processing failed with status: ${response.status}`);
      }

      // レスポンスからファイル名を取得
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'separated_audio.zip'; // デフォルトのファイル名
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }

      // レスポンスボディをBlobとして取得
      const blob = await response.blob();

      // Blobから一時URLを生成し、ダウンロードをトリガー
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // 後処理
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      setStatusMessage('Processing complete! Your download has started.');

    } catch (err) {
      console.error('Processing error:', err);
      if (err instanceof Error) {
        setError(`Error: ${err.message}`);
      } else {
        setError('An unknown error occurred during processing.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>Audio Source Separation</h1>
        <p className={styles.description}>
          Upload your audio file (MP3, WAV, etc.) to separate it into vocals, drums, bass, piano, and other stems.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label htmlFor="file-upload" className={styles.fileLabel}>
            <UploadIcon />
            <span>{selectedFile ? 'Change file' : 'Select a file'}</span>
          </label>
          <input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            accept="audio/*"
            className={styles.fileInput}
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!selectedFile || isLoading}
            className={styles.submitButton}
          >
            {isLoading ? <SpinnerIcon /> : 'Separate & Download'}
          </button>
        </form>

        <div className={styles.statusArea}>
          {error ? (
            <p className={styles.errorMessage}>{error}</p>
          ) : (
            <p className={styles.statusMessage}>{statusMessage}</p>
          )}
        </div>
      </div>
    </main>
  );
}
