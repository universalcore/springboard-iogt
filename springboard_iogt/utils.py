def randomize_query(s_obj, seed=None):
    return s_obj.query_raw({
        "function_score": {
            "functions": [
                {"random_score": {"seed": seed}}
            ],
            "score_mode": "sum"
        }})
