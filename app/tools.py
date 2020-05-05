from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TakeAndGo",
        version="0.0.1",
        description="Smart bookshelf project",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/Svintsova/TakeAndGo/master/public/logo192.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema