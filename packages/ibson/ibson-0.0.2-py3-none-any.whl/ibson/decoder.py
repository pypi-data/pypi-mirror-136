# Copyright (C) 2022 Aaron Gibson (eulersidcrisis@yahoo.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""decoder.py.

Decoding utilities for BSON.

This defines the primary ``BSONDecoder`` class that handles decoding some
BSON document into a python dictionary. It supports some common features to
control exactly how some objects should be interpreted, as well as handling
for some custom types.

In order to support a wider variety of use-cases, this uses functional-style
programming in a few places for traversing the BSON document structure. This
can enable "scanning/searching" operations of large BSON documents without
requiring the caller to decode the entire document. This also manages the
parsing stack externally (i.e. does NOT use recursion), so that deeply nested
BSON documents can still be parsed without any recursion overflow issues (of
course, there are still possible memory issues for the external stack itself,
but this is substantially larger in most cases as the appropriate memory is
allocated on the heap).

In order to work effectively, the underlying stream that is passed into the
decoder should be seekable; this is usually an acceptable requirement for most
uses; large BSON documents, for example, will most likely be stored as a file,
which should be seekable for most OS's.
If for some reason the underlying stream is _not_ seekable (i.e. reading from
a socket), then the caller should then first load the contents into memory
(i.e. via ``io.BytesIO()`` or similar), which will then be seekable. This is
no worse than what would be required anyway.
"""
import io
import uuid
import datetime
from collections import deque

# Local imports.
import ibson.codec_util as util
import ibson.errors as errors


def _parse_64bit_float(stm):
    buff = stm.read(util.DOUBLE_STRUCT.size)
    return util.DOUBLE_STRUCT.unpack(buff)[0]


def _parse_int32(stm):
    buff = stm.read(util.INT32_STRUCT.size)
    return util.INT32_STRUCT.unpack(buff)[0]


def _parse_int64(stm):
    buff = stm.read(util.INT64_STRUCT.size)
    return util.INT64_STRUCT.unpack(buff)[0]


def _parse_uint64(stm):
    buff = stm.read(util.UINT64_STRUCT.size)
    return util.UINT64_STRUCT.unpack(buff)[0]


def _parse_byte(stm):
    buff = stm.read(util.BYTE_STRUCT.size)
    return util.BYTE_STRUCT.unpack(buff)[0]


def _scan_for_null_terminator(buff):
    for i, x in enumerate(buff):
        if x == 0:
            return i
    return -1


def _parse_ename(stm, decode=True):
    """Parse out a C-string (null-terminated string).

    If 'decode=True' (default), then convert the parsed string into UTF-8
    automatically.
    """
    data = bytearray()
    while True:
        # Peek the data, but do not (yet) consume it.
        raw_data = stm.read(1)
        if raw_data == b'\x00':
            break
        data.extend(raw_data)

    # 'index' stores the index of the null terminator, or -1 if it was not
    # found. Realistically, this should be positive to include at least one
    # character. The current contents that were parsed are stored into 'data',
    # which we can now encode as a string (if requested).
    if decode:
        try:
            return data.decode('utf-8')
        except Exception:
            pass
    return data


def _parse_utf8_string(stm):
    """Parse out a UTF-8 string from the stream."""
    buff = stm.read(util.INT32_STRUCT.size)
    length = util.INT32_STRUCT.unpack(buff)[0]
    # Read 'length' bytes.
    data = stm.read(length)
    # The last byte _should_ be the null-terminator.
    assert data[length - 1] == 0, "Last byte not the null-terminator!"

    # Decode this data as UTF-8.
    return data[:-1].decode('utf-8')


def _parse_bool(stm):
    buff = stm.read(util.BYTE_STRUCT.size)
    if buff[0] == 0x00:
        return False
    elif buff[0] == 0x01:
        return True
    # Should never happen.
    raise Exception("Invalid bool type parsed!")


def _parse_binary(stm):
    buff = stm.read(util.INT32_STRUCT.size)
    length = util.INT32_STRUCT.unpack(buff)[0]
    buff = stm.read(util.BYTE_STRUCT.size)
    subtype = util.BYTE_STRUCT.unpack(buff)[0]

    # Read exactly 'length' bytes after.
    data = stm.read(length)

    # Handle UUID implicitly.
    if subtype in [0x03, 0x04]:
        return uuid.UUID(bytes=data)
    return data


def _parse_null(stm):
    return None, 0


def _parse_utc_datetime(stm):
    buff = stm.read(util.INT64_STRUCT.size)
    utc_ms = util.INT64_STRUCT.unpack(buff)[0]
    result = datetime.datetime.fromtimestamp(
        utc_ms / 1000.0, tz=datetime.timezone.utc)
    return result


class DecodeEvents(object):
    """Placeholder class for events when decoding a BSON document."""

    NESTED_DOCUMENT = object()
    """Event that denotes the start of a nested document with the given key.

    NOTE: The end of this nested document is flagged by an 'END_DOCUMENT'
    event.
    """

    NESTED_ARRAY = object()
    """Event that denotes the start of a nested array with the given key.

    NOTE: The end of this nested document if flagged by an 'END_DOCUMENT'
    event.
    """

    END_DOCUMENT = object()
    """Event that denotes the end of a nested document or array."""

    SKIP_KEY = object()
    """Event that denotes to skip the current key."""


class DecoderFrame(object):

    def __init__(self, key, fpos, parent=None, length=None, is_array=False):
        self._key = key
        self._starting_fpos = fpos
        self._parent = parent
        self._length = length
        self._is_array = is_array
        self._data = list() if is_array else dict()

    def add_item(self, key, value):
        if self.is_array:
            self._data.append(value)
        else:
            self._data[key] = value

    @property
    def key(self):
        """Return the key this frame pertains to."""
        return self._key

    @property
    def starting_fpos(self):
        """Return the starting position in the file for this frame."""
        return self._starting_fpos

    @property
    def parent(self):
        """Return the parent for this frame."""
        return self._parent

    @property
    def length(self):
        """Return the (expected) length of this frame."""
        return self._length

    @property
    def is_array(self):
        """Return whether the current frame pertains to an array or dict."""
        return self._is_array

    @property
    def data(self):
        return self._data


BSON_MIN_OBJECT = object()
"""Default object that is assumed when decoding the 'min key' BSON field."""


BSON_MAX_OBJECT = object()
"""Default object that is assumed when decoding the 'max key' BSON field."""


class BSONScanner(object):

    def __init__(self, min_key_object=BSON_MIN_OBJECT,
                 max_key_object=BSON_MAX_OBJECT, null_object=None):
        # By default, initialize the opcode mapping here. Subclasses should
        # register this mapping using the helper call to:
        # - register_opcode(opcode, callback)
        #
        # By default, most of the common types are already implemented, and
        # this class's constructor arguments handle some common cases.
        self._opcode_mapping = {
            0x01: _parse_64bit_float,
            0x02: _parse_utf8_string,
            # 0x03: _parse_document,
            # 0x04: _parse_array,
            0x05: _parse_binary,
            0x06: lambda args: None,
            # 0x07: _parse_object_id,
            0x08: _parse_bool,
            0x09: _parse_utc_datetime,
            # 0x0A implies 'NULL', so return the configured NULL object.
            0x0A: lambda args: null_object,
            # 0x0B: _parse_regex,
            # 0x0C: _parse_db_pointer,
            # 0x0D: _parse_js_code,
            # 0x0E: _parse_symbol,
            # 0x0F: _parse_js_code_with_scope,
            0x10: _parse_int32,
            # 0x11: parse_datetime,
            0x12: _parse_int64,
            # 0x13: _parse_decimal128,
            # Return the min/max objects for these opcodes.
            0x7F: lambda args: max_key_object,
            0xFF: lambda args: min_key_object,
        }

    def register_opcode(self, opcode, callback):
        """Register a custom callback to parse this opcode.

        NOTE: 'callback' is expected to have the signature:
            callback(stm, skip=False) -> result
        """
        # Let's ban using '0x00' as an opcode for now because this is used
        # in various places to denote the 'null-terminator' character.
        if opcode == 0x00:
            raise errors.InvalidBSONOpcode(opcode)
        self._opcode_mapping[opcode] = callback

    def register_binary_subtype(self, subtype, callback):
        """Register a custom callback to parse a custom binary type.
        """
        pass

    def scan_binary(self, stm):
        return _parse_binary(stm)

    def iterdecode(self, stm):
        """Iterate over the given BSON stream and (incrementally) decode it.

        This returns a generator that yields tuples of the form:
            (key, value, frame)
        where:
         - key: The key pertaining to this frame.
         - value: The parsed value
         - frame: The current frame as a DecoderFrame.

        One reason to invoke this call is to avoid loading the entire BSON
        document into memory when parsing it; traversing the document only
        stores the state needed to continue the traversal, which makes this
        more memory-efficient.

        It is possible to request to "skip" decoding a frame by sending the
        special DecodeEvents.SKIP_KEYS object back to this generator. In this
        case, it is NOT strictly guaranteed that the frame will be skipped!
        Rather, it is a hint to the generator that it can skip the next key if
        desired. This feature is useful to skip decoding nested documents when
        searching for a specific key (for example) and can hint to the system
        when it is okay to skip reading.
        """
        # The stream should be seekable. If it isn't, then it should be wrapped
        # appropriately using 'io' module utilities.
        #
        # Get the current position in the stream.
        fpos = stm.tell()

        # The first field in any BSON document is its length. Fetch that now.
        length = _parse_int32(stm)
        # The root key is the empty key.
        frame = DecoderFrame('', fpos, is_array=False, length=length)

        # Initialize the stack with the root document.
        current_stack = deque()
        current_stack.append(frame)

        # Start with the first 'yield' for the entire document.
        client_req = yield frame.key, DecodeEvents.NESTED_DOCUMENT, frame

        while current_stack:
            # Peek the current stack frame, which is at the end of the stack.
            frame = current_stack[-1]

            # A 'frame' consists of:
            #   <opcode> + <null-terminated key> + <value>
            opcode = _parse_byte(stm)

            # An 'opcode' of 0x00 implies the end of the current document or
            # array (meaning there is no null-terminated key), so handle that
            # case first.
            if opcode == 0x00:
                frame = current_stack.pop()
                client_req = (yield (
                    frame.key, DecodeEvents.END_DOCUMENT, frame))
                continue

            # Parse the key for the next element.
            key = _parse_ename(stm)

            # Check the 'nested document' case first.
            client_req = None
            if opcode in [0x03, 0x04]:
                nested_fpos = stm.tell()
                # A nested array. Create a new DocumentFrame type and push it
                # to the current stack.
                length = _parse_int32(stm)
                is_array = bool(opcode == 0x04)
                if is_array:
                    result = DecodeEvents.NESTED_ARRAY
                else:
                    result = DecodeEvents.NESTED_DOCUMENT

                # These given two opcodes imply nested documents. If the caller
                # responded with a request of "SKIP_KEY", then skip the key and
                # do not bother parsing any of those frames; instead, seek past
                # the perceived length of the document.
                client_req = (yield (key, result, frame))
                if client_req is DecodeEvents.SKIP_KEY:
                    # Seek ahead based on the parsed length.
                    stm.seek(length, 1)
                else:
                    # Create a new frame, with current_frame as the parent.
                    new_frame = DecoderFrame(
                        key, nested_fpos, is_array=is_array, parent=frame,
                        length=length)
                    current_stack.append(new_frame)
                continue

            # Depending on opcode, make the appropriate callback otherwise.
            result = self.process_opcode(opcode, stm, current_stack)

            # Confusing. Basically, the client can 'signal' a few operations to
            # this generator by calling the '.send()' method. If no '.send()'
            # is called and the caller just iterates over the given contents,
            # then 'client_req' will be 'None'.
            # If 'client_req' is something other than None, try and process a
            # few cases.
            client_req = (yield (key, result, frame))

    def process_opcode(self, opcode, stm, traversal_stk):
        """Process the given opcode and return the appropriate value.

        The result of this operation depends on the opcode, but this should
        return the parsed object OR a special 'DecodeEvent' subclass flagging
        a nested subdocument or array as appropriate.
        """
        callback = self._opcode_mapping.get(opcode)
        if not callback:
            raise Exception("Invalid opcode: {}".format(opcode))
        return callback(stm)


class BSONDecoder(BSONScanner):
    """Basic BSONDecoder object that decodes a BSON byte stream.

    This decoder is designed to decode the stream into a python 'dict'. Some
    of the common BSON types are decoded as expected, such as:
     - UUIDs
     - datetime
     - strings (as UTF-8)

    More customized objects can be handled as well by registering the proper
    handlers via: 'register_opcode()'
    which should parse out custom opcode types.
    """

    def loads(self, data):
        """Load the BSON document from the given bytes-like object."""
        with io.BytesIO(data) as stm:
            return self.load(stm)

    def load(self, stm):
        """Load the BSON document from the given (bytes-like) stream.

        NOTE: The underlying stream should be seekable if possible.
        """
        generator = self.iterdecode(stm)

        for key, val, frame in generator:
            if val is DecodeEvents.NESTED_DOCUMENT:
                frame.ext_data = dict()
                continue
            elif val is DecodeEvents.NESTED_ARRAY:
                frame.ext_data = []
                continue
            elif val is DecodeEvents.END_DOCUMENT:
                if frame.parent:
                    frame.parent.add_item(frame.key, frame.data)
                continue

            # Otherwise, add the given data to the current frame.
            frame.add_item(key, val)

        # This should not happen, but might if there is some problem with an
        # unwound frame stack.
        if not frame:
            raise errors.BSONDecodeError('Invalid end state!')
        return frame.data
