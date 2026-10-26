import "./AccessRes.css";

type AccessResProps = {
  approved: boolean;
};

function AccessRes({ approved }: AccessResProps) {

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