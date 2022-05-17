from http import HTTPStatus

from api30 import Api30, Request, Response

app = Api30()


def index(request: Request) -> Response:
    print('Index view!')
    return Response("Hello world!")


def docs(request: Request) -> Response:
    return Response({
        'docs': [
            {'pk': 1, 'data': 'Doc1'}
        ]
    })


def doc(request: Request, pk: str) -> Response:
    if int(pk) == 1:
        return Response({'pk': 1, 'data': 'Doc1'})
    return Response(None, status=HTTPStatus.NOT_FOUND)


app.get('/', index)
app.get('/docs', docs)
app.get(r'/docs/(\d+)', doc)


class RequestLogger:
    def pre(self, request: Request):
        print(f'Pre {request.path}')

    def post(self, request: Request, response: Response):
        print(f'Post: {request.path}, status: {response.status}')


app.push_middleware(RequestLogger())


# $ gunicorn my_app:app
