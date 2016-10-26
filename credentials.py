def get_keys(option):
    if option == 0:
        consumer_key    = "opadfiiudafioiadfouadiosojHOUdioafuidiudfjisOR5YcohKMscXJoQQ"
        consumer_secret = "VmJWfW-023jopafeopedXZDioadufkJemmpcp98P16ya5X9yO5VssRB36eM8"
        oauth_token     = "1490307913-uuj7sitXZ2-08-0adfi-CoDzvXva6wFVruW4RTJ46W56QD5B7"
        oauth_secret    = "kaaAYvezm4ASVbByHE49N8iyVl37qpioudoufaoaouiudfjk6QjAWPiuV5lE"
    elif option == 1:
        consumer_key    = "hJguioifuoiasd7D1awFmpCdiOzEpOSHuiaodufiaodiuosuoadfiououOUIw"
        consumer_secret = "IfR5bCdaofuHlq5K4ct90koadfkojadoBwS0DxoSPyHGBCnDS5NLgnGFQqb4"
        oauth_token     = "540154793-deBUXrbVZgrWR6Sob0nVMadfopijjnJbJfC9maeeBrIJZtCdEb"
        oauth_secret    = "o18zavzD5sdafouiaoidfuoaYDw9JHCqglo2mRvX8MsxoDYdT3godafjvDaVc"
    else:
        raise KeyError("wrong key option")
        exit(1)
    keys = {"client_key" : consumer_key,
            "client_secret" : consumer_secret,
            "resource_owner_key" : oauth_token,
            "resource_owner_secret" : oauth_secret}
    return keys
