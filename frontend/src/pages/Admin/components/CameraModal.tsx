import { useEffect, useRef, useState } from "react";

import Camera from "./Camera";
import type { CameraHandle } from "./Camera";

type CameraModalProps = {
  /** Receives the picture as a JPEG data URL. */
  onCapture: (image: string) => void;
  onClose: () => void;
};

/** Popup where the admin takes a profile picture with the webcam. */
function CameraModal({ onCapture, onClose }: CameraModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const cameraRef = useRef<CameraHandle>(null);
  const [error, setError] = useState<string | null>(null);

  // Opens the dialog when the component is shown and closes it when it is removed
  useEffect(() => {
    const dialog = dialogRef.current;

    if (dialog && !dialog.open) {
      dialog.showModal();
    }

    return () => {
      dialog?.close();
    };
  }, []);

  function closeCamera() {
    cameraRef.current?.stopCamera();
    onClose();
  }

  // Takes a picture, turns off the camera and sends the picture to the parent component
  function takePicture() {
    const image = cameraRef.current?.takeSnapshot();

    if (!image) {
      setError(
        "No camera image yet. Allow camera access and try again."
      );
      return;
    }

    cameraRef.current?.stopCamera();
    onCapture(image);
  }

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="camera-title"
      onCancel={(event) => {
        event.preventDefault();
        closeCamera();
      }}
    >
      

      <div className="camera-container">
        <Camera ref={cameraRef} autoStart />
      </div>

      {error && <p role="alert">{error}</p>}

      <button
        type="button"
        className="button-primary"
        onClick={takePicture}

        style={{
          marginRight: "5px"
        }}
          
      >
        Take Picture
      </button>

      <button type="button" 
        className="button-secondary"
        onClick={closeCamera}>
        Cancel
      </button>
    </dialog>
  );
}

export default CameraModal;