# coding: utf-8

import re
import six



from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class UploadProtocolMappingsRequest:

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'product_id': 'str',
        'body': 'UploadProtocolMappingsRequestBody'
    }

    attribute_map = {
        'product_id': 'product_id',
        'body': 'body'
    }

    def __init__(self, product_id=None, body=None):
        """UploadProtocolMappingsRequest

        The model defined in huaweicloud sdk

        :param product_id: 设备关联的产品ID，用于唯一标识一个产品模型，在管理门户导入产品模型后由平台分配获得。
        :type product_id: str
        :param body: Body of the UploadProtocolMappingsRequest
        :type body: :class:`huaweicloudsdkiotedge.v2.UploadProtocolMappingsRequestBody`
        """
        
        

        self._product_id = None
        self._body = None
        self.discriminator = None

        self.product_id = product_id
        if body is not None:
            self.body = body

    @property
    def product_id(self):
        """Gets the product_id of this UploadProtocolMappingsRequest.

        设备关联的产品ID，用于唯一标识一个产品模型，在管理门户导入产品模型后由平台分配获得。

        :return: The product_id of this UploadProtocolMappingsRequest.
        :rtype: str
        """
        return self._product_id

    @product_id.setter
    def product_id(self, product_id):
        """Sets the product_id of this UploadProtocolMappingsRequest.

        设备关联的产品ID，用于唯一标识一个产品模型，在管理门户导入产品模型后由平台分配获得。

        :param product_id: The product_id of this UploadProtocolMappingsRequest.
        :type product_id: str
        """
        self._product_id = product_id

    @property
    def body(self):
        """Gets the body of this UploadProtocolMappingsRequest.


        :return: The body of this UploadProtocolMappingsRequest.
        :rtype: :class:`huaweicloudsdkiotedge.v2.UploadProtocolMappingsRequestBody`
        """
        return self._body

    @body.setter
    def body(self, body):
        """Sets the body of this UploadProtocolMappingsRequest.


        :param body: The body of this UploadProtocolMappingsRequest.
        :type body: :class:`huaweicloudsdkiotedge.v2.UploadProtocolMappingsRequestBody`
        """
        self._body = body

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
        if not isinstance(other, UploadProtocolMappingsRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
