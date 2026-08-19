import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Portfolio Brief v0.1",
  description: "The first portfolio optimization vertical slice",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
