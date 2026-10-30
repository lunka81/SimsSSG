import "./ImageCard.css";
import type { ReactNode } from "react";



type ImageCardProps = {
  title: string;
  /** Address of the picture to show. */
  image?: string;
  /** Content shown instead of the picture. */
  children?: ReactNode;
};

/** Card with a title that shows either a picture or other content. */
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