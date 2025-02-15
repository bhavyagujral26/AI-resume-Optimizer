import React, { useState } from "react";
import "./ResumeTemplates.css";

const ResumeTemplates = () => {
  const templates = [
    { name: "Modern Resume", image: "/templates/modern-template.png", file: "/templates/modern-template.docx" },
    { name: "Classic Resume", image: "/templates/classic-template.png", file: "/templates/classic-template.docx" },
    { name: "Creative Resume", image: "/templates/creative-template.png", file: "/templates/creative-template.docx" }
  ];

  const [selectedTemplate, setSelectedTemplate] = useState(null);

  return (
    <div className="templates-section">
      <h2>📄 Choose a Resume Template</h2>
      <div className="templates">
        {templates.map((template, index) => (
          <div key={index} className="template-card">
            <img src={template.image} alt={template.name} />
            <p>{template.name}</p>
            <button onClick={() => setSelectedTemplate(template)}>📝 Edit</button>
            <a href={template.file} download>
              <button>⬇ Download</button>
            </a>
          </div>
        ))}
      </div>

      {selectedTemplate && (
        <div className="template-editor">
          <h3>Editing: {selectedTemplate.name}</h3>
          <textarea placeholder="Edit your resume content here..."></textarea>
          <button onClick={() => setSelectedTemplate(null)}>Close Editor</button>
        </div>
      )}
    </div>
  );
};

export default ResumeTemplates;
