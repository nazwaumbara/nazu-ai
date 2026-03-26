from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    """Endpoint sementara untuk mengecek status module Auth"""
    return {
        "status": "Auth module is ready", 
        "message": "Fitur autentikasi (login/register) akan segera hadir."
    }