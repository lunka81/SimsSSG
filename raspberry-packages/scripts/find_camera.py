import cv2

from camera.camera import Camera
from config.config import CAMERA_INDEX


def main():
    camera = Camera()

    try:
        print("Visar kameraflödet. Tryck Q i bildfönstret för att avsluta.")

        while True:
            frame = camera.read()

            cv2.imshow(f"Kamera {CAMERA_INDEX}", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()