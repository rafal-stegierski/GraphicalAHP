import pandas as pd 
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse 
from fastapi.responses import FileResponse
from rethinkdb import RethinkDB 
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware 
import logging 
from decision_calculations import divide_numbers, get_eig, get_cr, calculate_final_preference, calculate_drawing_ahp, calculate_classic_ahp
import bcrypt
import secrets
import xlsxwriter
from uuid import uuid4

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_origins=["http://localhost", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = RethinkDB()

def get_rethinkdb_conn():
    return r.connect("rethinkdb", 28015)

@app.get("/api/checkToken")
async def check_token(request: Request):
   auth_header = request.headers.get("Authorization")
   if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
   token = auth_header.split(" ")[1]
   try:
       conn = get_rethinkdb_conn()
       result = list(r.db("test").table("users").filter({"token": token}).run(conn))
       conn.close()
       if len(result)>0:
           return { "token": "ok" }
       raise HTTPException(status_code=401, detail="Invalid or missing token")
   except Exception as e:
       logging.error(f"User data access error {e}")
       raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/login")
async def get_login(request: Request):
   try:
       data = await request.json()
       conn = get_rethinkdb_conn()
       user = list(r.db("test").table("users").filter({"username": data['username']}).run(conn))
       conn.close()
       username = user[0]["username"]
       password = user[0]["password"].encode("utf-8")
       correct_password = bcrypt.checkpw(data['password'].encode("utf-8"), password)
       if correct_password:
           token = secrets.token_hex(32)
           conn = get_rethinkdb_conn()
           user = list(r.db("test").table("users").filter({"username": data['username']}).update({"token":token}).run(conn))
           conn.close()
           return { "token": token }
       else:
           return {}
   except Exception as e:
       logging.error(f"User data access error {e}")
       raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/surveys")
async def get_surveys():
    try:
        conn = get_rethinkdb_conn()
        surveys = list(r.db("test").table("surveys").run(conn))
        conn.close()
        logging.info(f"Returning surveys")
        return surveys
    except Exception as e:
        logging.error(f"Error during getting surveys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/survey-results/calculate")
async def calculate_survey_results(request: Request):
    survey_id = request.get("survey_id")
    method = request.get("method")
    comparisons = request.get("comparisons")

    if not survey_id or not method or not comparisons:
        raise HTTPException(status_code=400, detail="Missing required data")

    if method == "classic":
        results = calculate_classic_ahp(comparisons)
        return JSONResponse(content={
            "final_preference_vector": results["avg_priority_vector"],
            "consistency_ratio": results["avg_cr"]
        })

    elif method == "drawing":
        results = calculate_drawing_ahp(comparisons)
        return JSONResponse(content={
            "final_preference_vector": results["avg_priority_vector"],
            "consistency_ratio": results["avg_cr"]
        })

    else:
        raise HTTPException(status_code=400, detail="Invalid method")

@app.get("/api/survey-results/{survey_id}/calculate")
async def calculate_survey_results_from_list(survey_id: str, method: str):
    logging.info(f"Received request for survey ID: {survey_id} with method: {method}")
    try:
        conn = get_rethinkdb_conn()

        results = list(r.db("test").table("survey_results").filter({"survey_id": survey_id}).run(conn))
        conn.close()

        if not results:
            raise HTTPException(status_code=404, detail="No results for survey")

        logging.info(f"Getting results")

        all_cr_values = []
        all_preference_vectors = []

        for result in results:
            survey_type = result.get("survey_type")

            if survey_type != method:
                logging.info(f"Skipping results of different survey type: {survey_type}")
                continue

            comparisons = result['results']
            logging.info(f"Comparisons data structure: {comparisons}")

            if method == 'classic':
                calculation_result = calculate_classic_ahp(comparisons)
            elif method == 'drawing':
                calculation_result = calculate_drawing_ahp(comparisons)
            else:
                raise HTTPException(status_code=400, detail="Wrong method")

            all_cr_values.append(calculation_result["avg_cr"])
            all_preference_vectors.append(calculation_result["avg_priority_vector"])

        if not all_cr_values or not all_preference_vectors:
            raise HTTPException(status_code=400, detail="No results for selected method")

        avg_cr = sum(all_cr_values) / len(all_cr_values)
        avg_preference_vector = [sum(x) / len(x) for x in zip(*all_preference_vectors)]

        options = []

        for element in results[0]['results']:
            if element['optionA'] not in options:
                options.append(element['optionA'])
            if element['optionB'] not in options:
                options.append(element['optionB'])

        return JSONResponse(content={
            "options": options,
            "average_preference_vector": avg_preference_vector,
            "average_cr": avg_cr,
            "all_preference_vectors": all_preference_vectors,
            "all_cr_values": all_cr_values
        })

    except Exception as e:
        logging.error(f"Error during results computation: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/save-survey")
async def save_survey(survey_data: dict):
    try:
        conn = get_rethinkdb_conn()
        survey_id = str(uuid4())
        new_survey = {
            'id': survey_id,
            'name': survey_data.get('name'),
            'criteria': survey_data.get('criteria'),
            'options': survey_data.get('options'),
        }

        r.db("test").table("surveys").insert(new_survey).run(conn)
        conn.close()

        return {"status": "success", "message": "Survey saved successfully", "survey_id": survey_id}
    except Exception as e:
        logging.error(f"Error during saving survey: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/save-survey-results")
async def save_survey_results(survey_results:dict):
    try:
        survey_id = survey_results.get('survey_id')
        expert_name = survey_results.get('expertName')
        results = survey_results.get('results')
        survey_type = survey_results.get('survey_type') or survey_results.get('type')
        if not survey_id:
            logging.error("No survey ID")
        if not results:
            logging.error("No survey data")
        if not survey_type:
            logging.error("No survey type")

        if not survey_id or not results or not survey_type:
            raise HTTPException(status_code=400, detail="No survey ID, results or type")

        conn = get_rethinkdb_conn()
        submission_id = str(uuid4())

        new_entry = {
            'submission_id': submission_id,
            'survey_id': survey_id,
            'expertName': expert_name,
            'results': results,
            'survey_type': survey_type
        }

        r.db("test").table("survey_results").insert(new_entry).run(conn)
        conn.close()

        logging.info(f"Survey results saved succesfullty. Submission ID: {submission_id}")
        return {
            "status": "success",
            "message": "Survey results saved successfully",
            "submission_id": submission_id
        }

    except Exception as e:
        logging.error(f"Error during saving survey results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/survey-results/count/{survey_id}")
async def get_survey_results_count(survey_id: str):
    try:
        conn = get_rethinkdb_conn()
        logging.error(f"Get data for survey: {survey_id}")
        count = r.db("test").table("survey_results").filter({"survey_id": survey_id}).count().run(conn)
        conn.close()
        logging.error(f"Total number: {count}")
        return {"count": count}
    except Exception as e:
        logging.error(f"Error during getting survey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/survey-results/{survey_id}")
async def get_survey_results(survey_id: str):
    logging.info(f"Received request for survey results for ID: {survey_id}")
    try:
        conn = get_rethinkdb_conn()
        results = list(r.db("test").table("survey_results").filter({"survey_id": survey_id}).run(conn))
        conn.close()
        logging.info(f"Results for survey ID {survey_id}: {results[0]['expertName']}")
        return results
    except Exception as e:
        logging.error(f"Error during getting survey results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/survey-results/{survey_id}/download")
async def get_survey_results(survey_id: str):
    logging.info(f"Received request for survey results for ID: {survey_id}")
    try:
        conn = get_rethinkdb_conn()
        results = list(r.db("test").table("survey_results").filter({"survey_id": survey_id}).run(conn))
        conn.close()
        workbook = xlsxwriter.Workbook(survey_id + ".xlsx")
        bold = workbook.add_format({'bold': True})
        worksheet_classic = workbook.add_worksheet("Classic AHP")
        worksheet_drawing = workbook.add_worksheet("Drawing AHP")
        row_classic = 1
        row_drawing = 1
        col = 0

        worksheet_classic.write(0, 0, 'Id', bold)
        worksheet_classic.write(0, 1, 'Expert Name', bold)
        worksheet_classic.write(0, 2, 'Submission Id', bold)
        worksheet_classic.write(0, 3, 'Criterion', bold)
        worksheet_classic.write(0, 4, 'Local Id', bold)
        worksheet_classic.write(0, 5, 'Option A', bold)
        worksheet_classic.write(0, 6, 'Option B', bold)
        worksheet_classic.write(0, 7, 'Left Value', bold)
        worksheet_classic.write(0, 8, 'Right Value', bold)

        worksheet_drawing.write(0, 0, 'Id', bold)
        worksheet_drawing.write(0, 1, 'Expert Name', bold)
        worksheet_drawing.write(0, 2, 'Submission Id', bold)
        worksheet_drawing.write(0, 3, 'Criterion', bold)
        worksheet_drawing.write(0, 4, 'Local Id', bold)
        worksheet_drawing.write(0, 5, 'Option A', bold)
        worksheet_drawing.write(0, 6, 'Option B', bold)
        worksheet_drawing.write(0, 7, 'Left Value', bold)
        worksheet_drawing.write(0, 8, 'Right Value', bold)

        for result in results:
            if result['survey_type']=='classic':
                worksheet_classic.write(row_classic, 0, result['id'])
                worksheet_classic.write(row_classic, 1, result['expertName'])
                worksheet_classic.write(row_classic, 2, result['submission_id'])
                for element in result['results']:
                    worksheet_classic.write(row_classic, 3, element['criterion'])
                    worksheet_classic.write(row_classic, 4, element['id'])
                    worksheet_classic.write(row_classic, 5, element['optionA'])
                    worksheet_classic.write(row_classic, 6, element['optionB'])
                    worksheet_classic.write(row_classic, 7, element['value']['leftValue'])
                    worksheet_classic.write(row_classic, 8, element['value']['rightValue'])
                    row_classic += 1
            if result['survey_type']=='drawing':
                worksheet_drawing.write(row_drawing, 0, result['id'])
                worksheet_drawing.write(row_drawing, 1, result['expertName'])
                worksheet_drawing.write(row_drawing, 2, result['submission_id'])
                for element in result['results']:
                    worksheet_drawing.write(row_drawing, 3, element['criterion'])
                    worksheet_drawing.write(row_drawing, 4, element['id'])
                    worksheet_drawing.write(row_drawing, 5, element['optionA'])
                    worksheet_drawing.write(row_drawing, 6, element['optionB'])
                    for val in element['value']:
                        worksheet_drawing.write(row_drawing, 7, val['x'])
                        worksheet_drawing.write(row_drawing, 8, val['y'])
                        row_drawing += 1
        worksheet_classic.autofit()
        worksheet_drawing.autofit()
        workbook.close()
        return FileResponse(path = survey_id + ".xlsx", filename = survey_id + ".xlsx", media_type='application/vnd.ms-excel')
    except Exception as e:
        logging.error(f"Error during getting survey results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/survey-results")
async def get_all_survey_results():
    try:
        conn = get_rethinkdb_conn()
        results = list(r.db("test").table("survey_results").run(conn))
        conn.close()
        return results
    except Exception as e:
        logging.error(f"Error during getting survey results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def create_table_if_not_exists():
    conn = get_rethinkdb_conn()
    db_list = r.db_list().run(conn)
    if "test" not in db_list:
        r.db_create("test").run(conn)
    table_list = r.db("test").table_list().run(conn)
    if "surveys" not in table_list:
        r.db("test").table_create("surveys").run(conn)
    if "survey_results" not in table_list:
        r.db("test").table_create("survey_results").run(conn)
    if "users" not in table_list:
        r.db("test").table_create("users").run(conn)
        r.db("test").table("users").insert({"username": "admin", "password": "secret"})
    conn.close()

@app.delete("/api/surveys/{survey_id}")
async def delete_survey(survey_id: str):
    logging.info(f"Received request to delete survey with ID: {survey_id}")
    try:
        conn = get_rethinkdb_conn()
        survey = r.db("test").table("surveys").get(survey_id).run(conn)
        if not survey:
            conn.close()
            logging.error(f"Survey with ID {survey_id} not found")
            raise HTTPException(status_code=404, detail="Survey not found")
        r.db("test").table("surveys").get(survey_id).delete().run(conn)
        conn.close()
        logging.info(f"Survey with ID {survey_id} successfully deleted")
        return {"status": "success", "message": f"Survey with ID {survey_id} deleted"}
    except Exception as e:
        logging.error(f"Error while deleting survey: {e}")
        raise HTTPException(status_code=500, detail="Error while deleting survey")

create_table_if_not_exists()
