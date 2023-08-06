

def auth_header(api_key, accept_content_type):
    return dict(Autorization=f"Bearer {api_key}",
            Accept=accept_content_type)

