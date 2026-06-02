import Link from "next/link";
import { apiGet } from "../../lib/api";

type Tx = { id: string; type: string; date: string; description: string; amount: string; currency: string; merchant: string; category: string | null; budget: string | null };
type TxResponse = { count: number; items: Tx[]; pagination: { total?: number; current_page?: number; total_pages?: number } };
function money(value: string) { return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(Number(value || 0)); }

export default async function TransactionsPage() {
  const data = await apiGet<TxResponse>("/api/transactions/simple?start=2026-05-01&end=2026-05-31");
  return (
    <main className="page">
      <nav className="topnav"><strong>Firefly Brain V2.1</strong><Link href="/">Dashboard</Link><Link href="/abonnements">Abonnements</Link><Link href="/alertes">Alertes</Link><Link href="/patrimoine">Patrimoine</Link></nav>
      <section className="header compact"><div><div className="eyebrow">Transactions</div><h1>Transactions simplifiées</h1><p>Page {data.pagination?.current_page ?? 1} / {data.pagination?.total_pages ?? 1} — {data.pagination?.total ?? data.count} transaction(s)</p></div></section>
      <section className="section single"><div className="card"><div className="table"><div className="table-row five head"><span>Date</span><span>Marchand</span><span>Catégorie</span><span>Type</span><span>Montant</span></div>{data.items.slice(0, 50).map((tx) => <div className="table-row five" key={tx.id}><span>{tx.date?.slice(0,10)}</span><span>{tx.merchant || tx.description}</span><span>{tx.category || "Sans catégorie"}</span><span>{tx.type}</span><strong>{money(tx.amount)}</strong></div>)}</div></div></section>
    </main>
  );
}
