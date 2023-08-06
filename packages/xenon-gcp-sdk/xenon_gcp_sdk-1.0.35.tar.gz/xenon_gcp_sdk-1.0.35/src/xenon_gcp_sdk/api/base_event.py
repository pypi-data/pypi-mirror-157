import dataclasses
import json


class BaseEvent:
    def to_dict(self):
        return json.loads(self.as_json())

    def as_json(self):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        return json.dumps(self, cls=EnhancedJSONEncoder)
