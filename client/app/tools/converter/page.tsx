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

export default function ConverterPage() {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'video/mp4') {
        setError('Please select a valid MP4 file.');
        setSelectedFile(null);
        return;
      }
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
    if (!session) {
      setError('You must be logged in to use this feature.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatusMessage('Uploading and converting... This may take a moment.');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', session.user.id);

    try {
      const response = await fetch(`${API_BASE_URL}/api/mp4-to-mp3`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Conversion failed with status: ${response.status}`);
      }

      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'converted.mp3';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch?.[1]) {
          filename = filenameMatch[1];
        }
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      setStatusMessage('Conversion complete! Your download has started.');

    } catch (err) {
      console.error('Conversion error:', err);
      setError(err instanceof Error ? `Error: ${err.message}` : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderForm = () => {
    if (isSessionLoading) {
      return <div className={styles.statusArea}><SpinnerIcon /></div>;
    }

    return (
      <form onSubmit={handleSubmit} className={styles.form}>
        <label htmlFor="file-upload" className={`${styles.fileLabel} ${isLoading ? styles.disabled : ''}`}>
          <UploadIcon />
          <span>{selectedFile ? selectedFile.name : 'Select an MP4 file'}</span>
        </label>
        <input
          id="file-upload"
          type="file"
          onChange={handleFileChange}
          accept="video/mp4"
          className={styles.fileInput}
          disabled={isLoading || !session}
        />

        <button
          type="submit"
          disabled={!selectedFile || isLoading || !session}
          className={styles.submitButton}
        >
          {isLoading ? <SpinnerIcon /> : 'Convert & Download'}
        </button>
      </form>
    );
  }

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>MP4 to MP3 Converter</h1>
        <p className={styles.description}>
          Upload your MP4 video file to extract the audio track as a high-quality MP3 file.
        </p>

        {renderForm()}

        <div
          className={`
            ${styles.statusArea} 
            ${error || (!session && !isSessionLoading) ? styles.hasError : ''}
          `}
        >
          {error && (
            <p className={styles.errorMessage}>{error}</p>
          )}
          {!error && statusMessage && (
            <p className={styles.statusMessage}>{statusMessage}</p>
          )}
          {!session && !isSessionLoading && (
            <p className={styles.errorMessage}>Please log in to use the converter.</p>
          )}
        </div>
      </div>
    </main>
  );
}
