""" pip install slowapi[redis]  # للإنتاج (يستخدم Redis لتخزين البيانات)
# أو
pip install slowapi[memory] # للتجربة (يخزن البيانات في الذاكرة)

import os
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
def get_identifier(request: Request) -> str:
    """
    تحدد هوية العميل بناءً على IP أو مفتاح API.
    هذا يسمح بتطبيق حدود مختلفة للمستخدمين المسجلين والزوار.
    """
    ip = get_remote_address(request)
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    
    return f"ip:{ip}"
limiter = Limiter(
    key_func=get_identifier, 
    default_limits=[os.getenv("RATE_LIMIT_DEFAULT", "100/hour")], 
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),  

)
# installation
pip install fastapi-simple-rate-limiter

# usage
from fastapi import FastAPI, Request
from fastapi_simple_rate_limiter import rate_limiter

app = FastAPI()

@app.get("/test")
@rate_limiter(limit=3, seconds=60) 
async def test_list_api(request: Request):
    return {"message": "Success"} """