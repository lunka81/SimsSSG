from fastapi import APIRouter, Depends, Header
from fastapi import WebSocket, WebSocketDisconnect
import base64
from demo.services.recognition_socket import manager, send_to_frontend
from demo.models.employee_test import EmployeeTest
from demo.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from demo.services import comparison_services, img_services
from sqlalchemy.orm import Session
from demo.db.database import get_session

recognition_router = APIRouter(
    prefix="/recognition",
    tags=["identify"]
)

@recognition_router.post(
    "/identify",
    response_model=ComparisonResponse,
    status_code=200,
    summary="HTTP POST endpoint to which the raspberry pi sends embeddings of captured faces upon access attempts.",
    description="Calls functions for nearest neighbour search and response construction, then communicates the response to the frontend's start page via a websocket."   
)
async def compare_employee(
    payload: ComparisonRequest,
    session: Session = Depends(get_session),
    x_api_key: str | None = Header(default=None),
):
    comparison_services.validate_api_key(x_api_key)

    nearest_neighbour = comparison_services.find_nearest_neighbour(
        session, payload.embedding
    )

    match_score = (comparison_services.similarity_to_match_score(
        nearest_neighbour.similarity
    )
    if nearest_neighbour is not None 
    else None
    ) 

    response = comparison_services.get_compare_response(
        session, nearest_neighbour, match_score, payload
    )

    #Websocket communication written by Anders. Pushed by me because Anders has some bugs he doesn't want to commit to this branch.
    if response.employee_uuid is not None:
        employee = session.get(EmployeeTest, response.employee_uuid)

        if employee is not None:
            await send_to_frontend({
                "event": "person_recognized",
                "match_score": match_score,
                "approved": response.approved,
                "person": {
                    "uuid": str(employee.uuid),
                    "name": employee.name,
                    "permission": employee.permission,
                    "description": employee.description,
                    #both jpg and png allowed.
                    "image": (f"data:{img_services.image_media_type(employee.image)};base64,"+ base64.b64encode(employee.image).decode("ascii")
                              if employee.image is not None
                              else None),
                },
            })
    else: 
        await send_to_frontend({
            "event": "person_not_recognized",
            "match_score": match_score,
            "approved": response.approved,
            "person": None
        })
    return response


#summary: HTTP websocket endpoint that listens for continious requests using the websocket protocol.
#description: This is a way for the backend to communicate, to the frontend, the details of an employee being identified at the gate.

#Endpoint written by Anders. Pushed by me because Anders has some bugs he doesn't want to commit to this branch.
@recognition_router.websocket("/ws")
async def recognition_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)