import requests


def rapid_api(self, extension, optional_params=False, query_string=False):

    url = self.url + extension
    print("url", url)
    if optional_params:
        querystring = query_string
        request = requests.get(url, headers=self.headers, params=querystring)
    else:
        request = requests.get(url, headers=self.headers)

    if not request:
        print("No data returned from RapidAPI.")
        return

    response = request.json()["response"]
    paging = request.json()[
        "paging"
    ]  # some endpoints have paging, which we'll need to handle
    if not response:
        print("No response option within the response.")
        return

    return response, paging


def handle_pagination(paging, func, *args, **kwargs):
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
