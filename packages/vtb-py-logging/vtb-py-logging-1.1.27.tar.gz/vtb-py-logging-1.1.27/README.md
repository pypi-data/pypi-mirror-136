# Overview
This package setups the logging system in properly format. By default, it logs to console and to 
file `/var/log/<app_name>/<app_name>.log` in json format.
In the case if the code is run under `Pycharm` or under `Windows`, i.e. developer workstation, 
the default folder will be: `<project_folder> / log`.  

Also, this library adds request_id field in the logs.

The following environment variable can be used to configure this package:
* `LOG_LEVEL`  -- log level, by default "INFO". 
* `LOG_DIR` -- directory for log files. By default, it has value /var/log/<app_name>
* `LOG_FILENAME` -- filename of the log file. By default <app_name>.log
* `LOG_OUTPUT` -- log's handlers to the output logs. Supported the following format: simple, stderr, json
* `LOG_COLORED` -- output colored logs in stderr. By default, it is true
* `LOG_SQL` -- enable django SQL logs. By default,  it is false
* `LOGGING_DEFAULT_LEVEL` -- log level for the "default" logger. It is deprecated and added only compatible reason.
* `LOGGING_DEFAULT_HANDLER` -- handler name for the "default" logger. It is deprecated and added only compatible reason.



## Add to Django application
* Add `vtb-py-logging==1.1.12` or newer in `requirements.txt`

* Configure extra logging instead of default. 
```
    LOGGING_CONFIG = "vtb_py_logging.django.setup_logging"
    LOGGING = 1   # any values except False/None
    LOGGING_APP_NAME  # name of application. This name is used as default log file name
    REQUEST_ID_PREFIX = "<PREFIX>"  # the value should be two or three characters. 
                                    # It is used as preffix to generate new request_id if is not received.
                                    # Example of prefixes: 
                                    #     orw (orchestrator web)
                                    #     orm (orchestrator messaging)
                                    #     ss (state service)
```

* if the default logging configuration is not enough (for example you want to change log level for some loggers), 
in this case you can add the config setup function like this:

```
    # settings/setup_log.py
    
    import logging
    from vtb_py_logging.configure import initialize_logging
    from django.conf import settings
    
    def setup_logging(config):
        initialize_logging(settings.LOGGING_APP_NAME) 

        # manual logger configuration. For example it disable logs from the pika library
        pika_logger = logging.getLogger("pika")
        if not settings.DEBUG:
            pika_logger.setLevel(logging.WARNING)
```

Also `LOGGING_CONFIG` should point to this function like this:
```
LOGGING_CONFIG="<project_name>.settings.setup_log.setup_logging"
```

* Add middleware that pickup the request_id from the request header and store in the local context. 
This middleware should be on the first place in `MIDDLEWARE` variable in file `settings/main.py`:
  

```
    MIDDLEWARE = [
       'vtb_py_logging.django.request_id_middleware',
       ....
    ]
```    

* Drop file `settings/logging.py` and remote link to it from the 
variable `INCLUDED_SETTINGS` in the `settings/main.py` file.

* Do not forget to update `Dockerfile` to create properly directory for logs and configure access flags:

```
    RUN mkdir /var/log/<app_name>/ && chgrp -R 0 /var/log/<app_name>/ && chmod -R g=u /var/log/<app_name>/
```


* Do not forget to update docker-compose*.yaml files to use properly volumes


## Add logs to unittests

* To configure logging in pytest, you can add the following function in the `conftest.py`: 


```
    def pytest_configure(config):
        from app import utils
        os.environ["LOG_OUTPUT"] = "simple"
        setup_logging("test", level="DEBUG")
```

## Add to aiohttp based application

* Add `vtb-py-logging==1.1.12` or newer in `requirements.txt`

* Add file to the setting / configuring folder:
        

```
        from vtb_py_logging.configure import initialize_logging

        def setup_logging(name="orchestrator"):
            initialize_logging(name)
```            

* Call `setup_logging` in the `main.py` or `run.py`. I.e. this function should be called during configuration 
of the app, before creating web application instance

* Added request_id middleware in web application:


```            
    from vtb_py_logging.aiohttp import request_id_middleware
    ...
    app = web.Application(loop=loop, middlewares=[request_id_middleware("<Request ID Preffix>")])
```            


## Utils examples

* Example of passing request_id in the rest call:


```            
    from vtb_py_logging.request_id import get_request_id_header
    headers = {'Authorization': xxxx,
               **get_request_id_header()}
    async with aiohttp.ClientSession(headers=headers) as session:
```            

* get request_id from the current context:


```            
    from vtb_py_logging.request_id import get_context_request_id
    ...
    request_id = get_context_request_id()
```            

