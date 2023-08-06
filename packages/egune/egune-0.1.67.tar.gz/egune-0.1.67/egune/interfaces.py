from typing import List, Dict, Any, Union


class Interface:
    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)


class Text(Interface):
    def __init__(self, mutations: Union[str, Dict[str, str]]):
        if isinstance(mutations, str):
            self.mutations = {"original": mutations}
        else:
            self.mutations = mutations

    def add_mutation(self, key, mutation):
        self.mutations[key] = mutation

    def get(self, key="original") -> str:
        return self.mutations[key] if key in self.mutations else ""

    def to_dict(self):
        return self.mutations

    def get_keys(self):
        return [k for k in self.mutations]

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict.get("mutations", ""),
        )


class Entity(Interface):
    def __init__(
        self,
        name: str,
        input_type: str,
        val: str,
        sidx: int,
        eidx: int,
        confidence: float,
    ) -> None:
        self.name = name
        self.input_type = input_type
        self.val = val
        self.sidx = sidx
        self.eidx = eidx
        self.confidence = confidence

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict.get("name", ""),
            dict.get("input_type", ""),
            dict.get("val", ""),
            dict.get("sidx", 0),
            dict.get("eidx", 0),
            dict.get("confidence", 0),
        )


class Intent(Interface):
    def __init__(self, chosen: str, scores: Dict[str, float]) -> None:
        self.chosen = chosen
        self.scores = scores

    def is_intent_chosen(self):
        return self.chosen != ""

    def confidence(self):
        return self.scores[self.chosen]

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict.get("chosen", ""),
            dict.get("scores", {}),
        )


class Misc(Interface):
    def __init__(
        self,
        buttons: List[str] = None,
        multiselects: List[str] = None,
        checkboxes: List[str] = None,
        date: str = None,
        file: str = None,
        latitude: str = None,
        longitude: str = None,
        nfc: Any = None,
        form: Dict[str, Any] = None,
    ):
        self.buttons = buttons
        self.multiselects = multiselects
        self.checkboxes = checkboxes
        self.date = date
        self.file = file
        self.latitude = latitude
        self.longitude = longitude
        self.nfc = nfc
        self.form = form

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["buttons"] if "buttons" in dict else None,
            dict["multiselects"] if "multiselects" in dict else None,
            dict["checkboxes"] if "checkboxes" in dict else None,
            dict["date"] if "date" in dict else None,
            dict["file"] if "file" in dict else None,
            dict["latitude"] if "latitude" in dict else None,
            dict["longitude"] if "longitude" in dict else None,
            dict["nfc"] if "nfc" in dict else None,
            dict["form"] if "form" in dict else None,
        )


class State(Interface):
    ADD_ACTIVE_INTENT = "add_active_intent"
    DEACTIVATE_INTENT = "deactivate_intent"
    UPDATE_SLOT = "update_slot"

    def __init__(
        self,
        active_intents: List,
        slots: Dict,
        prev_entities: List,
        last_intent: str,
        last_message: str,
        last_responses: List,
        api: Dict
    ):
        self.active_intents = active_intents
        self.slots = slots
        self.prev_entities = prev_entities
        self.last_intent = last_intent
        self.last_message = last_message
        self.last_responses = last_responses
        self.api = api

    def apply_user_message(self, msg):
        self.prev_entities.extend([(e.name, e.val) for e in msg.entities])
        self.last_intent = msg.intent.chosen
        self.last_message = msg.text.get()

    def apply_response(self, responses):
        self.last_responses = [r.msg.code for r in responses if r.name == "say"]

    def apply_api(self, key, val):
        self.api[key] = val

    def apply_operation(self, command, data):
        if command == State.ADD_ACTIVE_INTENT:
            if data not in self.active_intents:
                self.active_intents.append(data)
        elif command == State.DEACTIVATE_INTENT:
            self.active_intents.remove(data)
        else: # command == State.UPDATE_SLOT:
            if data == "":
                del self.slots[command]
            else:
                self.slots[command] = data

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["active_intents"] if "active_intents" in list else None,
            dict["slots"] if "slots" in dict else None,
            dict["prev_entities"] if "prev_entities" in list else None,
            dict["last_intent"] if "last_intent" in str else None,
            dict["last_message"] if "last_message" in str else None,
            dict["last_responses"] if "last_responses" in list else None,
            dict["api"] if "api" in dict else None
        )

    @classmethod
    def empty(cls):
        return cls(
            [],
            {},
            [],
            "",
            "",
            [],
            {}
        )


class UserMessage(Interface):
    def __init__(
        self,
        user_id: str = None,
        text: Text = None,
        misc: Misc = None,
        intent: Intent = None,
        entities: List[Entity] = None,
        state: State = None,
    ):
        self.user_id = user_id
        self.text = text
        self.misc = misc
        self.intent = intent
        self.entities = entities
        self.state = state

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "text": self.text.to_dict() if self.text is not None else None,
            "misc": self.misc.to_dict() if self.misc is not None else None,
            "intent": self.intent.to_dict() if self.intent is not None else None,
            "entities": [e.to_dict() for e in self.entities]
            if self.entities is not None
            else None,
            "state": self.state.to_dict(),
        }

    def select(self, key):
        args = key.split(":")
        if args[0] == "text":
            return self.text.get(args[1])  # type:ignore
        elif args[0] == "intent":
            return self.intent.chosen  # type:ignore
        elif args[0] == "entity":
            for e in self.entities:  # type:ignore
                if e.name == args[1]:
                    return e.val
        return ""

    def get_entity_val(self, name, default=None):
        if self.entities is not None:
            for e in self.entities:
                if e.name == name:
                    return e.val
        return default

    def get_tracker_val(self, name, default=None):
        return self.trackers.get(name, default)

    @classmethod
    def from_dict(cls, message_dict):
        def is_exist(key):
            return key in message_dict and message_dict[key] is not None

        obj = cls()
        obj.user_id = message_dict["user_id"] if is_exist("user_id") else None
        obj.text = Text(message_dict["text"]) if is_exist("text") else None
        obj.misc = Misc.from_dict(message_dict["misc"]) if is_exist("misc") else None
        obj.intent = (
            Intent.from_dict(message_dict["intent"]) if is_exist("intent") else None
        )
        obj.entities = (
            [Entity.from_dict(e) for e in message_dict["entities"]]
            if is_exist("entities")
            else None
        )
        obj.trackers = message_dict["trackers"] if is_exist("trackers") else {}
        return obj


class ActorMessage(Interface):
    def __init__(
        self,
        user_id: str = None,
        code: str = None,
        text: str = None,
        list: List[str] = None,
        buttons: List[str] = None,
        checkboxes: List[str] = None,
        multiselects: List[str] = None,
        images: List[str] = None,
        files: List[str] = None,
        misc: Any = None,
    ):
        self.user_id = user_id
        self.code = code
        self.text = text
        self.buttons = buttons
        self.checkboxes = checkboxes
        self.multiselects = multiselects
        self.images = images
        self.files = files
        self.list = list
        self.misc = misc

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["user_id"] if "user_id" in dict else None,
            dict["code"] if "code" in dict else None,
            dict["text"] if "text" in dict else None,
            dict["list"] if "list" in dict else None,
            dict["buttons"] if "buttons" in dict else None,
            dict["checkboxes"] if "checkboxes" in dict else None,
            dict["multiselects"] if "multiselects" in dict else None,
            dict["images"] if "images" in dict else None,
            dict["files"] if "files" in dict else None,
            dict["misc"] if "misc" in dict else None,
        )


class Command:
    class Do(Interface):
        def __init__(self, action: str, request: UserMessage) -> None:
            self.name = "do"
            self.action = action
            self.request = request

        def app(self):
            return self.action.split(":")[0]

        def action_name(self):
            return self.action.split(":")[1]

        def to_dict(self):
            return {
                "name": "do",
                "action": self.action,
                "request": self.request.to_dict(),
            }

        @classmethod
        def from_dict(cls, dict):
            return cls(dict["action"], UserMessage.from_dict(dict["request"]))

    class Say(Interface):
        def __init__(self, msg: ActorMessage, user_message: UserMessage):
            self.name = "say"
            self.msg = msg
            self.user_message = user_message

        def to_dict(self):
            return {
                "name": "say",
                "msg": self.msg.to_dict(),
                "user_message": self.user_message.to_dict(),
            }

        @classmethod
        def from_dict(cls, dict):
            return cls(
                ActorMessage.from_dict(dict["msg"]),
                UserMessage.from_dict(dict["user_message"]),
            )

    @staticmethod
    def publish_commands(commands: List[Interface]):
        return [c.to_dict() for c in commands]

    @staticmethod
    def decode_commands(commands: List[Dict[str, Any]]):
        c = []
        for command in commands:
            if command["name"] == "do":
                c.append(Command.Do.from_dict(command))
            elif command["name"] == "say":
                c.append(Command.Say.from_dict(command))
            else:
                raise ValueError("command not supported")
        return c


class ApiRequest(Interface):
    def __init__(self, user_id: str, app: str, action: str, request: UserMessage, response=None, payload=None):
        self.user_id = user_id
        self.app = app
        self.action = action
        self.request = request
        self.response = response
        self.payload = payload

    @classmethod
    def from_dict(cls, response_dict):
        return cls(
            response_dict.get("user_id", ""),
            response_dict.get("app", ""),
            response_dict.get("action", ""),
            UserMessage.from_dict(response_dict.get("request", {})),
            response_dict.get("response", ""),
            response_dict.get("payload", {})
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "app": self.app,
            "action": self.action,
            "request": self.request.to_dict(),
            "response": self.response,
            "payload": self.payload
        }


class EventRequest(Interface):
    def __init__(self, request):
        self.name = request["name"]
        self.user_id = request["user_id"]
        self.app_id = request["app_id"]
        self.data = request["data"]
        self.id = request["id"]
