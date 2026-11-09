import cv2

for index in range(5):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if cap.isOpened():
        ok, frame = cap.read()
        if ok:
            print("Index", index, "works. Frame size:", frame.shape)
        else:
            print("Index", index, "opened but gave no frame")
        cap.release()
    else:
        print("Index", index, "not available")