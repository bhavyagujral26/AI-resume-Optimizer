import React from "react";
import ReactLoading from "react-loading";
import "./Loading.css";

const Loading = () => {
  return (
    <div className="loading-container">
      <ReactLoading type="spin" color="#ff416c" height={80} width={80} />
      <p>Analyzing your resume...</p>
    </div>
  );
};

export default Loading;
