import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print('Could not open the camera')
    exit()

while True:
    ok, frame = cap.read()

    if not ok:
        print('Could not read a frame')
        break

    cv2.imshow('Camera', frame)

    if cv2.waitKey(500) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()




