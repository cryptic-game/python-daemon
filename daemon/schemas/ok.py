from pydantic import BaseModel

from ..utils import example


class OKResponse(BaseModel):
    ok: bool

    Config = example(ok=True)


ok_response = {"ok": True}
