import os
from pathlib import Path

def create_scaffold(project_name: str):
    """
    Creates a production-ready FastAPI project skeleton.
    """
    base_dir = Path(project_name)
    dirs = [
        base_dir / "app" / "api" / "v1",
        base_dir / "app" / "core",
        base_dir / "app" / "models",
        base_dir / "app" / "services",
        base_dir / "app" / "tests",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        (d / "__init__.py").touch()
        
    (base_dir / "README.md").write_text(f"# {project_name}\n\nGenerated with FastAPI Agent Skills.")
    (base_dir / ".gitignore").write_text(".venv/\n__pycache__/\n*.pyc\n.env\n")
    (base_dir / "requirements.txt").write_text("fastapi\nuvicorn[standard]\npydantic\n")
    
    # Simple main.py
    main_content = """from fastapi import FastAPI
from app.api.v1 import routes

app = FastAPI(title="Generated Service", version="1.0.0")
app.include_router(routes.router, prefix="/v1")
"""
    (base_dir / "app" / "main.py").write_text(main_content)
    
    # Simple routes.py
    routes_content = """from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
"""
    (base_dir / "app" / "api" / "v1" / "routes.py").write_text(routes_content)
    
    print(f"Project '{project_name}' scaffolded successfully.")

if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "fastapi-service"
    create_scaffold(name)
