import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { GovernmentFooter } from "@/components/layout/government-footer";
import { GovernmentHeader } from "@/components/layout/government-header";
import { LanguageProvider } from "@/components/layout/language-provider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin", "latin-ext"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TRISETU | Scholarship Verification",
  description: "AI-enabled scholarship and fellowship verification workflow prototype for Scheduled Tribes.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={geistSans.variable + " " + geistMono.variable + " h-full antialiased"}>
      <body className="min-h-full flex flex-col bg-slate-50">
        <LanguageProvider>
          <GovernmentHeader />
          <div id="main-content" className="flex min-h-0 flex-1 flex-col">
            {children}
          </div>
          <GovernmentFooter />
        </LanguageProvider>
      </body>
    </html>
  );
}
