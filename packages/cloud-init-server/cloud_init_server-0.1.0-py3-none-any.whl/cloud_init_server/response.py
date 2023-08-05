from typing import Any, Dict

from yaml import SafeDumper
import yaml
from starlette.responses import PlainTextResponse as PlainTextResponse

class YAMLResponse(PlainTextResponse):
    use_doc: bool
    media_type: str = "text/yaml"

    def render(self, content: Any) -> bytes:
        original_content = content
        if hasattr(content, "__root__"):
            content = content.__root__
        elif hasattr(content, "dict"):
            content = content.dict()
        if not (isinstance(content, dict) or isinstance(content, list)):
            raise ValueError("Invalid yaml object response. Object is not a dict nor list.")
        
        header = ""
        if hasattr(original_content, "yaml_header"):
            header = "\n".join([f"# {line.strip()}" for line in original_content.yaml_header.splitlines()]) + "\n#\n"
        header = header + yaml.dump(content, default_flow_style=False, Dumper=SafeDumper)
        return header.encode("utf-8")
        
