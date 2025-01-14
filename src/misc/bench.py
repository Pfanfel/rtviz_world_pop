import asyncio
import time
import httpx
import random


API_URL = "http://127.0.0.1:8000/api/male/{z}/{y}/{x}/{raster_index}/{detailLevel}/{heightLevel}/{maxValue}"

# Define the ranges for z, y, x (within normal tile ranges)
Z_RANGE = (1, 8)  # Zoom levels typically range from 0 to 20
X_RANGE = (0, 200 - 1)  # x depends on the zoom level, up to 2^z - 1
Y_RANGE = (0, 100 - 1)  # y depends on the zoom level, up to 2^z - 1


def generate_random_tile():
    z = random.randint(*Z_RANGE)
    max_xy = 2**z - 1
    x = random.randint(0, max_xy)
    y = random.randint(0, max_xy)
    return z, y, x


async def fetch_tile(client, z, y, x):
    url = API_URL.format(
        z=z, y=y, x=x, raster_index=1, detailLevel=5, heightLevel=3, maxValue=1
    )
    start_time = time.time()
    try:
        response = await client.get(url)
        elapsed_time = time.time() - start_time
        print(f"Request to {url} took {elapsed_time:.2f} seconds")
        return response.status_code, response.text
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Request to {url} failed after {elapsed_time:.2f} seconds")
        return "Error", str(e)


async def main(concurrent_requests):
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(concurrent_requests):
            z, y, x = generate_random_tile()
            tasks.append(fetch_tile(client, z, y, x))

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        success_count = sum(1 for status, _ in results if status == 200)
        print(
            f"Total time for {concurrent_requests} requests: {end_time - start_time:.2f} seconds"
        )
        print(f"Successful responses: {success_count}/{concurrent_requests}")


if __name__ == "__main__":
    asyncio.run(main(20))  # Number of concurrent requests
