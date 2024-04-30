import asyncio

from _get_request import get_request

async def fetch_test():
    url = 'https://jsonplaceholder.typicode.com/todos/1'
    headers = {'Content-Type': 'application/json'}
    params = {}  # No parameters needed for this request

    # Using the get_request function to make an API call
    try:
        response = await get_request(url, headers, params)
        print("Response:", response)
    except Exception as e:
        print("An error occurred:", e)

# Run the asynchronous test function
if __name__ == "__main__":
    asyncio.run(fetch_test())
