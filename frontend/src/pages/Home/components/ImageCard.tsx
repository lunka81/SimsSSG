import "./ImageCard.css";
import type { ReactNode } from "react";



type ImageCardProps = {
  title: string;
  image?: string;
  showCorners?: boolean;
  children?: ReactNode;
};

function ImageCard({
  title,
  image,
  showCorners,
  children,
}: ImageCardProps) {
  return (
    <div className="images-container">
      <div className="image-title">
        <span>{title}</span>
      </div>

      <div className="image-placeholder">
  {children ?? (
    image ? <img src={image} alt={title} /> : <p>No picture</p>
  )}

        {showCorners && (
          <>
            <span className="corner top-left"></span>
            <span className="corner top-right"></span>
            <span className="corner bottom-left"></span>
            <span className="corner bottom-right"></span>
          </>
        )}
      </div>
    </div>
  );
}

export default ImageCard;