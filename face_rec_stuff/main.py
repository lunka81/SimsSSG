import base64
from datetime import datetime
from io import BytesIO
from time import perf_counter
from fastapi import HTTPException
from deepface.modules.exceptions import SpoofDetected
from deepface.modules import modeling
import cv2
import numpy as np
from deepface import DeepFace
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from sqlalchemy import select
from models.employee_log import EmployeeLog

from database.database import SessionLocal, Base, engine
from models.employee import Employee
from helper.face_metrics import (
    calculate_face_metrics,
    print_face_metrics, estimate_distance_cm,
)

# Skapar tabeller som definierats via Base, om de ännu inte finns.
# create_all ändrar däremot inte kolumner i en redan befintlig tabell.
Base.metadata.create_all(bind=engine)

app = FastAPI()

# React kör på port 5173 och FastAPI på en annan port.
# Webbläsaren betraktar dem därför som olika origins och kräver
# att backend uttryckligen tillåter anrop från React-adressen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Snapshot(BaseModel):
    """JSON-formatet som /api/save-image tar emot från frontend."""

    image: str    # Kamerabilden som data-URL: data:image/jpeg;base64,...
    name: str     # Namnet som användaren skrev vid registrering



class FindFaceRequest(BaseModel):
    """JSON-formatet som /api/find-face tar emot."""

    image: str    # Ny kamerabild som ska jämföras med databasen


def decode_image_to_bgr(image_data_url: str) -> tuple[bytes, np.ndarray]:
    """Avkodar en data-URL och ger tillbaka bildbytes och en BGR-array.

    Bildbytes används när originalbilden ska sparas i databasen.
    BGR-arrayen används som indata till DeepFace.
    """
    # Data-URL:en består av en header och Base64-kodade bilddata.
    # split(",", 1) delar bara vid det första kommatecknet.
    _, b64data = image_data_url.split(",", 1)

    # Base64-texten görs om till de ursprungliga JPEG-bytesen.
    img_bytes = base64.b64decode(b64data)

    # PIL öppnar bytesen som en bild. RGB säkerställer tre färgkanaler.
    pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")

    # NumPy ger en array av bildens pixlar.
    rgb = np.array(pil_img)

    # DeepFace förväntar sig en NumPy-bild i BGR-ordning.
    # Samma konvertering används vid både registrering och sökning.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    return img_bytes, bgr


@app.post("/api/save-image")
async def save_image(payload: Snapshot):
    """Sparar en bild och dess FaceNet512-embedding på samma rad."""

    # Behåll bildbytesen för lagring och använd BGR-bilden för modellen.
    img_bytes, bgr = decode_image_to_bgr(payload.image)

    # OpenCV hittar ansiktet. align=True riktar in det.
    # FaceNet512 omvandlar sedan ansiktet till en vektor med 512 tal.
    # enforce_detection=True avbryter om inget ansikte hittas.
    result = DeepFace.represent(
        img_path=bgr,
        model_name="Facenet512",
        detector_backend="opencv",
        enforce_detection=True,
        align=True,
    )
    metrics = calculate_face_metrics(result, bgr)
    print_face_metrics(metrics)

    # represent() ger en lista med resultat eftersom en bild kan
    # innehålla flera ansikten. Här använder vi det första ansiktet.
    # float(x) ger vanliga Python-tal att spara i pgvector-kolumnen.
    embedding = [float(x) for x in result[0]["embedding"]]

    # with stänger databassessionen när blocket avslutas.
    with SessionLocal() as db:
        employee = Employee(
            embedding=embedding,
            name=payload.name,
            timestamp=datetime.now(),
            approved=False,
            picture=img_bytes,
        )

        db.add(employee)       # Lägger till objektet i sessionen.
        db.commit()            # Skriver posten till databasen.
        db.refresh(employee)   # Hämtar bland annat genererat ID.

        return {"status": "saved", "id": employee.id}


@app.post("/api/find-face")
def recognize_face(payload: FindFaceRequest):

    # Tillfällig gräns för hur långt ifrån en kandidat får ligga.
    # Detta är cosine distance, inte en procentsats eller sannolikhet.

    MAX_DISTANCE = 0.5

    # Dessa tidsstämplar visar var en eventuell väntetid uppstår.

    start = perf_counter()

    # Sökbilden avkodas på samma sätt som bilderna vid registrering.
    # Bildbytesen används inte vidare i just den här endpointen.

    _, bgr = decode_image_to_bgr(payload.image)
    decoded = perf_counter()

    # Samma modell, detektor och justering används som i save_image.
    # anti_spoofing=True gör dessutom en separat kontroll som kan
    # avvisa försök där ett foto eller en skärm visas för kameran.

    result = DeepFace.represent(
        img_path=bgr,
        model_name="Facenet512",
        detector_backend="opencv",
        enforce_detection=True,
        align=True,
        anti_spoofing=True,
    )

    metrics = calculate_face_metrics(result, bgr)
    print_face_metrics(metrics)
    represented = perf_counter()
    # Använd ansiktsrutan som represent() redan hittade.
    face = result[0]["facial_area"]
    facial_area = (face["x"], face["y"], face["w"], face["h"])

    # DeepFaces anti-spoofing-modell. Första körningen kan även omfatta
    # att modellen byggs och vikterna läses in.
    fasnet = modeling.build_model(task="spoofing", model_name="Fasnet")
    is_real, spoof_score = fasnet.analyze(
        img=bgr,
        facial_area=facial_area,
    )
    spoofed = perf_counter()

    print(
        f"Avkoda: {decoded - start:.2f} s | "
        f"Detektion + FaceNet512: {represented - decoded:.2f} s | "
        f"Anti-spoofing: {spoofed - represented:.2f} s | "
        f"Levande: {is_real} | Score: {spoof_score:.3f}"
    )

    if not is_real:
        raise HTTPException(
            status_code=422,
            detail="Kunde inte bekräfta ett levande ansikte.",
        )

    # Vektorn från den nya bilden är frågan vi söker med i databasen.
    new_embedding = [float(x) for x in result[0]["embedding"]]
    database_started = perf_counter()
    # pgvector skapar ett SQL-uttryck för cosine distance mellan
    # sökbildens vektor och varje lagrad Employee.embedding.
    distance = Employee.embedding.cosine_distance(new_embedding)

    with SessionLocal() as db:
        matches = db.execute(
            select(
                Employee.id,
                Employee.name,
                Employee.picture,
                distance.label("distance"),
            )
            .order_by(distance)  # Lägsta avståndet först.
            .limit(3)            # Hämta bara närmaste bildpost. ska vara limit 1 i produktion
        ).all()                  # ska vara first()

        database_ms = (perf_counter() - database_started) * 1000

        for candidate in matches:
            print(
                f"ID: {candidate.id} | "
                f"Bild: {candidate.name} | "
                f"Vektoravstånd: {candidate.distance:.3f}"
            )
    # Listan är sorterad med lägst avstånd först.
    match = matches[0] if matches else None
    searched = perf_counter()
    shortest_distance = (
        float(match.distance) if match is not None else None
    )

    accepted = (
        shortest_distance is not None
        and shortest_distance <= MAX_DISTANCE
    )
    # En loggrad beskriver hela identifieringsförsöket.
    employee_log = EmployeeLog(
        nearest_image_id=match.id if match is not None else None,
        result="match" if accepted else "no_match",
        estimated_camera_distance_cm=metrics.estimated_distance_cm,
        face_width_ratio=metrics.face_width_ratio,
        vector_distance=shortest_distance,
        threshold=MAX_DISTANCE,
        detection_embedding_ms=(represented - decoded) * 1000,
        anti_spoofing_ms=(spoofed - represented) * 1000,
        database_ms=database_ms,
        is_real=bool(is_real),
        model_name="Facenet512",
        detector_backend="opencv",
    )

    db.add(employee_log)
    db.commit()

    # Tidtagningen skiljer bildavkodning, DeepFace och SQL-sökning åt.
    print(
        f"Avkoda: {decoded - start:.2f} s | "
        f"DeepFace: {represented - decoded:.2f} s | "
        f"Databas: {searched - spoofed:.2f} s"
    )

    # Utan gränsen skulle databasen alltid returnera närmaste rad,
    # även om personen framför kameran inte finns registrerad.
    if match is None or float(match.distance) > MAX_DISTANCE:
        return None

    # PostgreSQL lagrar originalbilden som bytes. JSON kan inte
    # använda bytes direkt som <img src>. Därför görs den om till
    # en Base64-kodad data-URL som React kan visa.
    picture = (
        "data:image/jpeg;base64,"
        + base64.b64encode(match.picture).decode("ascii")
        if match.picture else None
    )

    # ID, namn och bild kommer alla från raden med lägst avstånd.
    return {
        "id": match.id,
        "name": match.name,
        "picture": picture,
        "distance": float(match.distance),

    }


