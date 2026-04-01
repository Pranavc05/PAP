import Link from "next/link";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/learn", label: "Learning Path" },
  { href: "/workflows", label: "Workflow Lab" }
];

export function TopNav() {
  return (
    <header
      style={{
        padding: "16px 24px",
        borderBottom: "1px solid #e2e8f0",
        background: "#ffffff",
        position: "sticky",
        top: 0
      }}
    >
      <nav
        style={{
          display: "flex",
          gap: 16,
          maxWidth: 960,
          margin: "0 auto",
          alignItems: "center"
        }}
      >
        <strong>Process AI Academy</strong>
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
