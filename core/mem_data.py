IMG_CACHE = dict()


def get_image_cache(key):
    return IMG_CACHE.get(key)


def update_image_cache(obj):
    IMG_CACHE.update(obj)

