from unicore.hub.client.utils import same_origin


def randomize_query(s_obj, seed=None):
    return s_obj.query_raw({
        "function_score": {
            "functions": [
                {"random_score": {"seed": seed}}
            ],
            "score_mode": "sum"
        }})


def get_redirect_url(request, param_name='next'):
    redirect_url = request.GET.get(param_name)
    if redirect_url and same_origin(redirect_url, request.current_route_url()):
        return redirect_url
    return request.route_url('home')
