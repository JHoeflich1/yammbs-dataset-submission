# adapted from https://developers.zenodo.org/?python#quickstart-upload

import json
import logging
import os

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

URL = "https://sandbox.zenodo.org"
TOKEN = os.environ["ZENODO_TOKEN"]


def check_status(response, expect):
    assert (
        response.status_code == expect
    ), f"Request failed ({response.status_code}), body: {response.json()}"


auth = ("Bearer", TOKEN)

# this just checks that we can make requests with our token, so it can probably
# be skipped in general
logger.info("checking API access")
r = requests.get(f"{URL}/api/deposit/depositions", auth=auth)
check_status(r, 200)

# create a new empty upload
logger.info("creating an empty upload")
headers = {"Content-Type": "application/json"}
r = requests.post(
    f"{URL}/api/deposit/depositions", auth=auth, json={}, headers=headers
)
check_status(r, 201)

res = r.json()
bucket_url = res["links"]["bucket"]
deposition_id = res["id"]

# this is a real sqlite file from a yammbs run on the industry dataset, bzipped
# to save space. even the zipped form is 165 M
logger.info("uploading file")
filename = "test.sqlite.bz2"
with open(filename, "rb") as f:
    r = requests.put(f"{bucket_url}/{filename}", data=f, auth=auth)

check_status(r, 201)

# add the metadata
logger.info("updating metadata")
title = "Test benchmark upload"
data = {
    "metadata": {
        "title": title,
        "upload_type": "dataset",
        "description": title,
        "creators": [{"name": "Westbrook, Brent", "affiliation": "OMSF"}],
    }
}
r = requests.put(
    f"{URL}/api/deposit/depositions/{deposition_id}",
    auth=auth,
    data=json.dumps(data),
    headers=headers,
)
check_status(r, 200)

exit(0)  # exit for now to avoid publishing while testing

# publish the result
r = requests.post(
    f"{URL}/api/deposit/depositions/{deposition_id}/actions/publish",
    auth=auth,
)
print(r.status_code)
print(r.json())

# the response here is supposed to be a Deposition resource with a doi_url
# field that I think is probably the best thing to return to the user
res = r.json()
print(res["doi_url"])