import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blinkit Flash · Discovery Analytics",
  description: "Category discovery and consideration barriers in Indian quick commerce.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#0B0D0A", fontFamily: 'ui-sans-serif, -apple-system, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}
