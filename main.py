from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from common.utility.Global import G
from route.ExecutionRoute import router as exec_route
from route.TaskRoute import router as task_route
from route.ReferenceRoute import router as ref_route
from route.ProblemRoute import router as problem_route

app = FastAPI()

app.include_router(exec_route, tags=["exec_route"], prefix="/api/exec")
app.include_router(task_route, tags=["task_route"], prefix="/api/task")
app.include_router(ref_route, tags=["ref_route"], prefix="/api/ref")
app.include_router(problem_route, tags=["problem_route"], prefix="/api/problem")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=5003, reload=True)