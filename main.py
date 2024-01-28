from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
ref = "1vKcGrpCAs5-V4iJBbdG1YhoueQAmcwDP"


def authenticate_with_service_account():
    credentials = service_account.Credentials.from_service_account_file(
        "sample-411214-09943b2e9710.json", scopes=SCOPES
    )
    return credentials


def generate_file_url(file):
    url = f"https://drive.google.com/file/d/{file['id']}/view"
    return url


def list_files_in_folder(folder_id, credentials):
    service = build("drive", "v3", credentials=credentials)
    results = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)",
            orderBy="folder, name",
        )
        .execute()
    )
    files = results.get("files", [])

    for i in files:
        if i["mimeType"] == "application/vnd.google-apps.folder":
            i["mimeType"] = "folder"
        else:
            i["mimeType"] = "file"
            i["url"] = generate_file_url(i)
    return files


credentials = authenticate_with_service_account()


@app.get("/getinitial/")
async def getinitial():
    return {"id": ref, "data": list_files_in_folder(ref, credentials)}


@app.get("/getfiles/{id}")
async def getfiles(id: str):
    return {"id": id, "data": list_files_in_folder(id, credentials)}
