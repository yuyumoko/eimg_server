import datetime
import functools
import inspect

cache_data = {}
cache_data_ttl = {}


def get_func_key(func, *fn_args, **fn_kwargs):
    bound = inspect.signature(func).bind(*fn_args, **fn_kwargs)
    bound.apply_defaults()
    bound.arguments.pop("self", None)
    return hash(f"{func.__name__}@{bound.arguments}")


def async_cache(ttl=None):
    """

    example:
    @async_cache
    @async_cache(ttl=datetime.timedelta(hours=1))
    """

    def wrap(func):
        @functools.wraps(func)
        async def wrapped(*fn_args, **fn_kwargs):
            if fn_kwargs.get("no_cache", False):
                return await func(*fn_args, **fn_kwargs)

            ins_key = get_func_key(func, *fn_args, **fn_kwargs)
            default_data = {"time": None, "value": None}

            if not isinstance(ttl, datetime.timedelta):
                data = cache_data.get(ins_key, default_data)
                if not data["value"]:
                    data["value"] = await func(*fn_args, **fn_kwargs)
                    cache_data[ins_key] = data
                return data["value"]
            else:
                data = cache_data_ttl.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data["time"] or now - data["time"] > ttl:
                data["value"] = await func(*fn_args, **fn_kwargs)
                data["time"] = now
                data["ttl"] = ttl
                cache_data_ttl[ins_key] = data

            return data["value"]

        return wrapped

    if callable(ttl):
        return wrap(ttl)
    return wrap


def cache(ttl=None):
    """
    example:
    @cache
    @cache(ttl=datetime.timedelta(hours=1))
    """

    def wrap(func):
        @functools.wraps(func)
        def wrapped(*fn_args, **fn_kwargs):
            if fn_kwargs.get("no_cache", False):
                return func(*fn_args, **fn_kwargs)

            ins_key = get_func_key(func, *fn_args, **fn_kwargs)
            default_data = {"time": None, "value": None}

            if not isinstance(ttl, datetime.timedelta):
                data = cache_data.get(ins_key, default_data)
                if not data["value"]:
                    data["value"] = func(*fn_args, **fn_kwargs)
                    cache_data[ins_key] = data
                return data["value"]
            else:
                data = cache_data_ttl.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data["time"] or now - data["time"] > ttl:
                data["value"] = func(*fn_args, **fn_kwargs)
                data["time"] = now
                data["ttl"] = ttl
                cache_data_ttl[ins_key] = data

            return data["value"]

        return wrapped

    if callable(ttl):
        return wrap(ttl)
    return wrap


# async def auto_check_ttl():
#     for key in list(cache_data_ttl.keys()):
#         now = datetime.datetime.now()
#         data = cache_data_ttl.get(key)
#         if now - data["time"] > data["ttl"]:
#             del cache_data_ttl[key]
