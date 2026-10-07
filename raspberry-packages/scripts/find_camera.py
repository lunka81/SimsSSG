import cv2

from config.config import CAMERA_INDEX


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_MSMF)

    try:
        if not cap.isOpened():
            raise RuntimeError(
                f"Kunde inte öppna kamera {CAMERA_INDEX}"
            )

        print("Visar kameraflödet. Tryck Q i bildfönstret för att avsluta.")

        while True:
            ok, frame = cap.read()

            if not ok:
                print("Kunde inte läsa nästa bildruta")
                break

            cv2.imshow(f"Kamera {CAMERA_INDEX}", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()