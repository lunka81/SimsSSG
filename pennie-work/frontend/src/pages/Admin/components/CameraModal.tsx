import { useEffect, useRef, useState } from "react";
import { Camera as CameraIcon, X } from "lucide-react";
import Camera from "./Camera";
import type { CameraHandle } from "./Camera";
import "./CameraModal.css";

type CameraModalProps = {
  onCapture: (image: string) => void;
  onClose: () => void;
};

function CameraModal({ onCapture, onClose }: CameraModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const cameraRef = useRef<CameraHandle>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const dialog = dialogRef.current;

    if (dialog && !dialog.open) {
      dialog.showModal();
    }

    return () => {
      cameraRef.current?.stopCamera();
      dialog?.close();
    };
  }, []);

  function closeCamera() {
    cameraRef.current?.stopCamera();
    onClose();
  }

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
      className="camera-modal"
      aria-labelledby="camera-title"
      onCancel={(event) => {
        event.preventDefault();
        event.stopPropagation();
        closeCamera();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          closeCamera();
        }
      }}
    >
      <div className="camera-modal-content">
        <div className="camera-modal-header">
          <div>
            <h2 id="camera-title">Take photo</h2>
            <p>Position your face in the centre of the camera.</p>
          </div>

          <button
            type="button"
            className="icon-button"
            title="Close camera"
            aria-label="Close camera"
            onClick={closeCamera}
          >
            <X size={16} />
          </button>
        </div>

        <div className="camera-modal-preview">
          <Camera ref={cameraRef} autoStart />
        </div>

        {error && (
          <p className="camera-modal-error" role="alert">
            {error}
          </p>
        )}

        <div className="camera-modal-footer">
          <button
            type="button"
            className="button-secondary"
            onClick={closeCamera}
          >
            Cancel
          </button>

          <button
            type="button"
            className="button-primary"
            onClick={takePicture}
          >
            <CameraIcon size={16} />
            Take picture
          </button>
        </div>
      </div>
    </dialog>
  );
}

export default CameraModal;