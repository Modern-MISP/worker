import json

url: str = "http://worker.mmisp.cert.kit.edu:80"
headers: json = {"Authorization": "Bearer mispmisp"}

old_misp_url: str = "https://misp-02.mmisp.cert.kit.edu"
old_misp_headers: json = {"Authorization": "RlmznD5uUKg3MIaPYfzSK99WXVhcHJ1V692Ta7AE",
                          "Content-Type": "application/json",
                          "Accept": "application/json"}