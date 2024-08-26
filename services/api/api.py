from fastapi import FastAPI
from typing import Optional
import os
from google.cloud import discoveryengine_v1
from google.protobuf.json_format import MessageToDict
import json
from typing import Optional, List, Dict
app = FastAPI()

PROJECT_ID = os.getenv("PROJECT_ID", "dialogflow-433314")
DATASTORE_ID = os.getenv("DATASTORE_ID", "data-youtube_1724675515786")
DATASTORE_LOCATION = os.getenv("DATASTORE_ID", "global")
def format_search_results(
    response_pager: discoveryengine_v1.SearchResponse,
) -> List[Dict]:
    response_pager_dict = MessageToDict(response_pager._pb)
    return (
        "{response:"
        + json.dumps(
            [
                result["document"]["structData"]
                for result in response_pager_dict["results"]
            ]
        )
        + "}"
    )

def get_search_results(
    search_query: str, page_size: Optional[int] = 3
) -> discoveryengine_v1.SearchResponse:
    """Performs a search query in Discovery Engine and returns the results.

    Args:
        search_query: The search query text.
        page_size: (Optional) The max number of search results to return per page. Defaults to 3.

    Returns:
        A SearchResponse object containing the search results.
    """

    # Create the Discovery Engine client
    client = discoveryengine_v1.SearchServiceClient(client_options=None)

    # Construct the full resource name of the serving config
    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=DATASTORE_LOCATION,
        data_store=DATASTORE_ID,
        serving_config="default_config",
    )

    # Build the search request
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config, query=search_query, page_size=1
    )

    # Perform the search and return the response
    return format_search_results(client.search(request))

@app.get("/speaker")
async def get_speaker(query: Optional[str] = None):

    search_results = get_search_results(query)

    return search_results

if __name__ == "__main__":

    # run fastapi
    import uvicorn

    uvicorn.run("api:app", host="localhost", port=8000, reload=True)
