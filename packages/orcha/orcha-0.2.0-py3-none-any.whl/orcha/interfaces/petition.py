#                                   MIT License
#
#              Copyright (c) 2021 Javier Alonso <jalonso@teldat.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#            furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
#                 copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#                                    SOFTWARE.
"""
:class:`Petition` defines the behavior of the module that calls the service.
This type must be recoverable from a :class:`Message` object, as petitions
cannot be sent from clients to servers and vice versa.
"""
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import total_ordering
from queue import Queue
from signal import SIGINT
from typing import Any, Callable, NoReturn, Optional, Type, TypeVar, Union

from orcha.utils.cmd import kill_proc_tree

ProcT = Union[subprocess.Popen, int]
"""
Custom type which accepts both an open process and an integer, representing
the process PID.

:see: :py:class:`subprocess.Popen`
"""

ActionCallbackT = Callable[[ProcT], NoReturn]
"""
Function with the form ``(ProcT) -> None`` that is called when the petition
should run. It refers directly the action that represents this petition.
"""

P = TypeVar("P", bound="Petition")
"""
Type var that represents a :class:`Petition` instance or any subclass that
inherits from it.
"""


@total_ordering
@dataclass
class Petition(ABC):
    """Class that represents a petition that should be executed on the server.
    This class must have the ability to being created from an existing
    :class:`Message`, as this is the only item that can be exchanged during
    inner process communication.

    It is composed by multiple attributes:

     + :attr:`priority` defines the priority of the petition.
     + :attr:`id` is a unique identifier for the petition.
     + :attr:`queue` is a :py:class:`Queue <multiprocessing.Queue>` that can
       be sent across processes.
     + :attr:`action` represents the callable that will be executed.
     + :attr:`condition` is a predicate which defines whether the petition
       can be run or not.

    This class is intended to be a stub so your implementation must inherit
    from this one.

    .. versionchanged:: 0.1.9
        We define our own equality and comparison operators, there is no need
        in subclasses declaring fields as ``compare=False``. It is only checked
        the ID (for equality/inequality tests) and the priority (for comparison
        tests).

    .. versionchanged:: 0.2.0
        This class now defines a :func:`terminate` which is abstract and should
        be overriden by all subclasses that inherit from :class:`Petition`. Such
        function allows defining a custom behavior when a finish message is
        received.

        Warning:
            This is a breaking change - all existing projects should migrate
            their own :class:`Petition` subclasses to the new definition.

    :see: :py:func:`field <dataclasses.field>`
    """

    priority: int = field(init=False)
    """
    Priority of the petition. It is an integer whose value is used for comparing
    across other petitions. The lower the value is, the higher the priority gets.
    Items with the same priority may keep input order, but it is not guaranteed.
    """

    id: Union[int, str] = field(compare=False)
    """
    Unique identifier for this petition. This value must directly be extracted from
    :attr:`Message.id`.

    .. versionchanged:: 0.1.6
       Accept :obj:`str` as unique ID identifier also.
    """

    queue: Queue = field(compare=False, repr=False)
    """
    :class:`Queue <multiprocessing.Queue>` used for process communication. Actually,
    this queue is used as a one-sided pipe in which the server puts the messages of
    the :attr:`action` and finishes with a known exit code (i.e.: :obj:`None`, ``int``, ...).

    Warning:
        This queue **must** be a
        `proxy object <https://docs.python.org/3/library/multiprocessing.html#proxy-objects>`_
        which addresses a memory location on a
        :py:class:`Manager <multiprocessing.managers.BaseManager>`. You can decide
        to use your own queue given by :py:mod:`multiprocessing` but it probably won't work.
        It is better to use the exposed manager for obtaining a queue once the client is
        initialized: :attr:`Manager.manager <orcha.lib.manager.Manager.manager>`.
    """

    action: Callable[[ActionCallbackT, Type[P]], NoReturn] = field(compare=False, repr=False)
    """
    The action to be called when the petition is pop from the queue. It is a function with the
    form::

        def action(cb: (Union[subprocess.Popen, int]) -> None, p: Petition) -> None

    Notice that the action will
    be built on "server side", meaning that this attribute will default to :obj:`None` at the
    beginning (functions cannot be shared across processes).

    As a :class:`Petition` is built from :class:`Message`, use the :attr:`Message.extras` for
    defining how the petition will behave when :attr:`action` is called.
    """

    condition: Callable[[Type[P]], bool] = field(compare=False, repr=False)
    """
    Predicate that decides whether the request should be processed or not. It is a function
    with the form::

        def predicate(p: Petition) -> bool

    If your petitions do not require any particular condition, you can always define an
    empty predicate which always returns :obj:`True`::

        petition = Petition(..., condition=lambda _: True)

    """

    def communicate(self, message: Any, blocking: bool = True):
        """
        Communicates with the source process by sending a message through the internal queue.

        Args:
            message (any): a valid item that can be put on a :class:`queue.Queue`.
            blocking (bool): whether to block or not while putting the item on the queue.

        Raises:
            queue.Full: if the queue has exceeded its maximum capacity and ``blocking`` is set
                        to :obj:`True`.
        """
        try:
            self.queue.put(message, block=blocking)
        except ValueError:
            pass

    def communicate_nw(self, message: Any):
        """
        Communicates with the source process by sending a message through the internal queue
        without waiting.

        Args:
            message (any): a valid item that can be put on a :class:`queue.Queue`.

        Raises:
            queue.Full: if the queue has exceeded its maximum capacity.
        """
        try:
            self.queue.put_nowait(message)
        except ValueError:
            pass

    def finish(self, ret: Optional[int] = None):
        """
        Notifies to the listening process that the corresponding action has finished.

        Args:
            ret (int | None): return code of the operation, if any.
        """
        try:
            self.queue.put(ret)
        except ValueError:
            pass

    @abstractmethod
    def terminate(self, pid: Optional[int]) -> bool:
        """
        Function that is called every time a finish request is received
        for killing the process itself. One can use either the received PID, if any,
        or a saved argument at the running class instance.

        Args:
            pid (:obj:`int` | :obj:`None`): process identifier, useful when trying to
                signaling a process.

        Returns:
            :obj:`bool`: that indicates if the operation has been successful or not.

        .. versionadded:: 0.2.0
        """
        ...

    def __eq__(self, __o: object) -> bool:
        # ensure we are comparing against our class or a subclass of ours
        if not isinstance(__o, Petition):
            raise NotImplementedError()

        sid = self.id
        oid = __o.id

        # if IDs are not strings, convert them so we can truly compare
        if not isinstance(sid, str):
            sid = str(sid)

        if not isinstance(oid, str):
            oid = str(oid)

        return sid == oid

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, Petition):
            raise NotImplementedError()

        # we check equality for the priorities
        return self.priority < __o.priority


@dataclass(init=False)
class EmptyPetition(Petition):
    """
    Empty petition which will run always the latest (as its priority is ``inf``).
    This petition is used in :class:`Manager` for indicating that there won't be
    any new petitions after this one, so the :class:`Processor` can shut down.

    Note:
        This class accepts no parameters, and you can use it whenever you want for
        debugging purposes. Notice that it is immutable, which means that no attribute
        can be altered, added or removed once it has been initialized.
    """

    priority = float("inf")
    id = -1
    queue = None
    action = None
    condition = None

    def __init__(self):
        pass

    def terminate(self, _: Optional[int]) -> bool:
        pass


@dataclass(init=False)
class WatchdogPetition(Petition):
    """
    Watchdog petition has always the greatest priority so it should be run the first
    whenever it is received. It is used for indicating whether the processor should
    watchdog the SystemD main process so we inform we are still running.

    Warning:
        The priority of this petition is always the higher (using ``float("-inf")``),
        be careful whenever you place a custom petition with higher priority: do not
        use ``float("-inf")`` as an expression, try keeping your priorities above ``0``
        an go as high as you want.
    """

    priority = float("-inf")
    id = -1
    queue = None
    action = None
    condition = None

    def __init__(self):
        pass

    def terminate(self, _: Optional[int]) -> bool:
        pass


@dataclass
class SignalingPetition(Petition):
    """
    :class:`Petition` that finishes the running process by sending a signal (which used
    to be the default).

    It behaves exactly the same as its parent class, the only difference is that a
    signal is issued when a finish message is received.

    One can define which :attr:`signal` to send and whether to also :attr:`kill_parent`
    by issuing the signal to it.

    .. versionadded:: 0.2.0
    """

    signal: int = field(compare=False, default=SIGINT)
    """
    The signal number to send to the process when finishing. Notice that the value here
    should be valid within the host architecture the orchestrator is running on.
    """

    kill_parent: bool = field(compare=False, default=False)
    """
    Whether to send the specific signal to the parent also.
    """

    def terminate(self, pid: Optional[int]) -> bool:
        if pid is None:
            raise ValueError(f'Petition of type "{type(self).__name__}" requires a valid PID')

        return kill_proc_tree(pid, self.kill_parent, self.signal)


__all__ = [
    "ActionCallbackT",
    "EmptyPetition",
    "P",
    "Petition",
    "ProcT",
    "WatchdogPetition",
    "SignalingPetition",
]
