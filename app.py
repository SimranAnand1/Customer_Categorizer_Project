from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from src.pipeline.prediction_pipeline import PredictionPipeline
from src.pipeline.train_pipeline import TrainPipeline
from src.constant.application import *

import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Log environment variables
print("MONGODB_URL:", os.getenv("MONGODB_URL"))
print("MONGODB_URL_KEY:", os.getenv("MONGODB_URL_KEY"))

app = FastAPI()

# Set up template directory
templates = Jinja2Templates(directory="templates")

# Enable CORS for all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic Model for JSON input
class CustomerData(BaseModel):
    Age: int
    Education: int
    Marital_Status: int
    Parental_Status: int
    Children: int
    Income: float
    Total_Spending: float
    Days_as_Customer: int
    Recency: int
    Wines: int
    Fruits: int
    Meat: int
    Fish: int
    Sweets: int
    Gold: int
    Web: int
    Catalog: int
    Store: int
    Discount_Purchases: int
    Total_Promo: int
    NumWebVisitsMonth: int


# ✅ Train Model API
@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        return JSONResponse(content={"status": True, "message": "Training successful!"})
    except Exception as e:
        return JSONResponse(content={"status": False, "error": str(e)}, status_code=500)


# ✅ Test Environment Variables API
@app.get("/test_env")
async def test_env():
    mongo_url = os.getenv("MONGODB_URL")
    return {"MONGODB_URL": mongo_url}


# ✅ Render Customer Form (UI)
@app.get("/")
async def predictGetRouteClient(request: Request):
    try:
        return templates.TemplateResponse(
            "customer.html", {"request": request, "context": "Rendering"}
        )
    except Exception as e:
        return JSONResponse(content={"status": False, "error": str(e)}, status_code=500)


# ✅ Predict API (JSON Input)
@app.post("/")
async def predictRouteClient(data: CustomerData):
    try:

        print("Received data:", data.dict())  # Debugging step
        # Convert JSON to list format expected by model
        input_data = [
            data.Age, data.Education, data.Marital_Status, data.Parental_Status, data.Children,
            data.Income, data.Total_Spending, data.Days_as_Customer, data.Recency, data.Wines,
            data.Fruits, data.Meat, data.Fish, data.Sweets, data.Gold, data.Web, data.Catalog,
            data.Store, data.Discount_Purchases, data.Total_Promo, data.NumWebVisitsMonth
        ]

        # Run prediction
        prediction_pipeline = PredictionPipeline()
        predicted_cluster = prediction_pipeline.run_pipeline(input_data=input_data)
        #return {"message": "Prediction received", "data": data.dict()}
        resp={"predicted_cluster": int(predicted_cluster[0])}
        return JSONResponse(content=resp)

    
    except Exception as e:
        return JSONResponse(content={"status": False, "error": str(e)}, status_code=500)


# ✅ Run FastAPI Application
if __name__ == "__main__":
    import uvicorn

    print("MONGODB_URL:", os.getenv("MONGODB_URL"))
    print("MONGODB_URL_KEY:", os.getenv("MONGODB_URL_KEY"))


    uvicorn.run(app, host="127.0.0.1", port=APP_PORT)
