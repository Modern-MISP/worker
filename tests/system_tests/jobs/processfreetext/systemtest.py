import requests

url = "http://localhost:5000/"
headers = {"Authorization": "Bearer 1409"}
data = {
    "user": {"user_id": 0},
    "data": {
        "data": "This is an ip 1.2.3.4"
    }
}


def simple_testcase():
    start_worker_response = requests.post(url+"worker/processFreeText/enable", headers=headers).json()
    if start_worker_response["success"] == True or start_worker_response["message"] == 'Processfreetext-Worker already enabled':
    create_response = requests.post(url + "job/processFreeText", headers=headers, json=data).json()
    print(create_response)
    job_id = create_response["job_id"]
    status = False
    while not status:
        status_response = requests.get(url + f"job/{job_id}/status", headers=headers).json()
        if status_response["status"] == "success":
            status = True
            print("here")
    print(requests.get(url + f"job/{job_id}/result", headers=headers).json())



simple_testcase()
