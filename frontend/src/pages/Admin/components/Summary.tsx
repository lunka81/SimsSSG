import type { ReactNode } from "react";
import "./Summary.css";

type SummaryProps = {
  icon: ReactNode;
  /** CSS class for the icon, e.g. "summary-icon approved" for a green icon. */
  iconClass: string;
  /** The number shown in large text. */
  value: string;
  /** What the number describes. */
  label: string;
  /** Small text under the label, e.g. the time period. */
  sub: string;
};

/** A card that shows one statistic on the admin start page. */
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