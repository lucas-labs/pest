from ..core.application import PestApplication
from ..exceptions.http.http import ExceptionResponse
from ..utils.functions import model_schema


def patch(app: PestApplication) -> None:
    """Patches the OpenAPI schema"""
    openapi_schema = app.openapi()
    if not openapi_schema:
        return

    for path in openapi_schema['paths']:
        for method in openapi_schema['paths'][path]:
            if openapi_schema['paths'][path][method]['responses'].get('422'):
                openapi_schema['paths'][path][method]['responses']['400'] = openapi_schema['paths'][
                    path
                ][method]['responses']['422']

                # change schema ref to ErrorReponse instead of HTTPValidationError
                openapi_schema['paths'][path][method]['responses']['400']['content'][
                    'application/json'
                ]['schema']['$ref'] = '#/components/schemas/ExceptionResponse'

                # set example
                openapi_schema['paths'][path][method]['responses']['400']['content'][
                    'application/json'
                ]['example'] = {
                    'code': 400,
                    'error': 'Bad Request',
                    'message': [
                        'error hint',
                    ],
                }

                # remove 422
                openapi_schema['paths'][path][method]['responses'].pop('422')

        components = openapi_schema.get('components')
        if components:
            # remove ValidationError and HTTPValidationError
            schemas = components.get('schemas')
            if schemas:
                if schemas.get('ValidationError'):
                    schemas.pop('ValidationError')
                if schemas.get('HTTPValidationError'):
                    schemas.pop('HTTPValidationError')
                if not schemas.get('ExceptionResponse'):
                    schemas['ExceptionResponse'] = model_schema(ExceptionResponse)

        app.openapi_schema = openapi_schema
