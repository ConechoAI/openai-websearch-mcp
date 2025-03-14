from .server import mcp


def main():
    mcp.run()


def runner():
    import sys, json, traceback
    from starlette.testclient import TestClient
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(mcp.router)

    try:
        # create a test client
        client = TestClient(app)

        print("MCP Server started, waiting for requests from stdin...", file=sys.stderr)

        # Handle requests until EOF
        while True:
            try:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break

                # Check if the input is valid JSON
                try:
                    request_data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON input: {str(e)}", file=sys.stderr)
                    continue

                print(f"Received request: {request_data}", file=sys.stderr)
                # Construct the path
                jsonrpc_method = request_data.get("method")
                path = f"mcp/{mcp.name}/{jsonrpc_method}"

                # Send the request to the ASGI application
                try:
                    response = client.post(path, json=request_data)
                    response_data = response.json()

                    # Send the response back to the client
                    print(json.dumps(response_data, ensure_ascii=False))
                    sys.stdout.flush()
                except Exception as e:
                    # Send the error message to stderr
                    print(f"Error processing request: {str(e)}", file=sys.stderr)
                    print(traceback.format_exc(), file=sys.stderr)
                    sys.stderr.flush()

            except Exception as e:
                # Send the error message to stderr
                print(f"Unexpected error: {str(e)}", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
                sys.stderr.flush()
    except Exception as e:
        # Startup error
        print(f"Startup error: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
