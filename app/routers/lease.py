from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
def test_lease():
    return {"tst": "test"}
