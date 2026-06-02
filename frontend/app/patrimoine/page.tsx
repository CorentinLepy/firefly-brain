import Link from "next/link";
import { apiGet } from "../../lib/api";

type WealthAccount = { id: string; name: string; type: string; role: string | null; balance: number; currency: string };
type WealthResponse = { gross_assets: number; total_liabilities: number; net_worth: number; assets_count: number; liabilities_count: number; assets: WealthAccount[]; liabilities: WealthAccount[] };
function money(value: number) { return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value || 0); }

export default async function WealthPage() {
  const data = await apiGet<WealthResponse>("/api/wealth/summary");
  return (
    <main className="page">
      <nav className="topnav"><strong>Firefly Brain V2.1</strong><Link href="/">Dashboard</Link><Link href="/abonnements">Abonnements</Link><Link href="/alertes">Alertes</Link></nav>
      <section className="header compact"><div><div className="eyebrow">Patrimoine</div><h1>Actifs, dettes et patrimoine net</h1><p>Basé sur les comptes Firefly III inclus dans le patrimoine net.</p></div></section>
      <section className="hero-grid"><div className="card hero-card"><div className="label">Patrimoine net</div><div className="hero-value">{money(data.net_worth)}</div></div><div className="card hero-card"><div className="label">Actifs</div><div className="hero-value">{money(data.gross_assets)}</div><p>{data.assets_count} compte(s)</p></div><div className="card hero-card"><div className="label">Dettes</div><div className="hero-value">{money(data.total_liabilities)}</div><p>{data.liabilities_count} compte(s)</p></div></section>
      <section className="section"><div className="card"><h2>Actifs</h2><div className="list">{data.assets.map((item) => <div className="row line" key={item.id}><span>{item.name}</span><strong>{money(item.balance)}</strong></div>)}</div></div><div className="card"><h2>Dettes</h2><div className="list">{data.liabilities.map((item) => <div className="row line" key={item.id}><span>{item.name}</span><strong>{money(Math.abs(item.balance))}</strong></div>)}</div></div></section>
    </main>
  );
}
