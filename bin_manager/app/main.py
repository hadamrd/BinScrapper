# bin_manager/app/main.py
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import uvicorn
from typing import Optional
from bin_manager.app.scraping_worker import scraping_worker
from bin_manager.app.state import state_manager
from bin_manager.app.url_collection_worker import url_collection_worker
from bin_manager.db.database import BinDatabase
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="BIN Database Manager", version="0.1")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
api_router = APIRouter(prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "BIN Database Manager"
    })

@api_router.get("/stats")
async def get_stats():
    """Get current database statistics."""
    db = BinDatabase()
    try:
        total_urls = db.get_total_urls_count()
        processed = db.get_processed_urls_count()
        return {
            "total_banks": total_urls,
            "processed_banks": processed,
            "completion_percentage": (processed / total_urls * 100) if total_urls > 0 else 0,
            "scraping_status": state_manager.scraping_status
        }
    finally:
        db.close()

@api_router.get("/urls/status")
async def get_url_collection_status():
    """Get current URL collection status."""
    return state_manager.url_collection_status

@api_router.post("/urls/collect/start")
async def start_url_collection(background_tasks: BackgroundTasks):
    """Start the URL collection process."""
    if state_manager.url_collection_status['is_running']:
        raise HTTPException(status_code=400, detail="URL collection is already running")
    
    background_tasks.add_task(url_collection_worker)
    return {"status": "started", "message": "URL collection process started"}

@api_router.post("/urls/collect/stop")
async def stop_url_collection():
    """Stop the URL collection process."""
    if not state_manager.url_collection_status['is_running']:
        raise HTTPException(status_code=400, detail="URL collection is not running")
    
    state_manager.update_url_status(is_running=False)
    return {"status": "stopping"}

@api_router.post("/scraping/start")
async def start_scraping(background_tasks: BackgroundTasks):
    """Start the BIN scraping process."""
    if state_manager.scraping_status['is_running']:
        raise HTTPException(status_code=400, detail="Scraping is already running")
    
    background_tasks.add_task(scraping_worker)
    return {"status": "started", "message": "BIN scraping process started"}

@api_router.post("/scraping/stop")
async def stop_scraping():
    """Stop the BIN scraping process."""
    if not state_manager.scraping_status['is_running']:
        raise HTTPException(status_code=400, detail="Scraping is not running")
    
    state_manager.update_scraping_status(is_running=False)
    return {"status": "stopping"}

@api_router.get("/scraping/progress")
async def get_scraping_progress():
    """Get detailed scraping progress information."""
    db = BinDatabase()
    try:
        total_urls = db.get_total_urls_count()
        processed = db.get_processed_urls_count()
        
        return {
            "total_banks": total_urls,
            "processed_banks": processed,
            "remaining_banks": total_urls - processed,
            "completion_percentage": (processed / total_urls * 100) if total_urls > 0 else 0,
            "processed_bins": state_manager.scraping_status['processed_bins'],
            "current_bank": state_manager.scraping_status['current_bank'],
            "failed_urls": state_manager.scraping_status['failed_urls'],
            "is_running": state_manager.scraping_status['is_running'],
            "start_time": state_manager.scraping_status['start_time'],
            "last_update": state_manager.scraping_status['last_update']
        }
    finally:
        db.close()

@api_router.get("/scraping/resumable")
async def check_resumable():
    db = BinDatabase()
    try:
        total = db.get_total_urls_count()
        processed = db.get_processed_urls_count()
        is_resumable = total > 0 and processed < total
        
        response = {
            "resumable": is_resumable,
            "total": total,
            "processed": processed,
            "remaining": total - processed if total > 0 else 0
        }
        print(response)
        return response
    finally:
        db.close()

@api_router.post("/scraping/reset")
async def reset_state():
    """Reset the state manager to initial state."""
    state_manager.reset()
    return {"status": "State reset successfully"}

@api_router.get("/search")
async def search_bins(
    bin_prefix: Optional[str] = None,
    bank: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000)
):
    """Search BINs with optional filters."""
    db = BinDatabase()
    try:
        cursor = db.conn.cursor()
        
        query = """
            SELECT bin_number, pays, emetteur, marque_carte, type_carte, niveau_carte
            FROM bin_cards
            WHERE 1=1
        """
        params = []
        
        if bin_prefix:
            query += " AND bin_number LIKE ?"
            params.append(f"{bin_prefix}%")
        
        if bank:
            query += " AND emetteur LIKE ?"
            params.append(f"%{bank}%")
            
        if country:
            query += " AND pays LIKE ?"
            params.append(f"%{country}%")
            
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [{
            "bin": row[0],
            "country": row[1],
            "bank": row[2],
            "brand": row[3],
            "type": row[4],
            "level": row[5]
        } for row in results]
    finally:
        db.close()

app.include_router(api_router)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='BIN Database Manager Web Application')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the application on')
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)