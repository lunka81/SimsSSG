import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";

export type CameraHandle = {
  stopCamera: () => void;
  takeSnapshot: () => string | null;
};

type CameraProps = {
  autoStart?: boolean;
};

const Camera = forwardRef<CameraHandle, CameraProps>(
  function Camera({ autoStart = false }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null);
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

      if (
        !video ||
        video.readyState < 2 ||
        !video.videoWidth ||
        !video.videoHeight
      ) {
        return null;
      }

      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext("2d");
      if (!context) return null;

      context.drawImage(video, 0, 0);

      return canvas.toDataURL("image/jpeg");
    }

    useImperativeHandle(ref, () => ({
      stopCamera,
      takeSnapshot,
    }));

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