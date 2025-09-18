import argparse
import os
import sys
import asyncio
from pathlib import Path
from mmengine import DictAction
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add the project root to the Python path
root = str(Path(__file__).resolve().parents[1])
sys.path.append(root)

from src.logger import logger
from src.config import config
from src.models import model_manager
from src.agent import create_agent

class Task(BaseModel):
    task: str

# Global variable to hold the agent
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent
    parser = argparse.ArgumentParser(description='main')
    parser.add_argument("--config", default=os.path.join(root, "configs", "config_main.py"), help="config file path")
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.')
    # Use parse_known_args to avoid conflicts with uvicorn's args
    args, unknown = parser.parse_known_args()

    # Initialize the configuration
    config.init_config(args.config, args)

    # Initialize the logger
    logger.init_logger(log_path=config.log_path)
    logger.info(f"| Logger initialized at: {config.log_path}")
    logger.info(f"| Config:\n{config.pretty_text}")

    # Registed models
    model_manager.init_models(use_local_proxy=True)
    logger.info("| Registed models: %s", ", ".join(model_manager.registed_models.keys()))

    # Create agent
    agent = await create_agent(config)
    logger.visualize_agent_tree(agent)
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=os.path.join(root, "web", "static")), name="static")

@app.post("/run_agent")
async def run_agent_endpoint(task: Task):
    global agent
    if agent is None:
        return {"error": "Agent not initialized"}

    res = await agent.run(task.task)
    logger.info(f"| Result: {res}")
    return {"result": res}

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(root, "web", "static", "index.html"))
