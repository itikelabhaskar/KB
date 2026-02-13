import { useState, useRef, useEffect } from "react";
import { search } from "../api";

const EXAMPLES = [
    "What is the PTO policy?",
    "What caused incident 5023?",
    "What are our pricing tiers?",
    "How do I onboard as a new employee?",
    "What is the tech stack?",
];

export default function SearchPage({ session, onLogout }) {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const inputRef = useRef(null);
    const bottomRef = useRef(null);

    useEffect(() => { inputRef.current?.focus(); }, []);

    const doSearch = async (q) => {
        const text = q || query;
        if (!text.trim()) return;

        setQuery(text);
        setLoading(true);
        setError(null);

        try {
            const data = await search(session.token, text);
            setResults((prev) => [...prev, { query: text, ...data }]);
            setQuery("");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }

        setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 80);
    };

    const handleSubmit = (e) => { e.preventDefault(); doSearch(); };

    return (
        <div className="app-layout">
            {/* ── Topbar ── */}
            <header className="topbar">
                <div className="brand">
                    <span className="mark">K</span>
                    Knowledge Base
                </div>
                <div className="topbar-right">
                    <div className="user-info">
                        <div>
                            <div className="user-name">{session.user_id}</div>
                            <div className="user-dept">{session.department}</div>
                        </div>
                    </div>
                    <div className="role-tags">
                        {session.roles.map((r) => (
                            <span key={r} className={`role-tag ${r.toLowerCase()}`}>{r}</span>
                        ))}
                    </div>
                    <button className="logout-btn" onClick={onLogout}>Sign out</button>
                </div>
            </header>

            {/* ── Content ── */}
            <main className="main-content">
                {results.length === 0 && !loading ? (
                    <div className="welcome">
                        <h2>What do you want to know?</h2>
                        <p>
                            Search internal documents and get AI-powered answers.
                            Your access level: <strong>{session.roles.join(", ")}</strong>
                        </p>
                        <div className="example-queries">
                            {EXAMPLES.map((ex) => (
                                <button key={ex} className="example-btn" onClick={() => doSearch(ex)}>
                                    {ex}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="results-area">
                        {results.map((r, i) => (
                            <div key={i}>
                                <div className="q-bubble">{r.query}</div>

                                <div className="a-card">
                                    <div className="a-label">
                                        <span className="dot" />
                                        Answer
                                    </div>
                                    <div className="a-body">{r.answer}</div>
                                    <div className="a-meta">
                                        <span>{r.latency_ms} ms</span>
                                        <span>{r.chunks_found} chunks</span>
                                        <span>{r.citations.length} sources</span>
                                    </div>

                                    {r.citations.length > 0 && (
                                        <div className="citations">
                                            <div className="c-heading">Sources</div>
                                            <div className="c-list">
                                                {r.citations.map((c) => (
                                                    <div key={c.marker} className="c-item">
                                                        <span className="c-num">{c.marker}</span>
                                                        <span className="c-title">{c.doc_title}</span>
                                                        <span className="c-dept">{c.department}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="loading-state">
                                <div className="spinner" />
                                <span>Searching…</span>
                            </div>
                        )}

                        {error && <div className="error-msg">{error}</div>}
                        <div ref={bottomRef} />
                    </div>
                )}
            </main>

            {/* ── Search bar ── */}
            <div className="search-bar-wrap">
                <form className="search-bar" onSubmit={handleSubmit}>
                    <input
                        ref={inputRef}
                        type="text"
                        placeholder="Ask a question…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={loading}
                    />
                    <button type="submit" className="send-btn" disabled={loading || !query.trim()}>
                        ↑
                    </button>
                </form>
            </div>
        </div>
    );
}
