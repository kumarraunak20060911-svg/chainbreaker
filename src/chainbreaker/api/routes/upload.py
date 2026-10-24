from fastapi import APIRouter, File, UploadFile

from chainbreaker.web.app import process_rows
from chainbreaker.ingest.service import read_rows

router = APIRouter()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    return {"run_id": process_rows(read_rows(file.file))["run_id"]}
