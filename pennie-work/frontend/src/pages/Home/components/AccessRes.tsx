import "./AccessRes.css";

type AccessResProps = {
  confidence: number;
};

function AccessRes({ confidence }: AccessResProps) {
  const approved = confidence >= 80;

  return (
    //ternary operator. Om approved = true så läggs klassen "approved" till annars "denied"
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