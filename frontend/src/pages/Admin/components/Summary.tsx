import type { ReactNode } from "react";
import "./Summary.css";

type SummaryProps = {
  icon: ReactNode;
  iconClass: string;
  value: string;
  label: string;
  sub: string;
};

function Summary({ icon, iconClass, value, label, sub }: SummaryProps) {
  return (
    <div className="summary-card">
      <div className={iconClass}>{icon}</div>
      <div>
        <p className="summary-value">{value}</p>
        <p className="summary-label">{label}</p>
        <p className="summary-sub">{sub}</p>
      </div>
    </div>
  );
}

export default Summary;