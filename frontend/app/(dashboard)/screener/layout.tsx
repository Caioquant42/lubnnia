import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Screener - Zomma Quant",
  description: "Ferramentas de screener para análise técnica e fundamental",
};

interface ScreenerLayoutProps {
  children: React.ReactNode;
}

export default function ScreenerLayout({ children }: ScreenerLayoutProps) {
  return (
    <div className="flex-1 space-y-4">
      {children}
    </div>
  );
}