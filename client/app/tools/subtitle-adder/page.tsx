'use client';

import { useState, useEffect, FormEvent, ChangeEvent, useRef } from 'react';
import { useSession } from '@/lib/auth-client';
import styles from './page.module.css';

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
);
const SpinnerIcon = () => (
  <svg className={styles.spinner} viewBox="0 0 50 50"><circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle></svg>
);

export default function SubtitleAdderPage() {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle'); // idle, uploading, processing, complete, error
  const [progressDetail, setProgressDetail] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';


  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.type.startsWith('video/')) {
        setError('Please select a valid video file.');
        setFile(null);
        return;
      }
      resetState(false);
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) {
      setError('No file selected.');
      return;
    }
    if (!session) {
      setError('You must be logged in to use this feature.');
      return;
    }

    resetState(false);
    setStatus('uploading');
    setProgressDetail('Uploading file...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', session.user.id);

    try {
      const response = await fetch(`${API_BASE_URL}/api/add-subtitle`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed with an unknown server error.' }));
        throw new Error(errorData.detail);
      }

      const result = await response.json();
      setJobId(result.job_id);
      setStatus('processing');
      setProgressDetail('Request accepted. Starting the process...');

    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'An unexpected error occurred during upload.');
    }
  };

  const handleDownload = async () => {
    if (!jobId) return;

    setIsDownloading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/download-subtitled-video/${jobId}`);
      if (!response.ok) {
        throw new Error('Download failed. The file may have been cleaned up or does not exist.');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `subtitled_${jobId}.mp4`);
      document.body.appendChild(link);
      link.click();

      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not download the file.');
    } finally {
      setIsDownloading(false);
    }
  };

  const resetState = (resetFile = true) => {
    stopPolling();
    if (resetFile) {
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
    setJobId(null);
    setStatus('idle');
    setProgressDetail('');
    setError(null);
    setIsDownloading(false);
  };

  useEffect(() => {
    if (status !== 'processing' || !jobId) {
      return;
    }

    intervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/subtitle-status/${jobId}`);
        if (!response.ok) throw new Error('Failed to communicate with the server.');

        const data = await response.json();
        if (data.status === 'complete') {
          stopPolling();
          setStatus('complete');
          setProgressDetail('Subtitle generation is complete!');
        } else if (data.status === 'error') {
          stopPolling();
          setStatus('error');
          setError(data.detail || 'An unknown error occurred.');
        } else {
          setProgressDetail(data.detail || 'Processing...');
        }
      } catch (err) {
        stopPolling();
        setStatus('error');
        setError(err instanceof Error ? err.message : 'An error occurred while checking the status.');
      }
    }, 5000);

    return () => stopPolling();
  }, [status, jobId]);


  const renderContent = () => {
    if (isSessionLoading) {
      return <div className={styles.statusContainer}><SpinnerIcon /></div>;
    }

    if (status === 'uploading' || status === 'processing') {
      return (
        <div className={styles.statusContainer}>
          <SpinnerIcon />
          <p className={styles.progressDetail}>{progressDetail}</p>
          {status === 'processing' && <small className={styles.notice}>This process may take a few minutes. Please do not close the page.</small>}
        </div>
      );
    }

    if (status === 'complete' && jobId) {
      return (
        <div className={styles.statusContainer}>
          <h2 className={styles.completeTitle}>Processing Complete!</h2>
          <p>{progressDetail}</p>
          <button onClick={handleDownload} className={styles.downloadLink} disabled={isDownloading}>
            {isDownloading ? <SpinnerIcon /> : 'Download Subtitled Video'}
          </button>
          <button onClick={() => resetState(true)} className={styles.resetButton}>
            Try Another Video
          </button>
        </div>
      );
    }

    if (status === 'error') {
      return (
        <div className={styles.errorContainer}>
          <p className={styles.errorMessage}>Error: {error}</p>
          <button onClick={() => resetState(true)} className={styles.resetButton}>
            Try Again
          </button>
        </div>
      );
    }

    return (
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.fileInputWrapper}>
          <input
            ref={fileInputRef} id="file-input" type="file"
            accept="video/mp4,video/quicktime" onChange={handleFileChange}
            className={styles.fileInput} disabled={!session}
          />
          <label htmlFor="file-input" className={!session ? `${styles.fileInputLabel} ${styles.disabled}` : styles.fileInputLabel}>
            {file ? file.name : 'Choose a file (.mp4, .mov)'}
          </label>
        </div>
        <button type="submit" className={styles.submitButton} disabled={!file || !session}>
          Start Generating Subtitles
        </button>
        {!session && <p className={styles.errorMessage}>Please log in to use this feature.</p>}
      </form>
    );
  };


  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Video Subtitle Generator</h1>
        <p className={styles.description}>
          Upload a video file, and AI will automatically transcribe the audio and burn the subtitles into the video.
        </p>
        <div className={styles.contentWrapper}>
          {renderContent()}
        </div>
      </div>
    </main>
  );
}
