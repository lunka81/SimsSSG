import "./Confidence.css";

type ConfidenceProps = {
  value: number;
};

function Confidence({ value }: ConfidenceProps) {
  return (
    <div className="confidence">
      <div
        className="confidence-circle"
        //skapar en variabel i som används i CSS filen för att fylla cirkeln med färg
        style={{ "--confidence": `${value}%` } as React.CSSProperties}
>
        <div className="confidence-inner">
          <span className="confidence-value">{value}%</span>
          <span className="confidence-text">Confidence</span>
        </div>
      </div>
    </div>
  );
}

export default Confidence;