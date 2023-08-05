# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import operator

import numpy

__all__ = [
    'itemsgetter', 'NumpyEncoder',
]

logger = logging.getLogger(__name__)


def itemsgetter(*items):
    """Variant of :func:`operator.itemgetter` that returns a callable that
    always returns a tuple, even when called with one argument. This is to make
    the result type consistent, regardless of input.
    """

    if len(items) == 1:
        item = items[0]
        def f(obj):
            return (obj[item], )

    else:
        f = operator.itemgetter(*items)

    return f


# copied from dwave-hybrid utils
# (https://github.com/dwavesystems/dwave-hybrid/blob/b9025b5bb3d88dce98ec70e28cfdb25400a10e4a/hybrid/utils.py#L43-L61)
# TODO: switch to `dwave.common` if and when we create it
class NumpyEncoder(json.JSONEncoder):
    """JSON encoder for numpy types.

    Supported types:
     - basic numeric types: booleans, integers, floats
     - arrays: ndarray, recarray
    """

    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.bool_):
            return bool(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()

        return super().default(obj)
