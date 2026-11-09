import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";

/** Functions that a parent component can call on the camera through a ref. */
export type CameraHandle = {
  /** Turns off the webcam. */
  stopCamera: () => void;
  /** Takes a picture of the current video frame. Returns a JPEG data URL, or null if no image is ready yet. */
  takeSnapshot: () => string | null;
};

type CameraProps = {
  /** Starts the webcam as soon as the component is shown. */
  autoStart?: boolean;
};

/**
 * Shows live video from the user's webcam.
 * The parent component takes pictures and turns off the camera through a ref (see CameraHandle).
 */
const Camera = forwardRef<CameraHandle, CameraProps>(
  function Camera({ autoStart = false }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null);
    // The active video stream, saved so that the camera can be turned off later
    const streamRef = useRef<MediaStream | null>(null);
    const [error, setError] = useState<string | null>(null);

    function stopCamera() {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }

    function takeSnapshot(): string | null {
      const video = videoRef.current;

      // No picture can be taken before the video has received its first frame
      if (
        !video ||
        video.readyState < 2 ||
        !video.videoWidth ||
        !video.videoHeight
      ) {
        return null;
      }

      // Draws the current frame on a hidden canvas and saves it as a JPEG image
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext("2d");
      if (!context) return null;

      context.drawImage(video, 0, 0);

      return canvas.toDataURL("image/jpeg");
    }

    // Makes stopCamera and takeSnapshot available to the parent component
    useImperativeHandle(ref, () => ({
      stopCamera,
      takeSnapshot,
    }));

    // Asks for access to the webcam and shows the video.
    // cancelled is set if the component is removed before the camera has started,
    // so that the stream is turned off and the camera light does not stay on
    useEffect(() => {
      if (!autoStart) return;
      const videoElement = videoRef.current;

      let cancelled = false;
      let ownedStream: MediaStream | null = null;

      async function openCamera() {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });

          ownedStream = stream;

          if (cancelled) {
            stream.getTracks().forEach((track) => track.stop());
            return;
          }

          const video = videoRef.current;

          if (!video) {
            stream.getTracks().forEach((track) => track.stop());
            return;
          }

          streamRef.current = stream;
          video.srcObject = stream;
          await video.play();
        } catch (error) {
          ownedStream?.getTracks().forEach((track) => track.stop());

          if (!cancelled) {
            streamRef.current = null;
            setError(
              error instanceof Error
                ? error.message
                : "The camera could not be opened."
            );
          }
        }
      }

      void openCamera();

      return () => {
        cancelled = true;
        ownedStream?.getTracks().forEach((track) => track.stop());

        if (streamRef.current === ownedStream) {
          streamRef.current = null;

          if (videoElement) {
            videoElement.srcObject = null;
          }
        }
      };
    }, [autoStart]);

    return (
      <>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            borderRadius: "6px",
          }}
        />

        {error && <p role="alert">{error}</p>}
      </>
    );
  }
);

export default Camera;