import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";

// Inter (the app's typeface), self-hosted from @fontsource-variable/inter: no network at build or run time.
const inter = localFont({
  src: "../node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2",
  variable: "--font-inter",
  weight: "100 900",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Local Speech-to-Speech",
  description:
    "Real-time spoken conversations with a local AI assistant, with every model running on your Mac.",
};

export const viewport: Viewport = {
  themeColor: "#111821",
  colorScheme: "dark",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
