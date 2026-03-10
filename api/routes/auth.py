from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    """Login endpoint. Implement later."""
    pass


@router.post("/signup")
def signup():
    """Signup endpoint. Implement later."""
    pass
