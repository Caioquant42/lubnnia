import { Footer } from '@/components/Layout/Footer';
import { Header } from '@/components/Layout/Header';
import { Sidebar } from '@/components/Layout/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className='flex min-h-screen flex-col'>
      <div className='flex flex-1'>
        <Sidebar />
        <div className='flex flex-1 flex-col lg:ml-64'>
          <Header />
          <main className='flex-1 p-4 md:p-6'>{children}</main>
          <Footer />
        </div>
      </div>
    </div>
  );
}
