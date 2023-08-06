from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_comments_lists(request, *args, **kwargs):
    comments = [
        {"id": 1, "comment": "Comment 1"},
        {"id": 2, "comment": "Comment 2"}
    ]
    return Response(comments, status=status.HTTP_200_OK)
