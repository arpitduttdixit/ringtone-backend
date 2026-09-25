# Ringtone Backend

Backend service for asynchronous text-to-speech (TTS) generation.

The application exposes a FastAPI API, queues long-running work in Redis using RQ, and processes jobs through a separate worker. TTS generation is delegated to a local Tortoise TTS installation.

## Architecture

```text
Client
  |
  v
FastAPI (main.py)
  |
  v
Redis / RQ task_queue
  |
  v
RQ Worker (worker.py)
  |
  v
Tortoise TTS (tts_job.py)
  |
  v
Generated WAV file
```

Using a queue keeps expensive TTS generation out of the HTTP request lifecycle and allows the API and worker processes to run independently.

## Tech Stack

- Python
- FastAPI
- Redis
- RQ (Redis Queue)
- Tortoise TTS
- Pydantic
- python-dotenv

## Repository Structure

| File | Purpose |
| --- | --- |
| `main.py` | FastAPI application and API endpoints |
| `worker.py` | RQ worker that consumes jobs from Redis |
| `tts_job.py` | Executes Tortoise TTS generation |
| `job.py` | Simple background-job test function |
| `colab_worker.ipynb` | Notebook for running/experimenting with the worker environment |

## Environment Variables

Create a `.env` file in the project root:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

`.env` is ignored by Git and should not be committed.

## Running Locally

### 1. Install dependencies

The project currently does not include a dependency lock file or `requirements.txt`. At minimum, the API/worker code requires packages such as:

```bash
pip install fastapi uvicorn redis rq python-dotenv
```

Tortoise TTS must also be installed and available at:

```text
tortoise/do_tts.py
```

### 2. Start Redis

Make sure the Redis instance configured through the environment variables is running and reachable.

You can verify connectivity after starting the API with:

```http
GET /test-redis
```

### 3. Start the API

```bash
uvicorn main:app --reload
```

By default, FastAPI will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 4. Start the worker

In another terminal:

```bash
python worker.py
```

The worker listens to the `task_queue` Redis queue.

## API Endpoints

### Health check

```http
GET /
```

Example response:

```json
{
  "responseCode": 200,
  "responseMessage": "success"
}
```

### Redis connection test

```http
GET /test-redis
```

Checks whether the application can connect to Redis.

### Create a TTS job

```http
POST /tts
Content-Type: application/json
```

Example body:

```json
{
  "text": "Hello from the ringtone generator",
  "voice": "random",
  "preset": "ultra_fast"
}
```

The request is intended to enqueue TTS generation rather than perform the expensive operation inside the API request.

### Check TTS job status

```http
GET /tts/{job_id}
```

Possible states include:

- `processing`
- `completed`
- `failed`

## TTS Job

`tts_job.py` invokes Tortoise TTS using a subprocess similar to:

```bash
python tortoise/do_tts.py \
  --text "<text>" \
  --voice "<voice>" \
  --preset "<preset>" \
  --output_path "<output-file>"
```

Generated audio is stored as a WAV file under the configured output directory.

## Current Development Notes

The repository is still under development. A few areas currently need cleanup before the full TTS flow can run end-to-end:

- `main.py` enqueues `tasks.print_num`, while the test function currently lives in `job.py`.
- The arguments supplied when enqueueing `run_tts_command` do not currently match the function signature in `tts_job.py`.
- `uuid()` in the TTS endpoint should be replaced with an appropriate UUID call such as `uuid.uuid4()`.
- The TTS endpoint references `copy.upload_to_drive`, but that module is not present in this repository.
- A dependency file such as `requirements.txt` or `pyproject.toml` should be added for reproducible setup.

## Future Improvements

- Add dependency management with `requirements.txt` or `pyproject.toml`
- Add structured job chaining for TTS generation and upload
- Persist generated-file metadata
- Restrict CORS for production deployments
- Add request validation and limits for TTS text
- Add automated tests
- Add Docker support for the API, Redis, and worker
