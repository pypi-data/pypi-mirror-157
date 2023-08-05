from typing import Union
from cloud_init_server.exceptions import ServiceConfigError
from cloud_init_server.response import YAMLResponse
from cloud_init_server.config_generator import ConfigGenerator, ConfigRequestQueryParams, ConfigRequest
from cloud_init_server.create_app import create_app
from fastapi import Depends, HTTPException, Request

app = create_app("cloud-init")

config_generator = ConfigGenerator.create_from_config("./cloud_init_server.yaml")

@app.get("/flush")
def flush_cache():
    """
    Discard any present cache.
    """
    return YAMLResponse(config_generator.flush_cache())

@app.get("/config/{config}")
def get_config(request: Request, config: str, extra_params: ConfigRequestQueryParams = Depends()) -> str:
    """
    Get configuration for a specific resource.
    As a config parameter please use the path of the yaml template to be rendered with slashes replaced by '.'.
    For example you can have ./src_config directory with file ./src_config/a/b/service.yaml
    To render it just use:
      GET /config/a.b.service?node_id=SOME_ARBITRARY_NODE_IDENTIFICATOR
    """
    try:
        config = config_generator.get_configuration(ConfigRequest(
            **{
                **extra_params.dict(),
                **dict(config=config, extra_params=request.query_params),
            },
        ))
        return YAMLResponse(config)
    except ServiceConfigError as e:
        raise HTTPException(status_code=422, detail=str(e))

