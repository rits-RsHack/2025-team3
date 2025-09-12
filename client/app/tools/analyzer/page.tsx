'use client';

import { useState, ChangeEvent, FormEvent, useEffect } from 'react';
import styles from './page.module.css';

// アイコンコンポーネント (UIの補助として)
const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
);
const SpinnerIcon = () => (
  <svg className={styles.spinner} viewBox="0 0 50 50"><circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle></svg>
);

// APIレスポンスの型定義
interface AnalysisResult {
  job_id: string;
  analysis: string;
}

export default function AnalyzerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState<string>('この曲の歌詞、歌い方、雰囲気を総合的に分析してください。');
  const [appStatus, setAppStatus] = useState<'idle' | 'uploading' | 'polling' | 'complete' | 'error'>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('Select an audio file and enter your request.');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setStatusMessage(`Selected file: ${file.name}`);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedFile) {
      setStatusMessage('Please select a file first.');
      setAppStatus('error');
      return;
    }

    setAppStatus('uploading');
    setStatusMessage('Uploading file...');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('prompt', prompt);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start analysis.');
      }
      setJobId(data.job_id);
      setAppStatus('polling');
      setStatusMessage(`Analysis started (Job ID: ${data.job_id}). Waiting for completion...`);
    } catch (err) {
      console.error(err);
      setStatusMessage(err instanceof Error ? err.message : 'An unknown error occurred.');
      setAppStatus('error');
    }
  };

  useEffect(() => {
    if (appStatus !== 'polling' || !jobId) return;
    const intervalId = setInterval(async () => {
      try {
        const statusResponse = await fetch(`${API_BASE_URL}/api/analysis-status/${jobId}`);
        const statusData = await statusResponse.json();
        if (statusData.status === 'complete') {
          clearInterval(intervalId);
          const resultResponse = await fetch(`${API_BASE_URL}/api/analysis-result/${jobId}`);
          const resultData = await resultResponse.json();
          if (!resultResponse.ok) {
            throw new Error(resultData.detail || 'Failed to fetch the result.');
          }
          setAnalysisResult(resultData);
          setAppStatus('complete');
          setStatusMessage('Analysis complete!');
        }
      } catch (err) {
        console.error(err);
        setStatusMessage(err instanceof Error ? err.message : 'An error occurred while checking status.');
        setAppStatus('error');
        clearInterval(intervalId);
      }
    }, 5000);
    return () => clearInterval(intervalId);
  }, [appStatus, jobId, API_BASE_URL]);

  const handleReset = () => {
    setSelectedFile(null);
    setPrompt('この曲の歌詞、歌い方、雰囲気を総合的に分析してください。');
    setAppStatus('idle');
    setJobId(null);
    setStatusMessage('Select an audio file and enter your request.');
    setAnalysisResult(null);
  };

  const renderContent = () => {
    switch (appStatus) {
      case 'polling':
        return (
          <div className={styles.statusContainer}>
            <SpinnerIcon />
            <h2 className={styles.statusTitle}>Analysis in Progress</h2>
            <p className={styles.statusText}>{statusMessage}</p>
          </div>
        );
      case 'complete':
        return (
          analysisResult && (
            <div className={styles.statusContainer}>
              <h2 className={styles.statusTitle}>Analysis Result</h2>
              <pre className={styles.resultText}>{analysisResult.analysis}</pre>
              <button onClick={handleReset} className={styles.actionButton}>Analyze Another File</button>
            </div>
          )
        );
      case 'error':
        return (
          <div className={styles.statusContainer}>
            <h2 className={`${styles.statusTitle} ${styles.errorTitle}`}>An Error Occurred</h2>
            <p className={styles.errorText}>{statusMessage}</p>
            <button onClick={handleReset} className={styles.actionButton}>Try Again</button>
          </div>
        );
      case 'idle':
      case 'uploading':
      default:
        return (
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label htmlFor="file-upload" className={styles.fileLabel}>
                <UploadIcon />
                <span>{selectedFile ? selectedFile.name : 'Select an audio file'}</span>
              </label>
              <input
                id="file-upload"
                type="file"
                onChange={handleFileChange}
                accept="audio/*,video/*" // 動画も受け付けられるように
                className={styles.fileInput}
                disabled={appStatus === 'uploading'}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="prompt" className={styles.promptLabel}>Analysis Request</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className={styles.textarea}
                rows={3}
                placeholder="e.g., Analyze the vocal technique and lyrical themes."
                disabled={appStatus === 'uploading'}
              />
            </div>
            <button
              type="submit"
              disabled={!selectedFile || appStatus === 'uploading'}
              className={styles.actionButton}
            >
              {appStatus === 'uploading' ? <SpinnerIcon /> : 'Start Analysis'}
            </button>
          </form>
        );
    }
  };

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>AI Music Analysis</h1>
        <p className={styles.description}>
          Upload an audio or video file, and our AI will analyze it based on your request.
          This process is asynchronous and may take several minutes.
        </p>
        {renderContent()}
      </div>
    </main>
  );
}
