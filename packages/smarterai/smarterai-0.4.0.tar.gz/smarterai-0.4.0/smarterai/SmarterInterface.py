import inspect
from .smarterStore import SmarterStore
from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, Any


class SmarterMessage(dict):
    pass


class SmarterSender:
    def __init__(self, store_dir: str, delegate: Callable[[SmarterMessage, str], Optional[SmarterMessage]]):
        self.smarter_store = SmarterStore(store_dir=store_dir)
        self.delegate = delegate

    def send_message(self, message: SmarterMessage, port: str) -> Optional[SmarterMessage]:
        """
        Takes in a message from a python code component and sends it to its output port.
        :param message: A SmarterMessage to be sent through an output port
        :param port: The output port to be
        :return:
        """
        return self.delegate(message, port)

    def set_data(self, pattern: str, data: Any) -> None:
        """
        Takes in JSON serializable data and sets it to a specific front-end GUI component.
        :param pattern: The front-end GUI pattern to set the data to
        :param data: The data to be sent to the GUI. It needs to match the format the pattern expects the data in.
                        Example a chart expects a table-like format, while a textField expects some text.
        :return: None
        """
        self.smarter_store.set_pattern_data(pattern=pattern, data=data)
        message = SmarterMessage({"action": "setData",
                                  "args": {"pattern": pattern, "data": data}})
        self.send_message(message=message, port='#gui')

    def clear_data(self, pattern: str) -> None:
        """
        Clears any data associated with a specific pattern in the GUI components
        :param pattern: The front-end GUI pattern to set the data to
        :return: None
        """
        self.smarter_store.set_pattern_data(pattern=pattern, data=None)
        message = SmarterMessage({"action": "setData",
                                  "args": {"pattern": pattern, "data": None}})
        self.send_message(message=message, port='#gui')

    def append_data(self, pattern: str, data: Any, limit: int) -> None:
        """
        Appends new data to previously sent data to a specific pattern.
        :param pattern: The front-end GUI pattern to append the data to.
        :param data: The data to be appended to a GUI component's previous data.
        :param limit: If the data's total size is bigger than limit, then a sliding window will be implemented to hold
            the latest added elements
        :return: None
        """
        self.smarter_store.append_pattern_data(pattern=pattern, data=data)
        message = SmarterMessage({"action": "setData",
                                  "args": {"pattern": pattern, "data": data},
                                  "options": {"append": True, "limitLength": limit}})
        self.send_message(message=message, port='#gui')

    def prepend_data(self, pattern: str, data: Any, limit: int) -> None:
        """
        Prepends new data to previously sent data to a specific pattern.
        :param pattern: The front-end GUI pattern to append the data to.
        :param data: The data to be prepended to a GUI component's previous data.
        :param limit: If the data's total size is bigger than limit, then a sliding window will be implemented to hold
            the latest added elements
        :return: None
        """
        self.smarter_store.prepend_pattern_data(pattern=pattern, data=data)
        message = SmarterMessage({"action": "setData",
                                  "args": {"pattern": pattern, "data": data},
                                  "options": {"prepend": True, "limitLength": limit}})
        self.send_message(message=message, port='#gui')

    def get_data(self, pattern) -> SmarterMessage:
        return self.smarter_store.get_pattern_data(pattern)

    def reply_back(self, message: SmarterMessage) -> None:
        """
        Takes in a message to reply back to front-end REST/Websocket topics. An equivalent  to 'return' with a message.
        Uses built-in port #action to identify the front-end topic
        :param message: A SmarterMessage JSON Serializable
        :return: None
        """

        self.send_message(message=message, port='#action')


class _Smarter_SignatureCheckerMeta(ABCMeta):
    def __init__(cls, name, bases, attrs):
        errors = []
        for base_class in bases:
            for func_name in getattr(base_class, "__abstractmethods__", ()):
                smarter_signature = inspect.getfullargspec(
                    getattr(base_class, func_name)
                )
                flex_signature = inspect.getfullargspec(
                    getattr(cls, func_name)
                )
                if smarter_signature != flex_signature:
                    errors.append(
                        f"Abstract method {func_name} "
                        f"not implemented with correct signature in {cls.__name__}. Expected {smarter_signature}."
                    )
        if errors:
            raise TypeError("\n".join(errors))
        super().__init__(name, bases, attrs)


class SmarterPlugin(metaclass=_Smarter_SignatureCheckerMeta):
    """
    SmarterPlugin is designed for easy communication between the smarter.ai's platform and other Flex.
    In order to have the Flex's code accessible to the platform, this class needs to be inherited from
    a class explicitly named SmarterComponent.
    Example:
        Class SmarterComponent(SmarterPlugin):
            pass
    """

    @abstractmethod
    def invoke(
            self, port: str, message: SmarterMessage, sender: SmarterSender
    ) -> Optional[SmarterMessage]:
        """
        This is the flex's messages entry point. Any message sent to the current flex will be routed to this method.
        This method needs to be overwritten.

        Example:
            Class SmarterComponent(SmarterPlugin):
                def invoke(self, port: str,
                           msg: SmarterMessage,
                           send_message: SmarterSender) -> Optional[SmarterMessage]:
                    pass
        The message received and its associated port will be passed as inputs for this method,
        Along with a callable function that can be used to send messages to other flex.

        Arguments:
            port [str]: The input port name used to receive the message.
            msg [SmarterMessage]: The message passed to the flex.
            send_message[SmarterSender]: A Callable function used to send messages to other flex.
                                        The function has the signature:
                                            Callable[[SmarterMessage, str], SmarterMessage]
                                        Example:
                                            send_message(SmarterMessage(), 'out_port_name')

                                        Arguments:
                                            [SmarterMessage]: The new message to send out.
                                            [str]: The output port name used to send the new message.

                                        Returns:
                                            [SmarterMessage]: A return message.

        Returns:
            Optional[SmarterMessage]: If a message is being returned it should be of
                                      type SmarterMessage or None
        """
        raise NotImplementedError
