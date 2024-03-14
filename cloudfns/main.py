import os
import json
import functions_framework
from flask import jsonify, request

def process_api_request(request):

    request_json = request.get_json()

    report_year = request_json.get("reportYear")
    input_question = request_json.get("InputQuestion")

    response_json = {
        "reportYear": report_year,
        "QuestionnaireSummary": {
            "response": "Response1",
            "status": "success",
            "citation": "citation1",
            "documentReference": "http://www.abc.com",
            "accuracy": "0.8",
            "confidenceScores": "0.8"
        },
    }

    return json.dumps(response_json), 200

