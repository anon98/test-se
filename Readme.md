# PyVolt Setup

## Steps

1. **Build Docker Image:**

    ```bash
    docker build --no-cache -t pyvolt .
    ```

2. **Run Docker Container:**

    ```bash
    docker run -it -v $(pwd)/examples:/app/examples pyvolt
    ```

3. **Example Usage:**

    ```bash
    python3 quickstart/run_nv_state_estimator.py
    ```
