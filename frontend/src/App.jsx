import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload-resume",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage("✅ " + response.data.message);
    } catch (error) {
      console.error(error);
      setMessage(
        error.response?.data?.detail || "❌ Upload failed"
      );
    }
  };

  const fetchJobs = async () => {
    setLoading(true);

    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/scrape-jobs"
      );

      setJobs(response.data.jobs);
    } catch (error) {
      console.error(error);
      alert("❌ Failed to fetch jobs");
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial",
        maxWidth: "900px",
        margin: "auto",
      }}
    >
      <h1 style={{ textAlign: "center" }}>
        🚀 AI Job Hunter
      </h1>

      {/* Upload Section */}
      <h3>Upload Resume</h3>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button
        onClick={handleUpload}
        style={{
          padding: "10px 15px",
          marginRight: "10px",
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Upload Resume
      </button>

      <p>{message}</p>

      {/* Fetch Jobs */}
      <br />

      <button
        onClick={fetchJobs}
        style={{
          padding: "10px 15px",
          backgroundColor: "#2196F3",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        🔍 Find Jobs
      </button>

      {/* Loading */}
      {loading && <p>⏳ Fetching jobs...</p>}

      {/* Empty State */}
      {!loading && jobs.length === 0 && (
        <p style={{ marginTop: "20px", color: "gray" }}>
          No jobs found yet. Upload resume & click Find Jobs.
        </p>
      )}

      {/* Job Results */}
      <div style={{ marginTop: "30px" }}>
        {jobs.map((job, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #e0e0e0",
              padding: "20px",
              margin: "20px 0",
              borderRadius: "10px",
              backgroundColor: "#fafafa",
            }}
          >
            <h3>{job.title}</h3>

            <p><b>Company:</b> {job.company}</p>
            <p><b>Location:</b> {job.location}</p>
            <p><b>Match Score:</b> {job.match_score}%</p>

            {job.why_match && (
              <p><b>Why Match:</b> {job.why_match}</p>
            )}

            {job.skill_gap && (
              <p>
                <b>Missing Skills:</b>{" "}
                {job.skill_gap.missing_skills.join(", ")}
              </p>
            )}

            <a
              href={job.link}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#2196F3", fontWeight: "bold" }}
            >
              🔗 Apply Here
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
