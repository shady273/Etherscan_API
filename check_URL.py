def check_url(url):
    if url[-4:] == 'json' and url[:8] == 'https://':
        return url
    elif url[-4:] == 'json' and url[:7] == 'ipfs://':
        good_url = ('https://ipfs.io/ipfs/' + url[7:])
        return good_url
