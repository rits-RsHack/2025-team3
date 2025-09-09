import Header from '@/components/Header';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <Header />
      {/* ヘッダーが固定されているので、メインコンテンツが隠れないようにpaddingを追加 */}
      <main style={{ paddingTop: '80px' }}>
        {children}
      </main>
    </div>
  );
}
