import os

def get_inriver_token():
    token = os.getenv("IN_RIVER_API_KEY")
    if not token:
        raise ValueError("IN_RIVER_API_KEY is not set in environment variables.")
    return token 
    
    
    
def get_inriver_header():
        headers_inRiver = dict(Accept='application/json')
        headers_inRiver['Content-type'] = 'application/json'
        headers_inRiver['X-inRiver-APIKey'] = get_inriver_token()
        return headers_inRiver
    
