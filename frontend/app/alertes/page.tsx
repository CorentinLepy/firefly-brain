import Link from "next/link";
import { apiGet } from "../../lib/api";

type AlertItem = { type: string; severity: string; title: string; message: string };
type AlertsResponse = { count: number; items: AlertItem[]; period: { start: string; end: string } };

export default async function AlertsPage() {
  const data = await apiGet<AlertsResponse>("/api/alerts?start=2026-05-01&end=2026-05-31");
  return (
    <main className="page">
      <nav className="topnav"><strong>Firefly Brain V2.1</strong><Link href="/">Dashboard</Link><Link href="/abonnements">Abonnements</Link><Link href="/patrimoine">Patrimoine</Link></nav>
      <section className="header compact"><div><div className="eyebrow">Alertes</div><h1>Points de vigilance</h1><p>Période : {data.period.start} → {data.period.end}</p></div><div className="score-card"><span>Alertes</span><strong>{data.count}</strong></div></section>
      <section className="section single"><div className="card"><h2>Alertes détectées</h2><div className="list">{data.items.map((item) => <div className={`alert ${item.severity}`} key={item.type}><strong>{item.title}</strong><p>{item.message}</p></div>)}</div>{data.items.length === 0 ? <p>Aucune alerte détectée.</p> : null}</div></section>
    </main>
  );
}
