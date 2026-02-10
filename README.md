# ai-agent-application
# Required packages (will later add to requirements):
# streamlit google-generativeai python-dotenv
To run application on local server:
```streamlit run main.py --server.port <port number>```
- Ensure the server is up:
    ```curl -I http://localhost:8501```

Check list of available models that work with your API key:
```python list_models.py```
 - Ensure you have a working api key... we use (Google Gemini's API|https://ai.google.dev/gemini-api/docs/api-key)
 
