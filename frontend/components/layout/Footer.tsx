import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t py-4 md:py-6">
      <div className="container flex flex-col items-center justify-between gap-4 md:flex-row">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>© 2025 Zommaquant. Feito por praticantes, para praticantes.</span>
        </div>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <Link href="/terms" className="hover:text-foreground">
            Termos
          </Link>
          <Link href="/privacy" className="hover:text-foreground">
            Privacidade
          </Link>
          <Link href="/help" className="hover:text-foreground">
            Ajuda
          </Link>
        </nav>
      </div>
    </footer>
  );
}