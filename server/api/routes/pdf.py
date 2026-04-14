import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.api.schemas import ReportData
from server.services.pdf_service import generate_pdf_from_report

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/publish/pdf")
async def publish_pdf(report: ReportData):
    try:
        out_path = generate_pdf_from_report(report)
        return FileResponse(
            path=out_path,
            filename="Report.pdf",
            media_type="application/pdf",
            background=None,
        )
    except RuntimeError as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
