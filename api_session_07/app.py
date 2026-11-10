import connexion
app = connexion.FlaskApp(__name__)

app.add_api(
    "openapi.yaml",
    validate_responses=True,
)
if __name__ == "__main__":
    app.run(port=8000)