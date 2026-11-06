import "./ImageCard.css";
import type { ReactNode } from "react";



type ImageCardProps = {
  title: string;
  image?: string;
  children?: ReactNode;
};

function ImageCard({
  title,
  image,
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
      </div>
    </div>
  );
}

export default ImageCard;