# coding: utf-8

import re
import six



from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class AvailabilityZone:

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'code': 'str',
        'state': 'str',
        'protocol': 'list[str]'
    }

    attribute_map = {
        'code': 'code',
        'state': 'state',
        'protocol': 'protocol'
    }

    def __init__(self, code=None, state=None, protocol=None):
        """AvailabilityZone

        The model defined in huaweicloud sdk

        :param code: 可用区唯一编码。
        :type code: str
        :param state: 可用区状态。  取值：ACTIVE。
        :type state: str
        :param protocol: 未售罄的LB规格类别。取值： - L4：表示网络型LB未售罄。 - L7：表示应用型LB未售罄。
        :type protocol: list[str]
        """
        
        

        self._code = None
        self._state = None
        self._protocol = None
        self.discriminator = None

        self.code = code
        self.state = state
        if protocol is not None:
            self.protocol = protocol

    @property
    def code(self):
        """Gets the code of this AvailabilityZone.

        可用区唯一编码。

        :return: The code of this AvailabilityZone.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this AvailabilityZone.

        可用区唯一编码。

        :param code: The code of this AvailabilityZone.
        :type code: str
        """
        self._code = code

    @property
    def state(self):
        """Gets the state of this AvailabilityZone.

        可用区状态。  取值：ACTIVE。

        :return: The state of this AvailabilityZone.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this AvailabilityZone.

        可用区状态。  取值：ACTIVE。

        :param state: The state of this AvailabilityZone.
        :type state: str
        """
        self._state = state

    @property
    def protocol(self):
        """Gets the protocol of this AvailabilityZone.

        未售罄的LB规格类别。取值： - L4：表示网络型LB未售罄。 - L7：表示应用型LB未售罄。

        :return: The protocol of this AvailabilityZone.
        :rtype: list[str]
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """Sets the protocol of this AvailabilityZone.

        未售罄的LB规格类别。取值： - L4：表示网络型LB未售罄。 - L7：表示应用型LB未售罄。

        :param protocol: The protocol of this AvailabilityZone.
        :type protocol: list[str]
        """
        self._protocol = protocol

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                if attr in self.sensitive_list:
                    result[attr] = "****"
                else:
                    result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        import simplejson as json
        if six.PY2:
            import sys
            reload(sys)
            sys.setdefaultencoding("utf-8")
        return json.dumps(sanitize_for_serialization(self), ensure_ascii=False)

    def __repr__(self):
        """For `print`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AvailabilityZone):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
