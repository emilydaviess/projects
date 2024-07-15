import requests
from time import sleep


def rapid_api(self, extension, optional_params=False, query_string=False):

    url = self.url + extension
    print("url", url, query_string) if query_string else print("url", url)
    if optional_params:
        querystring = query_string
        request = requests.get(url, headers=self.headers, params=querystring)
    else:
        request = requests.get(url, headers=self.headers)

    if not request:
        self.print_warning("No data returned from RapidAPI.")
        return None, None
    response = request.json()["response"]
    paging = request.json()[
        "paging"
    ]  # some endpoints have paging, which we'll need to handle
    if not response:
        if not paging:
            self.print_warning("No response or paging option within the response.")
            return None, None

        self.print_warning(
            "No response option within the response, but we have paging."
        )
        return None, paging

    return response, paging


def handle_pagination(paging, func, *args, **kwargs):
    # rate limit is 30 requests per minute, hence sleep for 10s between requests
    sleep(10)

    # if there are more pages, we'll need to loop through them
    if paging["current"] < paging["total"]:
        print(
            "There are more pages to loop through - recall function with page:",
            paging["current"] + 1,
        )

        kwargs["api_paging"] = paging["current"] + 1
        func(*args, **kwargs)


def calculate_season(date):
    month = date.month
    year = date.year
    return str(year) if month > 7 else str(year - 1)
