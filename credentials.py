def get_keys(option):
    """Twitter app keys"""
    if option == 0:
        consumer_key    = "981238Hpiehr89020jisOR5YcohKMscXJoQQ"
        consumer_secret = "VmJWfWedekXZp98P16ya5X9yO5VssRB36eM8"
        oauth_token     = "1490307913zvXva6wFVruW4RTJ46W56QD5B7"
        oauth_secret    = "kaaAYvezm4yHE49N8iyVl37q6QjAWPiuV5lE"
    elif option == 1:
        consumer_key    = "981238Hpiehr89020jisOR5YcohKMscXJoQQ"
        consumer_secret = "VmJWfWedekXZp98P16ya5X9yO5VssRB36eM8"
        oauth_token     = "1490307913zvXva6wFVruW4RTJ46W56QD5B7"
        oauth_secret    = "kaaAYvezm4yHE49N8iyVl37q6QjAWPiuV5lE"
    else:
        raise KeyError("wrong key option")
        exit(1)

    keys = {"client_key" : consumer_key,
            "client_secret" : consumer_secret,
            "resource_owner_key" : oauth_token,
            "resource_owner_secret" : oauth_secret}
    return keys
