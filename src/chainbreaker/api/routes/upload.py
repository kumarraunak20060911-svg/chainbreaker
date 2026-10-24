from fastapi import APIRouter, File, UploadFile

from chainbreaker.web.app import process_rows
from chainbreaker.ingest.service import read_rows

router = APIRouter()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...), assets_file: UploadFile | None = File(None), inventory_file: UploadFile | None = File(None)):
    run = process_rows(read_rows(file.file), asset_rows=read_rows(assets_file.file) if assets_file else None, inventory_rows=read_rows(inventory_file.file) if inventory_file else None)
    return {"run_id": run["run_id"], "accepted_rows": run["diagnostics"].accepted_rows, "rejected_rows": len(run["diagnostics"].rejected_rows), "corrections": list(run["diagnostics"].corrections)}
