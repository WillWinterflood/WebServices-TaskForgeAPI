import os
import signal
import subprocess
import sys
import time


def get_int_env(name, default):
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        print(f"Invalid {name}={value!r}; using default {default}", flush=True)
        return default


def run_migrations():
    attempts = max(1, get_int_env("STARTUP_DB_MAX_RETRIES", 10))
    delay_seconds = max(1, get_int_env("STARTUP_DB_RETRY_DELAY_SECONDS", 3))

    for attempt in range(1, attempts + 1):
        print(f"Running database migrations ({attempt}/{attempts})", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
            check=False,
        )
        if result.returncode == 0:
            print("Database migrations completed", flush=True)
            return

        if attempt == attempts:
            raise SystemExit(result.returncode)

        print(
            f"Migration attempt failed with exit code {result.returncode}; retrying in {delay_seconds}s",
            flush=True,
        )
        time.sleep(delay_seconds)


def launch_api():
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    print(f"Starting API server on {host}:{port}", flush=True)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
    )

    def forward_signal(signum, _frame):
        if process.poll() is None:
            process.send_signal(signum)

    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, forward_signal)

    return process.wait()


if __name__ == "__main__":
    run_migrations()
    raise SystemExit(launch_api())
