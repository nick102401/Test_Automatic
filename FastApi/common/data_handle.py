# multipart/form-data
class MultipartFormData(object):
    """multipart/form-data格式转化"""

    @staticmethod
    def format(reqData, boundary="----WebKitFormBoundary7MA4YWxkTrZu0gW", headers={}):
        """
        form data
        :param: data:  {"req":{"cno":"18990876","flag":"Y"},"ts":1,"sig":1,"v": 2.0}
        :param: boundary: "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        :param: headers: 包含boundary的头信息；如果boundary与headers同时存在以headers为准
        :return: str
        :rtype: str
        """
        # 从headers中提取boundary信息
        for headersKey in headers.keys():
            if headersKey.lower() == "content-type":
                fd_val = str(headers[headersKey])
                if "boundary" in fd_val:
                    fd_val = fd_val.split(";")[1].strip()
                    boundary = fd_val.split("=")[1].strip()
                else:
                    raise Exception("multipart/form-data头信息错误，请检查content-type key是否包含boundary")
        # form-data格式定式
        join_str = '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'
        end_str = "--{}--".format(boundary)
        args_str = ""

        if not isinstance(reqData, dict):
            raise Exception("multipart/form-data参数错误，data参数应为dict类型")
        for key, value in reqData.items():
            args_str = args_str + join_str.format(boundary, key, value)

        args_str = args_str + end_str.format(boundary)
        args_str = args_str.replace("\'", "\"")
        return args_str


if __name__ == '__main__':
    mfd = MultipartFormData()
    data = {
        'applyStatus': '0',
        'applyType': '4',
        'applyUserDescription': '{"valid": true,'
                                '"projectName": "P3",'
                                '"tempId": "ST-72f987fe9f8646618c9ca66fc63c3135",'
                                '"description": "",'
                                '"endTime":"2021-08-02",'
                                '"startTime": "2021-08-02"}'
    }
    resp = mfd.format(reqData={},
                      headers={'Accept': 'application/json, text/plain, */*',
                               'Accept-Language': 'zh-CN,zh;q=0.9',
                               'Connection': 'keep-alive',
                               'Content-Type': 'multipart/form-data; boundary=------WebKitFormBoundary7MA4YWxkTrZu0gF'})
    print(resp)
