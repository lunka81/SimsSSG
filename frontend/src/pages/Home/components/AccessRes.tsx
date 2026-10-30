import "./AccessRes.css";

type AccessResProps = {
  /** true if access is granted, false if it is denied. */
  approved: boolean;
};

/** Green or red card that shows whether access is granted or denied. */
function AccessRes({ approved }: AccessResProps) {

  return (
    // Adds the class "approved" if approved is true, otherwise "denied"
    <div className={`result-card ${approved ? "approved" : "denied"}`}>
      <div className="result-icon">
        {approved ? "✓" : "✕"}
      </div>

      <div className="result-divider"></div>

      <h2>
        Access{" "}
        <span>
          {approved ? "granted" : "denied"}
        </span>
      </h2>
    </div>
  );
}

export default AccessRes;