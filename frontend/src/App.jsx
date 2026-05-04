import { useState } from "react";
import axios from "axios";

// All API calls go through Vite's proxy (/api → http://127.0.0.1:8000)
const API = axios.create({ baseURL: "/api" });

function scoreClass(score) {
  if (score >= 65) return "score-high";
  if (score >= 45) return "score-medium";
  return "score-low";
}

export default function App() {
  const [file, setFile]         = useState(null);
  const [status, setStatus]     = useState(null); // { type: "success"|"error", text: "" }
  const [jobs, setJobs]         = useState([]);
  const [uploading, setUploading] = useState(false);
  const [searching, setSearching] = useState(false);

  // ── Upload ──────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file) {
      setStatus({ type: "error", text: "Please select a PDF file first." });
      return;
    }
    setUploading(true);
    setStatus(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await API.post("/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus({ type: "success", text: "✅ " + res.data.message });
    } catch (err) {
      const detail = err.response?.data?.detail || "Upload failed. Check the console.";
      setStatus({ type: "error", text: "❌ " + detail });
    } finally {
      setUploading(false);
    }
  };

  // ── Find Jobs ────────────────────────────────────────────
  const fetchJobs = async () => {
    setSearching(true);
    setJobs([]);
    try {
      const res = await API.get("/scrape-jobs");
      const list = res.data.jobs || [];
      if (list.length === 0) {
        setStatus({ type: "error", text: res.data.message || "No matching jobs found right now." });
      } else {
        setStatus(null);
      }
      setJobs(list);
    } catch (err) {
      const detail = err.response?.data?.detail || "Failed to fetch jobs.";
      setStatus({ type: "error", text: "❌ " + detail });
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="container">
      {/* ── Header ─────────────────────────────────────── */}
      <header style={{ marginBottom: 40, textAlign: "center" }}>
        <h1 style={{ fontSize: "2.2rem", background: "linear-gradient(135deg,#6c63ff,#a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          🚀 Agentic Job Hunter
        </h1>
        <p style={{ color: "var(--text-muted)", marginTop: 8, fontSize: "0.95rem" }}>
          Upload your resume · discover matched jobs · see your skill gaps
        </p>
      </header>

      {/* ── Upload Section ──────────────────────────────── */}
      <div className="card">
        <h2 style={{ marginBottom: 18, fontSize: "1.1rem" }}>1 · Upload Resume</h2>

        <label className={`file-label ${file ? "has-file" : ""}`}>
          <span style={{ fontSize: "1.2rem" }}>📄</span>
          <span>{file ? file.name : "Click to choose a PDF…"}</span>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => { setFile(e.target.files[0]); setStatus(null); }}
          />
        </label>

        <div style={{ marginTop: 16, display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
          <button
            id="btn-upload"
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={uploading || !file}
          >
            {uploading ? <><div className="spinner" /> Uploading…</> : "Upload Resume"}
          </button>

          <button
            id="btn-find-jobs"
            className="btn btn-secondary"
            onClick={fetchJobs}
            disabled={searching}
          >
            {searching ? <><div className="spinner" /> Searching…</> : "🔍 Find Jobs"}
          </button>
        </div>

        {status && (
          <div className={`status-banner ${status.type}`} style={{ marginTop: 14 }}>
            {status.text}
          </div>
        )}
      </div>

      {/* ── Job Results ─────────────────────────────────── */}
      {searching && (
        <div className="empty-state" style={{ marginTop: 40 }}>
          <div className="spinner" style={{ margin: "0 auto 14px" }} />
          Scraping jobs & running AI analysis… this may take 20–30 seconds.
        </div>
      )}

      {!searching && jobs.length > 0 && (
        <>
          <div className="divider" />
          <h2 style={{ marginBottom: 20, fontSize: "1.1rem" }}>
            2 · Matched Jobs&nbsp;
            <span style={{ color: "var(--text-muted)", fontWeight: 400, fontSize: "0.9rem" }}>
              ({jobs.length} found)
            </span>
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {jobs.map((job, i) => (
              <article key={i} className="job-card">
                <div className="job-card__header">
                  <div>
                    <div className="job-card__title">{job.title}</div>
                    <div className="job-card__meta">
                      {job.company} · {job.location}
                    </div>
                  </div>
                  <span className={`score-badge ${scoreClass(job.match_score ?? 0)}`}>
                    {job.match_score ?? "—"}% match
                  </span>
                </div>

                {job.why_match && (
                  <div className="job-card__section">
                    <h4>Why it matches</h4>
                    <p>{job.why_match}</p>
                  </div>
                )}

                {job.skill_gap?.missing_skills?.length > 0 && (
                  <div className="job-card__section">
                    <h4>Skill gaps to close</h4>
                    <div style={{ marginTop: 4 }}>
                      {job.skill_gap.missing_skills.map((s, j) => (
                        <span key={j} className="skill-pill">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{ marginTop: 16 }}>
                  <a
                    href={job.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                    style={{ fontSize: "0.85rem", padding: "7px 16px" }}
                  >
                    🔗 Apply
                  </a>
                </div>
              </article>
            ))}
          </div>
        </>
      )}

      {!searching && jobs.length === 0 && !status && (
        <div className="empty-state" style={{ marginTop: 40 }}>
          Upload your resume then click <strong>Find Jobs</strong> to begin.
        </div>
      )}
    </div>
  );
}
