import {ClerkProvider} from "@clerk/nextjs";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { RootProviders } from "@/providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Child pages set their own fully-branded titles (e.g. "Dashboard - FinPilot AI"),
// so no title template is used here - it would double up the brand.
export const metadata: Metadata = {
  title: "FinPilot AI",
  description: "FinPilot AI — Intelligent Wealth Management.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <body>
        <ClerkProvider>
          <RootProviders>
          {children}
          </RootProviders>
        </ClerkProvider>
      </body>
    </html>
  );
}