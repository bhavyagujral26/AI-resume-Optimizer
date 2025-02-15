import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import "./App.css"; // Ensure your styles are applied
import Loading from "./components/Loading";
import ResumeTemplates from "./components/ResumeTemplates";

const App = () => {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Dark mode effect
  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
  }, [darkMode]);

  const handleFileChange = (event) => {
    setResume(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!resume || !jobDescription) {
      alert("Please upload a resume and enter a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    setLoading(true);
    setError(null); // Reset error before request

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      if (response.data.error) {
        setError(response.data.error);
        console.error("Backend Error:", response.data.error);
      } else {
        setResult(response.data);
        alert("Resume processed successfully!");
      }
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to process the resume. Please check your backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <button className="dark-mode-toggle" onClick={() => setDarkMode(!darkMode)}>
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>

      <h2 className="title">✨ AI Resume Optimizer ✨</h2>

      {loading && <Loading />} {/* ✅ Moved inside JSX */}

      <motion.div className="glassmorphism form-section">
        <label className="label">📂 Upload Resume (PDF/DOCX):</label>
        <input type="file" onChange={handleFileChange} className="input-field" />

        <label className="label">📝 Job Description:</label>
        <textarea
          rows="4"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here..."
          className="input-textarea"
        ></textarea>

        <motion.button
          className="fancy-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "⏳ Processing..." : "🚀 Analyze Resume"}
        </motion.button>
      </motion.div>

      {error && <p className="error-message">❌ {error}</p>}

      {result && (
        <motion.div
          className="glassmorphism result-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h4>📊 Results:</h4>
          <p><strong>Match Score:</strong> {result.match_result?.overall_score}%</p>
          <p><strong>Skill Match:</strong> {result.match_result?.skill_match}%</p>
          <p><strong>Education Match:</strong> {result.match_result?.education_match}%</p>
          <p><strong>Text Similarity:</strong> {result.match_result?.text_similarity}%</p>

          <h5>🚀 Missing Skills:</h5>
          {result.match_result?.missing_skills?.length > 0 ? (
            <ul>
              {result.match_result.missing_skills.map((skill, index) => (
                <li key={index}>{skill}</li>
              ))}
            </ul>
          ) : (
            <p>✅ No missing skills detected.</p>
          )}

          <h5>📄 AI-Enhanced Resume Text:</h5>
          <p className="enhanced-resume">
            {result.match_result?.improved_text || "No enhanced resume generated."}
          </p>
        </motion.div>
      )}

      {/* ✅ Resume Templates Section Below Everything */}
      <ResumeTemplates />
    </motion.div>
  );
};

export default App;
