import Link from "next/link";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/icps", label: "ICPs" },
  { href: "/leads", label: "Leads" },
  { href: "/marketplace", label: "Marketplace" },
];

export function Nav() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-3">
        <Link href="/" className="text-base font-semibold tracking-tight">
          Lead Gen Agency
        </Link>
        <nav className="flex items-center gap-4 text-sm text-slate-600">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="hover:text-slate-900 hover:underline"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
