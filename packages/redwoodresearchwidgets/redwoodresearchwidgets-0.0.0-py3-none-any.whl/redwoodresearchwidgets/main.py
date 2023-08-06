import os
import sys
import time
import json
import datetime
import asyncio
import threading
import traceback
from typing import Dict, List, Optional, Any

import IPython
import msgpack
import numpy
import torch
import requests
import tornado.web

import streamdb
import streamdb.rrserve

publish_code = """
<html>
    <body>
        <div id="rrinterp-root">Loading...</div>
        <script type="module">
import * as rrinterp from 'https://rrserve.s3.us-west-2.amazonaws.com/%(rrserve_key)s';
let root = document.getElementById('rrinterp-root');

async function main() {
    const path = `https://rrserve.s3.us-west-2.amazonaws.com/%(rrserve_data_key)s`;
    const response = await fetch(path);
    const dataBuffer = await response.arrayBuffer();
    console.log('Got data:', dataBuffer);

    rrinterp.renderWidget(root, rrinterp.PageController, {
        buildId: %(rrserve_id)s,
        buildCategory: %(rrserve_category)r,
        isInJupyter: false,
        requests: [
            {
                message: {
                    kind: 'render',
                    dest: 'rrinterp-root',
                    name: %(name)s,
                    remoteUrl: %(remoteUrl)s,
                },
                buffers: [dataBuffer],
            },
        ],
    });
}

main();
        </script>

        <div style="margin-left: 20px; margin-top: 50px; font-size: 80%%; opacity: 0.8;">
            To render this component in your notebook:
            <pre>data = rrinterp.fetch_data("https://rrserve.s3.us-west-2.amazonaws.com/%(rrserve_data_key)s")
widget = rrinterp.render(%(name)s, **data)</pre>
        </div>
    </body>
</html>
"""

page_injected_code = """
<div id="rrinterp-widgets-main-injected-div">[%(rrserve_id)s] Initializing.</div>
<script type="module">
window.rrinterpMainDiv = document.getElementById("rrinterp-widgets-main-injected-div");
window.rrinterpMainDiv.innerText = "[%(rrserve_id)s] Initializing..";
import * as rrinterp from 'https://rrserve.s3.us-west-2.amazonaws.com/%(rrserve_key)s';
window.rrinterpMainDiv.innerText = "[%(rrserve_id)s] Initializing...";
rrinterp.renderWidget(window.rrinterpMainDiv, rrinterp.PageController, {
    buildId: %(rrserve_id)s,
    buildCategory: %(rrserve_category)r,
    isInJupyter: true,
});
</script>
"""

global_lock = threading.Lock()
global_comm = None
global_last_message = None
global_last_exception = None
global_widgets: Optional[Dict[str, Any]] = None
global_branch: Optional[str] = None
global_already_initted = False
global_rrserve_key: Optional[str] = None
global_rrserve_id: Optional[int] = None
global_rrserve_category: Optional[str] = None
global_registered_host: Optional[str] = None
global_remote_execution_widget = None
global_remote_execution_thread = None


def get_unique_identifier() -> str:
    time_part = datetime.datetime.now().strftime("%y-%m-%dT%H:%M")
    random_part = os.urandom(4).hex()
    return f"{time_part}-{random_part}"


def rrinterpbus_message(comm, open_msg):
    global global_comm
    global_comm = comm

    @comm.on_msg
    def _recv(msg):
        global global_last_message, global_widgets, global_last_exception
        global_last_message = msg
        kind = msg["content"]["data"]["kind"]
        if kind == "init":
            with global_lock:
                global_widgets = {entry["name"]: entry for entry in msg["content"]["data"]["widgetList"]}
        elif kind == "callback":
            try:
                with global_lock:
                    function = callables_table[msg["content"]["data"]["id"]]
                data = msgpack_decode(msg["buffers"][0])
                value = function(*data)
            except:
                global_last_exception = traceback.format_exc()
                value = None
            global_comm.send(
                {
                    "kind": "callbackResult",
                    "token": msg["content"]["data"]["token"],
                },
                buffers=[msgpack_encode(value)],
            )


def init(branch: str = "main"):
    global global_already_initted, global_branch, global_rrserve_key, global_rrserve_id, global_rrserve_category
    global_branch = branch

    ipython = IPython.get_ipython()
    if ipython is None:
        raise RuntimeError("Attempting to init not from an IPython context")

    if not global_already_initted:
        ipython.kernel.comm_manager.register_target("rrinterpbus", rrinterpbus_message)
    global_already_initted = True

    category = "rrinterp-widgets:" + branch
    response = streamdb.rrserve.rrserve_query([category])["rows"]
    if "key" not in response or not response["key"]:
        raise RuntimeError("No rrinterp-widgets build for branch: %r" % branch)
    global_rrserve_key = response["key"][0]
    global_rrserve_id = response["id"][0]
    global_rrserve_category = category
    code = page_injected_code % {
        "rrserve_key": global_rrserve_key,
        "rrserve_id": global_rrserve_id,
        "rrserve_category": global_rrserve_category,
    }
    IPython.display.display(IPython.display.HTML(code))

    # if update_all_widgets:
    #    for widget in global_widget_registry:
    #        widget.update()


class AllowCORS:
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def options(self, *args):
        self.set_status(204)
        self.finish()


class RpcHandler(AllowCORS, tornado.web.RequestHandler):
    def post(self, function_token):
        global global_last_exception
        try:
            with global_lock:
                function = callables_table[function_token]
            args = msgpack_decode(self.request.body)
            value = function(*args)
        except:
            global_last_exception = traceback.format_exc()
            value = None
        self.write(msgpack_encode(value))


class HealthHandler(AllowCORS, tornado.web.RequestHandler):
    def get(self):
        self.write('{"kind": "ok"}')


def setup_remote_execution(host: str, port: int):
    global global_remote_execution_widget, global_remote_execution_thread, global_registered_host
    # global_remote_execution_widget = render("RemoteExecutionWidget", host=host, port=port, request_count=0)
    global_registered_host = host

    def thread_main():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Thread starting up")
        application = tornado.web.Application(
            [
                ("/rpc/(.*)", RpcHandler),
                ("/health", HealthHandler),
            ]
        )
        application.listen(port, "0.0.0.0")
        tornado.ioloop.IOLoop.current().start()

    global_remote_execution_thread = threading.Thread(target=thread_main)
    global_remote_execution_thread.start()


def get_widgets():
    widgets = None
    with global_lock:
        widgets = global_widgets
    # for _ in range(30):
    #    with global_lock:
    #        widgets = global_widgets
    #    if widgets:
    #        break
    #    time.sleep(0.2)
    if widgets is None:
        raise RuntimeError("No widgets list yet -- did you call rrinterp.init() yet?")
    return widgets


callables_table = {}


def _msgpack_special_encoder(is_for_remote: bool):
    def _encode(obj):
        if isinstance(obj, numpy.ndarray):
            dtype = obj.dtype.name
            # Unfortunately there is no Int64Array type in Javascript.
            # So we convert int64 arrays to int32 arrays, and encode them over the wire that way.
            # However, we maintain the original type to allow for (somewhat) reversible decoding.
            # This is pretty absurdly confusing, so I might change this later.
            if obj.dtype == numpy.int64:
                obj = obj.astype(numpy.int32)
            if obj.dtype == numpy.uint64:
                obj = obj.astype(numpy.uint32)
            return {
                "$$type$$": "ndarray",
                "dtype": dtype,
                "shape": obj.shape,
                "data": obj.tobytes(),
                "v": 0,  # I might change the over-the-wire encoding later, so I want a version tag.
            }
        if isinstance(obj, torch.Tensor):
            array_encoding = _encode(obj.detach().cpu().numpy())
            return {
                "$$type$$": "torch",
                "array": array_encoding,
                "device": str(obj.device),
            }
        if isinstance(obj, Widget):
            return {
                "$$type$$": "widget-ref",
                "id": obj.random_id,
            }
        if callable(obj):
            function_token = os.urandom(12).hex()
            with global_lock:
                callables_table[function_token] = obj
            if is_for_remote:
                if not global_registered_host:
                    raise ValueError("Cannot remote-serialize a function until you've setup remote code mode")
                return {
                    "$$type$$": "remote-callback",
                    "id": function_token,
                    "host": global_registered_host + "/rpc/" + function_token,
                }
            return {
                "$$type$$": "local-callback",
                "id": function_token,
            }
        raise TypeError("cannot serialize %r object" % type(obj))

    return _encode


def remote_callback_wrapper(x):
    def f(*args):
        result = requests.post(
            url=x["host"],
            data=msgpack_encode(args, is_for_remote=True),
            headers={"Content-Type": "application/octet-stream"},
        )
        return msgpack_decode(result.content)

    return f


def _decode_walk_tree(x):
    if isinstance(x, dict):
        if "$$type$$" in x:
            if x["$$type$$"] == "ndarray":
                array = numpy.frombuffer(
                    x["data"],
                    dtype={
                        "int8": numpy.int8,
                        "uint8": numpy.uint8,
                        "int16": numpy.int16,
                        "uint16": numpy.uint16,
                        "int32": numpy.int32,
                        "uint32": numpy.uint32,
                        "int64": numpy.int32,  # Intentional mismatch! See comment above.
                        "uint64": numpy.uint32,  # Intentional mismatch! See comment above.
                        "float32": numpy.float32,
                        "float64": numpy.float64,
                    }[x["dtype"]],
                ).reshape(x["shape"])
                if x["dtype"] == "int64":
                    array = array.astype(numpy.int64)
                if x["dtype"] == "uint64":
                    array = array.astype(numpy.uint64)
                return array
            elif x["$$type$$"] == "torch":
                array = _decode_walk_tree(x["array"])
                return torch.tensor(array)
                # return torch.tensor(array, device=x["device"])
            elif x["$$type$$"] == "remote-callback":
                return remote_callback_wrapper(x)
            else:
                raise ValueError("Bad serialized $$type$$: %r" % x["$$type$$"])
        return {k: _decode_walk_tree(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_decode_walk_tree(v) for v in x]
    return x


def msgpack_encode(obj: Any, is_for_remote=False) -> bytes:
    return msgpack.packb(obj, default=_msgpack_special_encoder(is_for_remote))


def msgpack_decode(raw_data: bytes) -> Any:
    return _decode_walk_tree(msgpack.unpackb(raw_data))


def stash_data(data, name=None):
    if name is None:
        name = "anonymous-" + get_unique_identifier()
    encoded_data = msgpack_encode(data, is_for_remote=True)
    data_key = f"/rrinterp-data-stash/{name}.bin"
    streamdb.rrserve.upload_to_rrserve(
        key=data_key,
        category="rrinterp-data-stash:" + name,
        data=encoded_data,
        content_type="application/octet-stream",
    )
    return name


def fetch_data(url):
    if not url.startswith("https://"):
        url = f"https://rrserve.s3.us-west-2.amazonaws.com//rrinterp-data-stash/{url}.bin"
    raw_data = requests.get(url).content
    return msgpack_decode(raw_data)


class Widget:
    def __init__(self, name: str, random_id: str, remote_url=None):
        self.name = name
        self.random_id = random_id
        self.remote_url = remote_url
        self.data: Dict[str, Any] = {}
        self.buf_length = 1

    def __repr__(self):
        return "<%s widget %s with %i bytes of data>" % (self.name, self.random_id, self.buf_length)

    def update(self, **kwargs):
        self.data.update(kwargs)
        buf = msgpack_encode(self.data)
        self.buf_length = len(buf)
        global_comm.send(
            {
                "kind": "render",
                "dest": self.random_id,
                "name": self.name,
                "remoteUrl": self.remote_url,
            },
            buffers=[buf],
        )

    def publish(self, name=None):
        if name is None:
            name = "anonymous-" + get_unique_identifier()
        key_base = "/rrinterp-published-widgets/" + name
        # For race reasons it's nice to upload the data first.
        encoded_data = msgpack_encode(self.data, is_for_remote=True)
        data_key = key_base + "-data.bin"
        streamdb.rrserve.upload_to_rrserve(
            key=data_key,
            category="rrinterp-published-widgets-data:" + name,
            data=encoded_data,
            content_type="application/octet-stream",
        )
        page = publish_code % {
            "rrserve_key": global_rrserve_key,
            "rrserve_id": global_rrserve_id,
            "rrserve_category": global_rrserve_category,
            "rrserve_data_key": data_key,
            "name": json.dumps(self.name),
            "remoteUrl": json.dumps(self.remote_url),
        }
        streamdb.rrserve.upload_to_rrserve(
            key=key_base + ".html",
            category="rrinterp-published-widgets-html:" + name,
            data=page,
            content_type="text/html",
        )
        k = key_base + ".html"
        return IPython.display.HTML(
            '<a href="https://rrserve.s3.us-west-2.amazonaws.com/%s">https://rrserve.s3.us-west-2.amazonaws.com/%s</a>'
            % (k, k)
        )


def render(component_name: str, **kwargs):
    widgets = get_widgets()
    remote_url = None
    if component_name.startswith("@"):
        # Attempt to load a remote widget.
        remote_url = streamdb.rrserve.rrserve_most_recent_url("rrinterp-magic-component:" + component_name)
        # print("Rendering from:", remote_url)
    elif component_name not in widgets:
        raise ValueError("Unknown widget %r, try one of: %s" % (component_name, ", ".join(widgets)))
    # widget_desc = widgets[component_name]
    random_id = "rrinterp-" + os.urandom(8).hex()
    IPython.display.display(
        IPython.display.HTML(
            """
        <div id="%s">Rendering %s...</div>
    """
            % (random_id, component_name)
        )
    )
    widget = Widget(component_name, random_id, remote_url=remote_url)
    # global_widget_registry.add(widget)
    widget.update(**kwargs)
    return widget


def setup_syntax_highlighting():
    from notebook.services.config.manager import ConfigManager

    ConfigManager().update(
        "notebook",
        {"CodeCell": {"highlight_modes": {"magic_text/javascript": {"reg": "^%%react_component"}}}},
    )


@IPython.core.magic.register_cell_magic
def react_component(line, cell):
    component_name = line.strip()
    assert component_name.startswith("@"), "All component names must start with @"

    for _ in range(200):
        r = requests.post(
            "https://a2n2.redwoodresearch.org/widgets/compile",
            auth=requests.auth.HTTPBasicAuth("redwood", "tree"),
            json={"code": cell},
        ).json()
        time.sleep(0.5)
        if r["done"]:
            break
    else:
        raise RuntimeError("Timed out trying to compile")
    if r["ret"] != 0:
        print(r["stdout"] + r["stderr"], file=sys.stderr)
        raise RuntimeError("Error compiling")
    compiled = r["bundled"]
    print("Built component successfully")
    key_base = "/rrinterp-magic-component-builds/component-%s-%s" % (component_name, get_unique_identifier())
    streamdb.rrserve.upload_to_rrserve(
        key=key_base + ".js",
        category="rrinterp-magic-component:" + component_name,
        data=compiled,
        content_type="text/javascript",
    )
    streamdb.rrserve.upload_to_rrserve(
        key=key_base + ".tsx",
        category="rrinterp-magic-component-source:" + component_name,
        data=cell,
        content_type="text/plain",
    )
    print("Uploaded and registered -- you may now use rrinterp.render(%r, ...)" % component_name)


@IPython.core.magic.register_line_cell_magic
def component_source(line, cell=None, return_as_string=False):
    component_name = line.strip()
    assert component_name.startswith("@"), "All component names must start with @"
    url = streamdb.rrserve.rrserve_most_recent_url("rrinterp-magic-component-source:" + component_name)
    source = requests.get(url).text
    if return_as_string:
        return source
    cell_text = "%%%%react_component %s\n" % component_name + source.rstrip()
    IPython.get_ipython().set_next_input(cell_text)
