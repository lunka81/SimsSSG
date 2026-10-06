import "./ImageCard.css";

type ImageCardProps = {
  title: string;
  image: string;
  /*Visar de orangea hörnen runt bilden (valfri, false om den inte skickas med)*/
  showCorners?: boolean;
};

function ImageCard({ title, image, showCorners = false }: ImageCardProps) {
  return (
    <div className="images-container">
      <div className="image-title">
        <span>{title}</span>
      </div>

      <div className="image-placeholder">
        <img src={image} alt={title} />

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
