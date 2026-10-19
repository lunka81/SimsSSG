#script to create the first admin account. 
#not possible from the web app unless one is logged in. 

import argparse
import sys
import mimetypes
import base64
from getpass import getpass
from pathlib import Path
from fastapi import HTTPException

from demo.schemas.admin_schema import AdminCreate
from demo.schemas.employee_schema import EmployeeCreate
from demo.models.employee_test import Permission
from demo.db.database import SessionLocal
from demo.services.admin_services import add_admin, username_unique

#Models must be imported so SQLAlchemy can resolve the relationships between them.
import demo.models.employee_test
import demo.models.employee_test_log
import demo.models.admin

#vibecoded function
def image_to_data_url(path: Path) -> str:
    #decode_image_to_bgr expects the same format as the frontend sends: 
    #"data:image/jpeg;base64,..."
    media_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    b64data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{b64data}"

def main():
    """
    run this script with a command like:
        python admin_init.py --name [your name] --username [your username]
                --image [path to your image] -- description [your optional desc]
    """
    parser = argparse.ArgumentParser(description="Create an admin account.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--description", required=False)
    args=parser.parse_args()

    if not args.image.is_file():
        sys.exit(f"Couldn't find image at {args.image}")

    password = getpass(prompt="Enter admin password: ")
    password_reenter = getpass(prompt="Enter admin password again: ")
    if password_reenter != password:
        sys.exit("Passwords don't match")

    img_data_url = image_to_data_url(args.image)

    admin_payload = AdminCreate(
        name=args.name,
        permission=Permission.ADMIN,
        description=args.description,
        img=img_data_url,
        username=args.username,
        plain_password=password
    )
    with SessionLocal() as session:
        if not username_unique(session, admin_payload.username):
            sys.exit("Username already exist")
        try:
            add_admin(session, admin_payload)
        except HTTPException as e: #most likely, face wasn't detected.
            sys.exit(f"Couldn't create admin: {e.detail}") 
    print(f"New admin: {admin_payload.username}")

    
main()