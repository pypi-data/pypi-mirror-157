"""functions for adding caches to python functions using decoration"""

from __future__ import annotations

import functools
import typing

if typing.TYPE_CHECKING:
    from typing_extensions import ParamSpec
    from typing import TypeVar

    P = ParamSpec('P')
    R = TypeVar('R')

from . import cachetypes
from . import spec


def cache(
    cachetype: spec.CachetypeSpec, add_cache_args: bool = True, **cache_kwargs
) -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, R]]:
    """decorate function to add a cache

    ## Added Function Args
    - these parameters are added to every decorated function:
        - cache_load: bool of whether to load the result from cache
        - cache_save: bool of whether to save the result to cache
        - cache_verbose: bool of whether to print cache usage information
    - avoid adding these args with `add_cache_args=False`

    ## Inputs

    #### Decorator Options
    - cachetype: type of config to use, one of the following options
        - 'memory': cache stored in memory within a dict
        - 'disk': cache stored to disk in pickle object
        - BaseCase instance: pass in an instance of a subclass of BaseCache
    - add_cache_kwargs: bool of whether to add args to function (see above)

    #### Miscellaneous Options
    - safety: one of ['thread', 'process', None] for concurrency safety
    - verbose: bool of whether to be verbose
    - cache_name: str name of cache, used in verbose reporting statements
    - old_f: function being decorated by cache, None for standalone cache

    #### Hash Options
    - hash_mode: str of hash mode, either 'json' or 'json_digest'
    - f_hash: function for computing hash
        - should take same args as decorated function
    - normalize_hash_inputs: bool of whether to normalize function args
        - if f() has one arg, g, then normalizing will make f(5) == f(g=5)
          according to the hashes computed by the hash
    - hash_include_args: list of str names of arguments used to compute hash
        - this requires normalizing hash inputs
    - hash_exclude_args: list of str names of arguments excluded from hash
        - this requires normalizing hash inputs

    #### Eviction Options
    - ttl: Timelength of maximum age of entries in cache
    - max_size: int count of maximum number of entries in cache
    - max_size_policy: one of ['lru', 'fifo', 'lfu', None]

    #### Statistic Tracking Options
    - track_basic_stats: bool of whether to track basic usage stats
    - track_detailed_stats: bool of whether to track creations and accesses
    - track_creation_times: bool of whether to track creation times
    - track_access_times: bool of whether to track access times
    - track_access_counts: bool of whether to track access counts

    #### DiskCache Options
    - cache_dir: str of path to store cache data, tmpdir if None
    - file_format: str of file format of output on disk (e.g. json)

    ## Returns
    - decorated function that uses cache for saving and loading function outputs
    """

    def decorator(f: typing.Callable[P, R]) -> typing.Callable[P, R]:

        # create cache
        CacheClass = cachetypes.get_cache_class(cachetype)
        cache_instance = CacheClass(old_f=f, **cache_kwargs)

        # create new function for decorator to return
        new_f = _create_new_f(
            old_f=f,
            cache_instance=cache_instance,
            add_cache_args=add_cache_args,
        )

        return new_f

    return decorator


def _create_new_f(
    old_f: typing.Callable[P, R], cache_instance, add_cache_args
) -> typing.Callable[P, R]:
    """create new function by decorating old_f to use cache_instance

    ## Inputs
    - old_f: function to be decorated
    - cache_instance: BaseCache instance for function to use
    - add_cache_args: bool of whether to add cache control args to function
    """

    if add_cache_args:

        # ensure not overwriting args
        import inspect

        argspec = inspect.getfullargspec(old_f)
        arg_names: list[str] = argspec.args + argspec.kwonlyargs
        if argspec.varargs is not None:
            arg_names.append(argspec.varargs)
        if argspec.varkw is not None:
            arg_names.append(argspec.varkw)

        cache_args = ['cache_load', 'cache_save', 'cache_verbose']
        for cache_arg in cache_args:
            if cache_arg in arg_names:
                raise Exception(
                    'function already has arg '
                    + str(cache_arg)
                    + ', use add_cache_args=False'
                )

        @functools.wraps(old_f)
        def new_f(
            *args,
            cache_load: bool = True,
            cache_save: bool = True,
            cache_verbose: typing.Optional[bool] = None,
            **kwargs
        ) -> R:
            return execute_with_cache(
                old_f=old_f,
                cache_instance=cache_instance,
                args=args,
                kwargs=kwargs,
                # cache_load=cache_load,
                # cache_save=cache_save,
                # cache_verbose=cache_verbose,
            )

    else:

        @functools.wraps(old_f)
        def new_f(*args, **kwargs):
            return execute_with_cache(
                old_f=old_f,
                cache_instance=cache_instance,
                args=args,
                kwargs=kwargs,
                cache_load=True,
                cache_save=True,
                cache_verbose=None,
            )

    new_f.cache = cache_instance  # type: ignore

    return new_f


def execute_with_cache(
    old_f,
    args,
    kwargs,
    cache_instance,
    cache_load=True,
    cache_save=True,
    cache_verbose=None,
):
    """execute old_f with specified inputs and use cache if appropriate

    TODO: might be worth it to create a totally separate decorator for async

    ## Inputs
    - old_f: function to call
    - args: list of input args
    - kwargs: dict of input kwargs
    - cache_instance: BaseCache instance to use
    - cache_load: bool of whether to attempt to load from cache
    - cache_save: bool of whether to save output to cache
    - cache_verbose: bool of whether to print cache operation info
    """
    is_coroutine = _iscoroutinefunction(old_f)

    # set verbosity
    if cache_verbose is None:
        cache_verbose = cache_instance.verbose

    # compute entry_hash
    if cache_load or cache_save:
        entry_hash = cache_instance.compute_entry_hash(args=args, kwargs=kwargs)

    # attempt to load from cache
    loaded_from_cache = None
    if cache_load:
        loaded_from_cache = cache_instance.load_entry(
            entry_hash=entry_hash,
            verbose=cache_verbose,
            must_exist=False,
        )

    # retrieve output
    if loaded_from_cache is not None:

        # use output from cache
        if is_coroutine:

            async def async_get_from_cache():
                return loaded_from_cache

            output = async_get_from_cache()
        else:
            output = loaded_from_cache

    else:

        if is_coroutine:

            output = async_f_wrapper(
                old_f=old_f,
                args=args,
                kwargs=kwargs,
                cache_save=cache_save,
                entry_hash=entry_hash,
                cache_instance=cache_instance,
                cache_verbose=cache_verbose,
            )

        else:

            # compute output
            output = old_f(*args, **kwargs)

            # save to cache
            if cache_save:
                cache_instance.save_entry(
                    entry_hash, output, verbose=cache_verbose
                )

    return output


async def async_f_wrapper(
    old_f, args, kwargs, cache_save, entry_hash, cache_instance, cache_verbose
):

    # await result
    output = await old_f(*args, **kwargs)

    # save to cache
    if cache_save:
        cache_instance.save_entry(entry_hash, output, verbose=cache_verbose)

    return output


def _iscoroutinefunction(function):
    """lightweight version of inspect.iscoroutinefunction()"""

    import types

    if not isinstance(function, types.FunctionType):
        return False

    # inspect.CO_COROUTINE
    flag = 128

    return bool(function.__code__.co_flags & flag)
