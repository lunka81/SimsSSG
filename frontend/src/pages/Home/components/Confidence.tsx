import "./Confidence.css";

type ConfidenceProps = {
  /** The confidence in percent, 0–100. */
  value: number;
};

/** Circle that shows how confident the recognition is. */
function Confidence({ value }: ConfidenceProps) {
  return (
    <div className="confidence">
      <div
        className="confidence-circle"
        // Creates a CSS variable that the CSS file uses to fill the circle with colour
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