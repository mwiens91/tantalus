"""Views to support the current implementation of tasks.

At some point these should be replaced by just making RESTful API calls.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from tantalus.backend.serializers import read_models_from_http_request

class ReadModelsView(APIView):
    """A view to consume JSON and execute the read_models function."""
    def post(self, request):
        """Parse a JSON dump or 400."""
        # Try parsing the request
        try:
            json_list = request.data['json_list']
        except KeyError as e:
            return Response(
                data={'Exception': "'json_list' not provided!"},
                status=status.HTTP_400_BAD_REQUEST)

        # Consume data and create model instances
        try:
            read_models_from_http_request(json_list)
        except Exception as e:
            return Response(
                data={'Exception': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Success!
        return Response(data=request.data, status=status.HTTP_200_OK)
