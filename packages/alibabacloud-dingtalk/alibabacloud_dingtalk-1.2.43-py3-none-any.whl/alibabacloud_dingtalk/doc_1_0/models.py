# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import Dict, List


class BatchGetWorkspaceDocsHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchGetWorkspaceDocsRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        node_ids: List[str] = None,
        ding_isv_org_id: int = None,
        ding_org_id: int = None,
        ding_access_token_type: str = None,
        ding_uid: int = None,
    ):
        # 操作用户unionId
        self.operator_id = operator_id
        # 查询节点Id
        self.node_ids = node_ids
        self.ding_isv_org_id = ding_isv_org_id
        self.ding_org_id = ding_org_id
        self.ding_access_token_type = ding_access_token_type
        self.ding_uid = ding_uid

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.node_ids is not None:
            result['nodeIds'] = self.node_ids
        if self.ding_isv_org_id is not None:
            result['dingIsvOrgId'] = self.ding_isv_org_id
        if self.ding_org_id is not None:
            result['dingOrgId'] = self.ding_org_id
        if self.ding_access_token_type is not None:
            result['dingAccessTokenType'] = self.ding_access_token_type
        if self.ding_uid is not None:
            result['dingUid'] = self.ding_uid
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('nodeIds') is not None:
            self.node_ids = m.get('nodeIds')
        if m.get('dingIsvOrgId') is not None:
            self.ding_isv_org_id = m.get('dingIsvOrgId')
        if m.get('dingOrgId') is not None:
            self.ding_org_id = m.get('dingOrgId')
        if m.get('dingAccessTokenType') is not None:
            self.ding_access_token_type = m.get('dingAccessTokenType')
        if m.get('dingUid') is not None:
            self.ding_uid = m.get('dingUid')
        return self


class BatchGetWorkspaceDocsResponseBodyResultNodeBO(TeaModel):
    def __init__(
        self,
        name: str = None,
        node_id: str = None,
        url: str = None,
        last_edit_time: int = None,
        deleted: bool = None,
        doc_type: str = None,
    ):
        self.name = name
        self.node_id = node_id
        self.url = url
        # 最后编辑时间
        self.last_edit_time = last_edit_time
        self.deleted = deleted
        # 节点类型
        self.doc_type = doc_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        if self.deleted is not None:
            result['deleted'] = self.deleted
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        if m.get('deleted') is not None:
            self.deleted = m.get('deleted')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        return self


class BatchGetWorkspaceDocsResponseBodyResultWorkspaceBO(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        name: str = None,
    ):
        self.workspace_id = workspace_id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class BatchGetWorkspaceDocsResponseBodyResult(TeaModel):
    def __init__(
        self,
        node_bo: BatchGetWorkspaceDocsResponseBodyResultNodeBO = None,
        workspace_bo: BatchGetWorkspaceDocsResponseBodyResultWorkspaceBO = None,
        has_permission: bool = None,
    ):
        self.node_bo = node_bo
        self.workspace_bo = workspace_bo
        self.has_permission = has_permission

    def validate(self):
        if self.node_bo:
            self.node_bo.validate()
        if self.workspace_bo:
            self.workspace_bo.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_bo is not None:
            result['nodeBO'] = self.node_bo.to_map()
        if self.workspace_bo is not None:
            result['workspaceBO'] = self.workspace_bo.to_map()
        if self.has_permission is not None:
            result['hasPermission'] = self.has_permission
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeBO') is not None:
            temp_model = BatchGetWorkspaceDocsResponseBodyResultNodeBO()
            self.node_bo = temp_model.from_map(m['nodeBO'])
        if m.get('workspaceBO') is not None:
            temp_model = BatchGetWorkspaceDocsResponseBodyResultWorkspaceBO()
            self.workspace_bo = temp_model.from_map(m['workspaceBO'])
        if m.get('hasPermission') is not None:
            self.has_permission = m.get('hasPermission')
        return self


class BatchGetWorkspaceDocsResponseBody(TeaModel):
    def __init__(
        self,
        result: List[BatchGetWorkspaceDocsResponseBodyResult] = None,
    ):
        self.result = result

    def validate(self):
        if self.result:
            for k in self.result:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['result'] = []
        if self.result is not None:
            for k in self.result:
                result['result'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.result = []
        if m.get('result') is not None:
            for k in m.get('result'):
                temp_model = BatchGetWorkspaceDocsResponseBodyResult()
                self.result.append(temp_model.from_map(k))
        return self


class BatchGetWorkspaceDocsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchGetWorkspaceDocsResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchGetWorkspaceDocsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteSheetHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class DeleteSheetRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        return self


class DeleteSheetResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class UpdateWorkspaceDocMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class UpdateWorkspaceDocMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
        role_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type
        # 用户权限
        self.role_type = role_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        if self.role_type is not None:
            result['roleType'] = self.role_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        if m.get('roleType') is not None:
            self.role_type = m.get('roleType')
        return self


class UpdateWorkspaceDocMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[UpdateWorkspaceDocMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = UpdateWorkspaceDocMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class UpdateWorkspaceDocMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class CreateWorkspaceDocHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class CreateWorkspaceDocRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
        doc_type: str = None,
        operator_id: str = None,
        parent_node_id: str = None,
    ):
        # 文档名
        self.name = name
        # 文档类型
        self.doc_type = doc_type
        # 操作人unionId
        self.operator_id = operator_id
        # 父节点nodeId
        self.parent_node_id = parent_node_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.parent_node_id is not None:
            result['parentNodeId'] = self.parent_node_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('parentNodeId') is not None:
            self.parent_node_id = m.get('parentNodeId')
        return self


class CreateWorkspaceDocResponseBody(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        node_id: str = None,
        doc_key: str = None,
        url: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 文档Id
        self.node_id = node_id
        # 文档docKey
        self.doc_key = doc_key
        # 文档打开url
        self.url = url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.doc_key is not None:
            result['docKey'] = self.doc_key
        if self.url is not None:
            result['url'] = self.url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('docKey') is not None:
            self.doc_key = m.get('docKey')
        if m.get('url') is not None:
            self.url = m.get('url')
        return self


class CreateWorkspaceDocResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: CreateWorkspaceDocResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = CreateWorkspaceDocResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetRangeHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetRangeRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        return self


class GetRangeResponseBody(TeaModel):
    def __init__(
        self,
        values: List[str] = None,
    ):
        # 值
        self.values = values

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.values is not None:
            result['values'] = self.values
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('values') is not None:
            self.values = m.get('values')
        return self


class GetRangeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetRangeResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetRangeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateSheetHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class CreateSheetRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        name: str = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id
        # 工作表名称
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreateSheetResponseBody(TeaModel):
    def __init__(
        self,
        visibility: str = None,
        name: str = None,
    ):
        # 工作表可见性
        self.visibility = visibility
        # 创建的工作表的名称。当输入参数中的工作表名称在表格中已存在时，可能与输入参数指定的工作表名称不同。
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.visibility is not None:
            result['visibility'] = self.visibility
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('visibility') is not None:
            self.visibility = m.get('visibility')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreateSheetResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: CreateSheetResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = CreateSheetResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateWorkspaceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class CreateWorkspaceRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
        description: str = None,
        operator_id: str = None,
        ding_org_id: int = None,
        ding_uid: int = None,
        ding_access_token_type: str = None,
        ding_isv_org_id: int = None,
    ):
        # 团队空间名称
        self.name = name
        # 团队空间描述
        self.description = description
        # 用户id
        self.operator_id = operator_id
        self.ding_org_id = ding_org_id
        self.ding_uid = ding_uid
        self.ding_access_token_type = ding_access_token_type
        self.ding_isv_org_id = ding_isv_org_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.description is not None:
            result['description'] = self.description
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.ding_org_id is not None:
            result['dingOrgId'] = self.ding_org_id
        if self.ding_uid is not None:
            result['dingUid'] = self.ding_uid
        if self.ding_access_token_type is not None:
            result['dingAccessTokenType'] = self.ding_access_token_type
        if self.ding_isv_org_id is not None:
            result['dingIsvOrgId'] = self.ding_isv_org_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('dingOrgId') is not None:
            self.ding_org_id = m.get('dingOrgId')
        if m.get('dingUid') is not None:
            self.ding_uid = m.get('dingUid')
        if m.get('dingAccessTokenType') is not None:
            self.ding_access_token_type = m.get('dingAccessTokenType')
        if m.get('dingIsvOrgId') is not None:
            self.ding_isv_org_id = m.get('dingIsvOrgId')
        return self


class CreateWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        name: str = None,
        description: str = None,
        url: str = None,
    ):
        # 工作空间id
        self.workspace_id = workspace_id
        # 工作空间名称
        self.name = name
        # 工作空间描述
        self.description = description
        # 工作空间打开url
        self.url = url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.name is not None:
            result['name'] = self.name
        if self.description is not None:
            result['description'] = self.description
        if self.url is not None:
            result['url'] = self.url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('url') is not None:
            self.url = m.get('url')
        return self


class CreateWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: CreateWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = CreateWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteWorkspaceDocMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class DeleteWorkspaceDocMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        return self


class DeleteWorkspaceDocMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[DeleteWorkspaceDocMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = DeleteWorkspaceDocMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class DeleteWorkspaceDocMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class GetWorkspaceHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        url: str = None,
        is_deleted: bool = None,
        owner: str = None,
        corp_id: str = None,
    ):
        self.url = url
        self.is_deleted = is_deleted
        self.owner = owner
        # 团队空间所属企业id
        self.corp_id = corp_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.url is not None:
            result['url'] = self.url
        if self.is_deleted is not None:
            result['isDeleted'] = self.is_deleted
        if self.owner is not None:
            result['owner'] = self.owner
        if self.corp_id is not None:
            result['corpId'] = self.corp_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('isDeleted') is not None:
            self.is_deleted = m.get('isDeleted')
        if m.get('owner') is not None:
            self.owner = m.get('owner')
        if m.get('corpId') is not None:
            self.corp_id = m.get('corpId')
        return self


class GetWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class SearchWorkspaceDocsHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class SearchWorkspaceDocsRequest(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        operator_id: str = None,
        keyword: str = None,
        max_results: int = None,
        next_token: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 发起操作用户unionId
        self.operator_id = operator_id
        # 搜索关键字
        self.keyword = keyword
        # 搜索数量
        self.max_results = max_results
        # 翻页Id
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.keyword is not None:
            result['keyword'] = self.keyword
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('keyword') is not None:
            self.keyword = m.get('keyword')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class SearchWorkspaceDocsResponseBodyDocsNodeBO(TeaModel):
    def __init__(
        self,
        name: str = None,
        node_id: str = None,
        url: str = None,
        last_edit_time: int = None,
        doc_type: str = None,
    ):
        # 节点名称
        self.name = name
        # 节点Id
        self.node_id = node_id
        # 节点打开url
        self.url = url
        # 最近编辑时间
        self.last_edit_time = last_edit_time
        # 节点类型
        self.doc_type = doc_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        return self


class SearchWorkspaceDocsResponseBodyDocsWorkspaceBO(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        name: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间名称
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class SearchWorkspaceDocsResponseBodyDocs(TeaModel):
    def __init__(
        self,
        node_bo: SearchWorkspaceDocsResponseBodyDocsNodeBO = None,
        workspace_bo: SearchWorkspaceDocsResponseBodyDocsWorkspaceBO = None,
    ):
        self.node_bo = node_bo
        self.workspace_bo = workspace_bo

    def validate(self):
        if self.node_bo:
            self.node_bo.validate()
        if self.workspace_bo:
            self.workspace_bo.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_bo is not None:
            result['nodeBO'] = self.node_bo.to_map()
        if self.workspace_bo is not None:
            result['workspaceBO'] = self.workspace_bo.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeBO') is not None:
            temp_model = SearchWorkspaceDocsResponseBodyDocsNodeBO()
            self.node_bo = temp_model.from_map(m['nodeBO'])
        if m.get('workspaceBO') is not None:
            temp_model = SearchWorkspaceDocsResponseBodyDocsWorkspaceBO()
            self.workspace_bo = temp_model.from_map(m['workspaceBO'])
        return self


class SearchWorkspaceDocsResponseBody(TeaModel):
    def __init__(
        self,
        has_more: bool = None,
        next_token: str = None,
        docs: List[SearchWorkspaceDocsResponseBodyDocs] = None,
    ):
        # 是否还有可搜索内容
        self.has_more = has_more
        self.next_token = next_token
        self.docs = docs

    def validate(self):
        if self.docs:
            for k in self.docs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.has_more is not None:
            result['hasMore'] = self.has_more
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['docs'] = []
        if self.docs is not None:
            for k in self.docs:
                result['docs'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('hasMore') is not None:
            self.has_more = m.get('hasMore')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.docs = []
        if m.get('docs') is not None:
            for k in m.get('docs'):
                temp_model = SearchWorkspaceDocsResponseBodyDocs()
                self.docs.append(temp_model.from_map(k))
        return self


class SearchWorkspaceDocsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: SearchWorkspaceDocsResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = SearchWorkspaceDocsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateRangeHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class UpdateRangeRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        values: List[List[str]] = None,
        background_colors: List[List[str]] = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id
        # 值
        self.values = values
        # 背景色
        self.background_colors = background_colors

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.values is not None:
            result['values'] = self.values
        if self.background_colors is not None:
            result['backgroundColors'] = self.background_colors
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('values') is not None:
            self.values = m.get('values')
        if m.get('backgroundColors') is not None:
            self.background_colors = m.get('backgroundColors')
        return self


class UpdateRangeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class BatchGetWorkspacesHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class BatchGetWorkspacesRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        include_recent: bool = None,
        workspace_ids: List[str] = None,
        ding_org_id: int = None,
        ding_isv_org_id: int = None,
        ding_uid: int = None,
        ding_access_token_type: str = None,
    ):
        # 操作用户unionId
        self.operator_id = operator_id
        # 是否查询最近访问文档
        self.include_recent = include_recent
        # 待查询空间Id
        self.workspace_ids = workspace_ids
        self.ding_org_id = ding_org_id
        self.ding_isv_org_id = ding_isv_org_id
        self.ding_uid = ding_uid
        self.ding_access_token_type = ding_access_token_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.include_recent is not None:
            result['includeRecent'] = self.include_recent
        if self.workspace_ids is not None:
            result['workspaceIds'] = self.workspace_ids
        if self.ding_org_id is not None:
            result['dingOrgId'] = self.ding_org_id
        if self.ding_isv_org_id is not None:
            result['dingIsvOrgId'] = self.ding_isv_org_id
        if self.ding_uid is not None:
            result['dingUid'] = self.ding_uid
        if self.ding_access_token_type is not None:
            result['dingAccessTokenType'] = self.ding_access_token_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('includeRecent') is not None:
            self.include_recent = m.get('includeRecent')
        if m.get('workspaceIds') is not None:
            self.workspace_ids = m.get('workspaceIds')
        if m.get('dingOrgId') is not None:
            self.ding_org_id = m.get('dingOrgId')
        if m.get('dingIsvOrgId') is not None:
            self.ding_isv_org_id = m.get('dingIsvOrgId')
        if m.get('dingUid') is not None:
            self.ding_uid = m.get('dingUid')
        if m.get('dingAccessTokenType') is not None:
            self.ding_access_token_type = m.get('dingAccessTokenType')
        return self


class BatchGetWorkspacesResponseBodyWorkspacesWorkspaceRecentList(TeaModel):
    def __init__(
        self,
        node_id: str = None,
        name: str = None,
        url: str = None,
        last_edit_time: str = None,
    ):
        # 文档Id
        self.node_id = node_id
        # 文档名称
        self.name = name
        # 文档打开url
        self.url = url
        # 最近编辑时间
        self.last_edit_time = last_edit_time

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.name is not None:
            result['name'] = self.name
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        return self


class BatchGetWorkspacesResponseBodyWorkspacesWorkspace(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        name: str = None,
        url: str = None,
        recent_list: List[BatchGetWorkspacesResponseBodyWorkspacesWorkspaceRecentList] = None,
        org_published: bool = None,
        create_time: int = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间名称
        self.name = name
        # 团队空间打开url
        self.url = url
        # 最近访问列表
        self.recent_list = recent_list
        # 是否全员公开
        self.org_published = org_published
        # 团队空间创建时间
        self.create_time = create_time

    def validate(self):
        if self.recent_list:
            for k in self.recent_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.name is not None:
            result['name'] = self.name
        if self.url is not None:
            result['url'] = self.url
        result['recentList'] = []
        if self.recent_list is not None:
            for k in self.recent_list:
                result['recentList'].append(k.to_map() if k else None)
        if self.org_published is not None:
            result['orgPublished'] = self.org_published
        if self.create_time is not None:
            result['createTime'] = self.create_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('url') is not None:
            self.url = m.get('url')
        self.recent_list = []
        if m.get('recentList') is not None:
            for k in m.get('recentList'):
                temp_model = BatchGetWorkspacesResponseBodyWorkspacesWorkspaceRecentList()
                self.recent_list.append(temp_model.from_map(k))
        if m.get('orgPublished') is not None:
            self.org_published = m.get('orgPublished')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        return self


class BatchGetWorkspacesResponseBodyWorkspaces(TeaModel):
    def __init__(
        self,
        has_permission: bool = None,
        workspace: BatchGetWorkspacesResponseBodyWorkspacesWorkspace = None,
    ):
        # 是否有访问团队空间权限
        self.has_permission = has_permission
        # 团队空间信息
        self.workspace = workspace

    def validate(self):
        if self.workspace:
            self.workspace.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.has_permission is not None:
            result['hasPermission'] = self.has_permission
        if self.workspace is not None:
            result['workspace'] = self.workspace.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('hasPermission') is not None:
            self.has_permission = m.get('hasPermission')
        if m.get('workspace') is not None:
            temp_model = BatchGetWorkspacesResponseBodyWorkspacesWorkspace()
            self.workspace = temp_model.from_map(m['workspace'])
        return self


class BatchGetWorkspacesResponseBody(TeaModel):
    def __init__(
        self,
        workspaces: List[BatchGetWorkspacesResponseBodyWorkspaces] = None,
    ):
        # workspace信息
        self.workspaces = workspaces

    def validate(self):
        if self.workspaces:
            for k in self.workspaces:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['workspaces'] = []
        if self.workspaces is not None:
            for k in self.workspaces:
                result['workspaces'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.workspaces = []
        if m.get('workspaces') is not None:
            for k in m.get('workspaces'):
                temp_model = BatchGetWorkspacesResponseBodyWorkspaces()
                self.workspaces.append(temp_model.from_map(k))
        return self


class BatchGetWorkspacesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: BatchGetWorkspacesResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = BatchGetWorkspacesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteWorkspaceMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class DeleteWorkspaceMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        return self


class DeleteWorkspaceMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[DeleteWorkspaceMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = DeleteWorkspaceMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class DeleteWorkspaceMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class AddWorkspaceDocMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class AddWorkspaceDocMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
        role_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type
        # 用户权限
        self.role_type = role_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        if self.role_type is not None:
            result['roleType'] = self.role_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        if m.get('roleType') is not None:
            self.role_type = m.get('roleType')
        return self


class AddWorkspaceDocMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[AddWorkspaceDocMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = AddWorkspaceDocMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class AddWorkspaceDocMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class UpdateWorkspaceMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class UpdateWorkspaceMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
        role_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type
        # 用户权限
        self.role_type = role_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        if self.role_type is not None:
            result['roleType'] = self.role_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        if m.get('roleType') is not None:
            self.role_type = m.get('roleType')
        return self


class UpdateWorkspaceMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[UpdateWorkspaceMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = UpdateWorkspaceMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class UpdateWorkspaceMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class GetSheetHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetSheetRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        return self


class GetSheetResponseBody(TeaModel):
    def __init__(
        self,
        name: List[str] = None,
        visibility: List[str] = None,
    ):
        # 工作表名称
        self.name = name
        # 工作表可见性
        self.visibility = visibility

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.visibility is not None:
            result['visibility'] = self.visibility
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('visibility') is not None:
            self.visibility = m.get('visibility')
        return self


class GetSheetResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetSheetResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetSheetResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetRelatedWorkspacesHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetRelatedWorkspacesRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        include_recent: bool = None,
    ):
        # 发起操作用户unionId
        self.operator_id = operator_id
        # 是否查询最近访问文档列表
        self.include_recent = include_recent

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.include_recent is not None:
            result['includeRecent'] = self.include_recent
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('includeRecent') is not None:
            self.include_recent = m.get('includeRecent')
        return self


class GetRelatedWorkspacesResponseBodyWorkspacesRecentList(TeaModel):
    def __init__(
        self,
        node_id: str = None,
        name: str = None,
        url: str = None,
        last_edit_time: int = None,
    ):
        # 文档id
        self.node_id = node_id
        # 文档名称
        self.name = name
        # 文档打开url
        self.url = url
        # 文档最后编辑时间
        self.last_edit_time = last_edit_time

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.name is not None:
            result['name'] = self.name
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        return self


class GetRelatedWorkspacesResponseBodyWorkspaces(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        url: str = None,
        deleted: bool = None,
        owner: str = None,
        role: str = None,
        name: str = None,
        recent_list: List[GetRelatedWorkspacesResponseBodyWorkspacesRecentList] = None,
        create_time: int = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间打开url
        self.url = url
        # 团队空间是否被删除
        self.deleted = deleted
        self.owner = owner
        # 用户的角色
        self.role = role
        # 团队空间名称
        self.name = name
        # 团队空间最近访问文档列表
        self.recent_list = recent_list
        # 团队空间创建时间
        self.create_time = create_time

    def validate(self):
        if self.recent_list:
            for k in self.recent_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.url is not None:
            result['url'] = self.url
        if self.deleted is not None:
            result['deleted'] = self.deleted
        if self.owner is not None:
            result['owner'] = self.owner
        if self.role is not None:
            result['role'] = self.role
        if self.name is not None:
            result['name'] = self.name
        result['recentList'] = []
        if self.recent_list is not None:
            for k in self.recent_list:
                result['recentList'].append(k.to_map() if k else None)
        if self.create_time is not None:
            result['createTime'] = self.create_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('deleted') is not None:
            self.deleted = m.get('deleted')
        if m.get('owner') is not None:
            self.owner = m.get('owner')
        if m.get('role') is not None:
            self.role = m.get('role')
        if m.get('name') is not None:
            self.name = m.get('name')
        self.recent_list = []
        if m.get('recentList') is not None:
            for k in m.get('recentList'):
                temp_model = GetRelatedWorkspacesResponseBodyWorkspacesRecentList()
                self.recent_list.append(temp_model.from_map(k))
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        return self


class GetRelatedWorkspacesResponseBody(TeaModel):
    def __init__(
        self,
        workspaces: List[GetRelatedWorkspacesResponseBodyWorkspaces] = None,
    ):
        # 团队空间结果集
        self.workspaces = workspaces

    def validate(self):
        if self.workspaces:
            for k in self.workspaces:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['workspaces'] = []
        if self.workspaces is not None:
            for k in self.workspaces:
                result['workspaces'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.workspaces = []
        if m.get('workspaces') is not None:
            for k in m.get('workspaces'):
                temp_model = GetRelatedWorkspacesResponseBodyWorkspaces()
                self.workspaces.append(temp_model.from_map(k))
        return self


class GetRelatedWorkspacesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetRelatedWorkspacesResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetRelatedWorkspacesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetRecentEditDocsHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetRecentEditDocsRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        max_results: int = None,
        next_token: str = None,
    ):
        # 发起操作用户unionId
        self.operator_id = operator_id
        # 查询size
        self.max_results = max_results
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class GetRecentEditDocsResponseBodyRecentListNodeBO(TeaModel):
    def __init__(
        self,
        node_id: str = None,
        node_name: str = None,
        url: str = None,
        last_edit_time: int = None,
        is_deleted: bool = None,
        doc_type: str = None,
    ):
        # 文档Id
        self.node_id = node_id
        # 文档名称
        self.node_name = node_name
        # 文档打开url
        self.url = url
        # 最后编辑时间
        self.last_edit_time = last_edit_time
        # 是否被删除
        self.is_deleted = is_deleted
        # 节点类型
        self.doc_type = doc_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.node_name is not None:
            result['nodeName'] = self.node_name
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        if self.is_deleted is not None:
            result['isDeleted'] = self.is_deleted
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('nodeName') is not None:
            self.node_name = m.get('nodeName')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        if m.get('isDeleted') is not None:
            self.is_deleted = m.get('isDeleted')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        return self


class GetRecentEditDocsResponseBodyRecentListWorkspaceBO(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        workspace_name: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间名称
        self.workspace_name = workspace_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.workspace_name is not None:
            result['workspaceName'] = self.workspace_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('workspaceName') is not None:
            self.workspace_name = m.get('workspaceName')
        return self


class GetRecentEditDocsResponseBodyRecentList(TeaModel):
    def __init__(
        self,
        node_bo: GetRecentEditDocsResponseBodyRecentListNodeBO = None,
        workspace_bo: GetRecentEditDocsResponseBodyRecentListWorkspaceBO = None,
    ):
        # 文档信息
        self.node_bo = node_bo
        # 团队空间信息
        self.workspace_bo = workspace_bo

    def validate(self):
        if self.node_bo:
            self.node_bo.validate()
        if self.workspace_bo:
            self.workspace_bo.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_bo is not None:
            result['nodeBO'] = self.node_bo.to_map()
        if self.workspace_bo is not None:
            result['workspaceBO'] = self.workspace_bo.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeBO') is not None:
            temp_model = GetRecentEditDocsResponseBodyRecentListNodeBO()
            self.node_bo = temp_model.from_map(m['nodeBO'])
        if m.get('workspaceBO') is not None:
            temp_model = GetRecentEditDocsResponseBodyRecentListWorkspaceBO()
            self.workspace_bo = temp_model.from_map(m['workspaceBO'])
        return self


class GetRecentEditDocsResponseBody(TeaModel):
    def __init__(
        self,
        recent_list: List[GetRecentEditDocsResponseBodyRecentList] = None,
        next_token: str = None,
    ):
        # 查询结果
        self.recent_list = recent_list
        self.next_token = next_token

    def validate(self):
        if self.recent_list:
            for k in self.recent_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['recentList'] = []
        if self.recent_list is not None:
            for k in self.recent_list:
                result['recentList'].append(k.to_map() if k else None)
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.recent_list = []
        if m.get('recentList') is not None:
            for k in m.get('recentList'):
                temp_model = GetRecentEditDocsResponseBodyRecentList()
                self.recent_list.append(temp_model.from_map(k))
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class GetRecentEditDocsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetRecentEditDocsResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetRecentEditDocsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetRecentOpenDocsHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetRecentOpenDocsRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        max_results: int = None,
        next_token: str = None,
    ):
        # 发起操作用户unionId
        self.operator_id = operator_id
        # 查询size
        self.max_results = max_results
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class GetRecentOpenDocsResponseBodyRecentListNodeBO(TeaModel):
    def __init__(
        self,
        node_id: str = None,
        node_name: str = None,
        url: str = None,
        last_open_time: int = None,
        is_deleted: bool = None,
        doc_type: str = None,
    ):
        # 文档Id
        self.node_id = node_id
        # 文档名称
        self.node_name = node_name
        # 文档打开url
        self.url = url
        # 最后编辑时间
        self.last_open_time = last_open_time
        # 是否被删除
        self.is_deleted = is_deleted
        # 节点类型
        self.doc_type = doc_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.node_name is not None:
            result['nodeName'] = self.node_name
        if self.url is not None:
            result['url'] = self.url
        if self.last_open_time is not None:
            result['lastOpenTime'] = self.last_open_time
        if self.is_deleted is not None:
            result['isDeleted'] = self.is_deleted
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('nodeName') is not None:
            self.node_name = m.get('nodeName')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastOpenTime') is not None:
            self.last_open_time = m.get('lastOpenTime')
        if m.get('isDeleted') is not None:
            self.is_deleted = m.get('isDeleted')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        return self


class GetRecentOpenDocsResponseBodyRecentListWorkspaceBO(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        workspace_name: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间名称
        self.workspace_name = workspace_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.workspace_name is not None:
            result['workspaceName'] = self.workspace_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('workspaceName') is not None:
            self.workspace_name = m.get('workspaceName')
        return self


class GetRecentOpenDocsResponseBodyRecentList(TeaModel):
    def __init__(
        self,
        node_bo: GetRecentOpenDocsResponseBodyRecentListNodeBO = None,
        workspace_bo: GetRecentOpenDocsResponseBodyRecentListWorkspaceBO = None,
    ):
        # 文档信息
        self.node_bo = node_bo
        # 团队空间信息
        self.workspace_bo = workspace_bo

    def validate(self):
        if self.node_bo:
            self.node_bo.validate()
        if self.workspace_bo:
            self.workspace_bo.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_bo is not None:
            result['nodeBO'] = self.node_bo.to_map()
        if self.workspace_bo is not None:
            result['workspaceBO'] = self.workspace_bo.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeBO') is not None:
            temp_model = GetRecentOpenDocsResponseBodyRecentListNodeBO()
            self.node_bo = temp_model.from_map(m['nodeBO'])
        if m.get('workspaceBO') is not None:
            temp_model = GetRecentOpenDocsResponseBodyRecentListWorkspaceBO()
            self.workspace_bo = temp_model.from_map(m['workspaceBO'])
        return self


class GetRecentOpenDocsResponseBody(TeaModel):
    def __init__(
        self,
        recent_list: List[GetRecentOpenDocsResponseBodyRecentList] = None,
        next_token: str = None,
    ):
        # 查询结果
        self.recent_list = recent_list
        self.next_token = next_token

    def validate(self):
        if self.recent_list:
            for k in self.recent_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['recentList'] = []
        if self.recent_list is not None:
            for k in self.recent_list:
                result['recentList'].append(k.to_map() if k else None)
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.recent_list = []
        if m.get('recentList') is not None:
            for k in m.get('recentList'):
                temp_model = GetRecentOpenDocsResponseBodyRecentList()
                self.recent_list.append(temp_model.from_map(k))
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class GetRecentOpenDocsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetRecentOpenDocsResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetRecentOpenDocsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AddWorkspaceMembersHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class AddWorkspaceMembersRequestMembers(TeaModel):
    def __init__(
        self,
        member_id: str = None,
        member_type: str = None,
        role_type: str = None,
    ):
        # 被操作用户unionId
        self.member_id = member_id
        # 用户类型
        self.member_type = member_type
        # 用户权限
        self.role_type = role_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.member_id is not None:
            result['memberId'] = self.member_id
        if self.member_type is not None:
            result['memberType'] = self.member_type
        if self.role_type is not None:
            result['roleType'] = self.role_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('memberId') is not None:
            self.member_id = m.get('memberId')
        if m.get('memberType') is not None:
            self.member_type = m.get('memberType')
        if m.get('roleType') is not None:
            self.role_type = m.get('roleType')
        return self


class AddWorkspaceMembersRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        members: List[AddWorkspaceMembersRequestMembers] = None,
    ):
        # 发起操作者unionId
        self.operator_id = operator_id
        # 被操作用户组
        self.members = members

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = AddWorkspaceMembersRequestMembers()
                self.members.append(temp_model.from_map(k))
        return self


class AddWorkspaceMembersResponseBody(TeaModel):
    def __init__(
        self,
        not_in_org_list: List[str] = None,
    ):
        self.not_in_org_list = not_in_org_list

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.not_in_org_list is not None:
            result['notInOrgList'] = self.not_in_org_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('notInOrgList') is not None:
            self.not_in_org_list = m.get('notInOrgList')
        return self


class AddWorkspaceMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: AddWorkspaceMembersResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = AddWorkspaceMembersResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteWorkspaceDocHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class DeleteWorkspaceDocRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
    ):
        # 发起删除请求的用户用户的unionId
        self.operator_id = operator_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        return self


class DeleteWorkspaceDocResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


class GetWorkspaceNodeHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class GetWorkspaceNodeRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
    ):
        # 操作用户unionId
        self.operator_id = operator_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        return self


class GetWorkspaceNodeResponseBodyNodeBO(TeaModel):
    def __init__(
        self,
        name: str = None,
        node_id: str = None,
        url: str = None,
        last_edit_time: int = None,
        doc_type: str = None,
    ):
        # 节点名称
        self.name = name
        # 节点Id
        self.node_id = node_id
        # 节点打开url
        self.url = url
        # 最后编辑时间
        self.last_edit_time = last_edit_time
        # 节点类型
        self.doc_type = doc_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.node_id is not None:
            result['nodeId'] = self.node_id
        if self.url is not None:
            result['url'] = self.url
        if self.last_edit_time is not None:
            result['lastEditTime'] = self.last_edit_time
        if self.doc_type is not None:
            result['docType'] = self.doc_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nodeId') is not None:
            self.node_id = m.get('nodeId')
        if m.get('url') is not None:
            self.url = m.get('url')
        if m.get('lastEditTime') is not None:
            self.last_edit_time = m.get('lastEditTime')
        if m.get('docType') is not None:
            self.doc_type = m.get('docType')
        return self


class GetWorkspaceNodeResponseBodyWorkspaceBO(TeaModel):
    def __init__(
        self,
        workspace_id: str = None,
        name: str = None,
    ):
        # 团队空间Id
        self.workspace_id = workspace_id
        # 团队空间名称
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.workspace_id is not None:
            result['workspaceId'] = self.workspace_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('workspaceId') is not None:
            self.workspace_id = m.get('workspaceId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetWorkspaceNodeResponseBody(TeaModel):
    def __init__(
        self,
        node_bo: GetWorkspaceNodeResponseBodyNodeBO = None,
        workspace_bo: GetWorkspaceNodeResponseBodyWorkspaceBO = None,
        has_permission: bool = None,
    ):
        # 节点信息
        self.node_bo = node_bo
        # 节点所属团队空间信息
        self.workspace_bo = workspace_bo
        # 是否有权限
        self.has_permission = has_permission

    def validate(self):
        if self.node_bo:
            self.node_bo.validate()
        if self.workspace_bo:
            self.workspace_bo.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.node_bo is not None:
            result['nodeBO'] = self.node_bo.to_map()
        if self.workspace_bo is not None:
            result['workspaceBO'] = self.workspace_bo.to_map()
        if self.has_permission is not None:
            result['hasPermission'] = self.has_permission
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('nodeBO') is not None:
            temp_model = GetWorkspaceNodeResponseBodyNodeBO()
            self.node_bo = temp_model.from_map(m['nodeBO'])
        if m.get('workspaceBO') is not None:
            temp_model = GetWorkspaceNodeResponseBodyWorkspaceBO()
            self.workspace_bo = temp_model.from_map(m['workspaceBO'])
        if m.get('hasPermission') is not None:
            self.has_permission = m.get('hasPermission')
        return self


class GetWorkspaceNodeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        body: GetWorkspaceNodeResponseBody = None,
    ):
        self.headers = headers
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('body') is not None:
            temp_model = GetWorkspaceNodeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AppendRowsHeaders(TeaModel):
    def __init__(
        self,
        common_headers: Dict[str, str] = None,
        x_acs_dingtalk_access_token: str = None,
    ):
        self.common_headers = common_headers
        self.x_acs_dingtalk_access_token = x_acs_dingtalk_access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.common_headers is not None:
            result['commonHeaders'] = self.common_headers
        if self.x_acs_dingtalk_access_token is not None:
            result['x-acs-dingtalk-access-token'] = self.x_acs_dingtalk_access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('commonHeaders') is not None:
            self.common_headers = m.get('commonHeaders')
        if m.get('x-acs-dingtalk-access-token') is not None:
            self.x_acs_dingtalk_access_token = m.get('x-acs-dingtalk-access-token')
        return self


class AppendRowsRequest(TeaModel):
    def __init__(
        self,
        operator_id: str = None,
        values: List[List[str]] = None,
    ):
        # 操作人unionId
        self.operator_id = operator_id
        # 要追加的值
        self.values = values

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.operator_id is not None:
            result['operatorId'] = self.operator_id
        if self.values is not None:
            result['values'] = self.values
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('operatorId') is not None:
            self.operator_id = m.get('operatorId')
        if m.get('values') is not None:
            self.values = m.get('values')
        return self


class AppendRowsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
    ):
        self.headers = headers

    def validate(self):
        self.validate_required(self.headers, 'headers')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        return self


