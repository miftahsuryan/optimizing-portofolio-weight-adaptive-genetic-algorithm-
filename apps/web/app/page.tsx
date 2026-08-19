"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  createBrief,
  listBriefs,
  PortfolioBrief,
  RiskProfile,
} from "../lib/api";

export default function Home() {
  const [name, setName] = useState("My first portfolio");
  const [riskProfile, setRiskProfile] = useState<RiskProfile>("balanced");
  const [briefs, setBriefs] = useState<PortfolioBrief[]>([]);
  const [status, setStatus] = useState<"loading" | "idle" | "saving">("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listBriefs()
      .then(setBriefs)
      .catch((reason: unknown) =>
        setError(reason instanceof Error ? reason.message : "Could not load briefs"),
      )
      .finally(() => setStatus("idle"));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    setError(null);
    try {
      const brief = await createBrief({ name, risk_profile: riskProfile });
      setBriefs((current) => [brief, ...current]);
      setName("");
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Could not save brief");
    } finally {
      setStatus("idle");
    }
  }

  return (
    <main>
      <header>
        <p className="eyebrow">PORTFOLIO LAB · v0.1</p>
        <h1>Turn a risk profile into a clear first move.</h1>
        <p className="lede">A complete UI → API → PostgreSQL slice with a deterministic AI preview.</p>
      </header>

      <section className="composer" aria-labelledby="brief-title">
        <div>
          <p className="step">01 / CREATE</p>
          <h2 id="brief-title">New portfolio brief</h2>
        </div>
        <form onSubmit={submit}>
          <label>
            Portfolio name
            <input value={name} onChange={(event) => setName(event.target.value)} maxLength={120} required />
          </label>
          <label>
            Risk profile
            <select value={riskProfile} onChange={(event) => setRiskProfile(event.target.value as RiskProfile)}>
              <option value="conservative">Conservative</option>
              <option value="balanced">Balanced</option>
              <option value="growth">Growth</option>
            </select>
          </label>
          <button disabled={status === "saving"}>{status === "saving" ? "Saving…" : "Generate & persist"}</button>
        </form>
        {error && <p className="error" role="alert">{error}</p>}
      </section>

      <section className="history" aria-labelledby="history-title">
        <div className="section-heading">
          <div>
            <p className="step">02 / PERSISTED</p>
            <h2 id="history-title">Saved briefs</h2>
          </div>
          <span>{briefs.length} rows</span>
        </div>
        {status === "loading" ? (
          <p className="empty">Loading persisted rows…</p>
        ) : briefs.length === 0 ? (
          <p className="empty">No briefs yet. Create the first one above.</p>
        ) : (
          <div className="cards">
            {briefs.map((brief) => (
              <article key={brief.id}>
                <div className="card-top">
                  <h3>{brief.name}</h3>
                  <span className={`risk ${brief.risk_profile}`}>{brief.risk_profile}</span>
                </div>
                <p>{brief.ai_summary}</p>
                <small>Persisted · {new Date(brief.created_at).toLocaleString()}</small>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
