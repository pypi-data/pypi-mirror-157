# -*- coding : utf-8 -*-
"""
@File        : role_funcs.py
@Author      : liushuo
@Time        : 2022/5/25 4:20 PM
@Description :
"""

from departments.models import Role, UserRole
from departments.forms.forms import RoleForms
from departments.utils.error_response import Resp
from django.db import transaction
from departments.common.config import BadRequestCode, ServerErrorCode


def create_role(data: dict) -> dict:
    """
    新建角色
    :param data:{"name"： "角色名称"， "desc"： "备注"}
    :return:
    """
    # 校验数据
    checked = RoleForms(data)
    # 判断数据合法性
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg=checked.errors)
    # 找到最大的排序数
    # if code
    # code = Role.objects.aggregate(num=Max('code'))["num"]
    # data["code"] = int(code) + 1
    # data["is_edited"] = True
    # data["is_deleted"] = True
    # 查找组织里面是否有相同的角色
    same_role = Role.objects.filter(
        name=data["name"],
        organization_id=data["organization_id"]
    ).exists()
    # 如果角色名称存在，返回错
    if same_role:
        return Resp(code=ServerErrorCode, msg=f"[{data['name']}]该角色名称已经存在，请使用其他名称")

    role_instance = Role.objects.create(**data)
    return Resp(data={'id': role_instance.pk})


def get_roles(organization_id: int, role_name: str = None) -> dict:
    """
    通过组织id获取全量角色
    :param organization_id:
    :param role_name: 角色名称，默认为空
    :return:
    """
    items = list()
    # 在没有搜索框的情况下
    if not role_name:
        roles = Role.objects.filter(
            organization_id=organization_id,
            is_deleted=False
        )

        for i in roles:
            items.append({
                "id": i.id,
                "name": i.name,
                "desc": i.desc,
                "created_at": i.created_at
            })
    else:
        roles = Role.objects.filter(
            organization_id=organization_id,
            is_deleted=False,
            name__contains=role_name.strip()
        )
        for item in roles:
            items.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "desc": item.desc,
                    "created_at": item.created_at
                }
            )

    return Resp(data=items)


def get_role_object(organization_id: int, pk: int):
    """
    获取这个组织下，这个角色详情()
    :param organization_id:
    :param pk:
    :return:(返回的时候，id，全部)
    """
    try:
        instance = Role.objects.get(pk=pk, organization_id=organization_id, is_deleted=False)
        return Resp(
            data={"id": instance.id, "name": instance.name, "desc": instance.desc}
        )
    except Role.DoesNotExist:
        return Resp(code=ServerErrorCode, msg=f"the organization can't be found name: {pk}")


def update_role(pk: int, data: dict) -> dict:
    """
    更新角色信息
    :param pk:
    :param data:
    :return:
    """
    # 校验数据
    checked = RoleForms(data)
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg=checked.errors)
    organization_id = data["organization_id"]
    try:
        instance = Role.objects.get(pk=pk, organization_id=organization_id, is_deleted=False)
        # instance = Role.objects.get(pk=pk, organization_id=organization_id, is_deleted=False, is_edited=True)
        if not instance.is_edited:
            return Resp(code=BadRequestCode, msg="系统角色，不可修改")
        """
            我需要去查询，他要改的名字是否已经存在，如果角色名称已经存在提示：该角色名称已经存在，请使用其他名称
            如果没有存在，则修改保存数据
        """
        instance.name = data["name"]
        instance.desc = data["desc"]
        instance.save()
        return Resp(data="修改成功")
    except Exception as err:
        raise ValueError(f"{str(err)} id: {pk}")


def delete_role(organization_id: int, pk: int):
    """
    删除角色
    :param organization_id:
    :param pk:
    :return:
    """
    """
    按照id查询，假删除可以，id不会变，
               如果真删除，表中的id就会变---不用管id会不会变，显示出来就好了（根据需求来看把）

    （删除，查询当前角色下还有没有用户，如果没有用户的话，可以删除）
    (查询该角色下还有没有用户的时候，直接按照，组织id和角色的id去查就可以了吧，
    只要角色用户表里面有该角色，就说明该角色下用用户)
    """
    instance = Role.objects.get(pk=pk, organization_id=organization_id, is_deleted=False)
    if not instance.is_edited:
        return Resp(code=BadRequestCode, msg="系统角色，不可删除")
    if UserRole.objects.filter(
            role_id=pk,
    ).exists():
        return ValueError("当前角色下还有用户，无法删除")
    Role.objects.filter(pk=pk).delete()
    return Resp(data="删除成功")


#     Role.objects.filter(
#         pk=pk,
#         organization_id=organization_id,
#         is_edited=True,
#         is_deleted=False
#     # ).delete()
# ).update(is_deleted=True)

def edit_role(organization_id: int, pk: int):
    """
    启用/停用角色
    :param organization_id:
    :param pk:
    :return:
    """
    """
    先去查询这个角色
    判断是不是创建者和管理员，如果是的话，不能操作
    能不能把启用/停用写到一起。
    就写个if，判断是否启用为True，就把它直接赋值成Flase，否则把它赋值成Flase
    """
    instance = Role.objects.get(pk=pk, organization_id=organization_id)
    if not instance.is_edited:
        return Resp(code=BadRequestCode, msg="系统角色，不可操作")
    instance.is_enabled = not instance.is_edited
    instance.save()
    return Resp(data="修改成功")


def add_role_user(organization_id: int, role_id, user_ids: list):
    """
    添加对应角色的用户（批量添加）
    :param organization_id:
    :param role_id:
    :param user_ids:
    :return:
    """
    """
    如果批量给角色添加用户的话，先去角色表查询该角色是否存在
    如果存在，循环需要添加的用户id
    """
    if not Role.objects.filter(
            pk=role_id,
            organization_id=organization_id,
            is_deleted=False
    ).exists():
        return Resp(code=BadRequestCode, msg="该角色不存在")

    role_user_list = [
        UserRole(role_id=role_id, user_id=user) for user in user_ids
    ]
    try:
        UserRole.objects.bulk_create(role_user_list)
    except Exception as err:
        raise Exception(err)
    return Resp(data="添加成功")


def get_role_user(organization_id: int, role_id):
    """
    获取对应角色的用户
    :param organization_id:
    :param role_id:
    :return:
    """
    """
    如果查询该角色的所有用户，需要去角色用户表里面去查询，用户所对应的角色id，根据角色的id查询
    查出来的数据，为该角色对应的用户id
    """
    user_ids = UserRole.objects.filter(
        role__organization_id=organization_id,
        role__is_deleted=False,
        role_id=role_id
    ).order_by("id").values_list("user_id", flat=True)
    return Resp(data=list(user_ids))


def delete_role_user(organization_id: int, role_id, user_ids: list):
    """
    删除对应角色的用户（批量删除）
    :param organization_id:
    :param role_id:
    :param user_ids:
    :return:
    """
    """
    批量删除该角色下的用户，需要先查询该角色是否存在
    角色存在，按照用户的ids去删除
    """
    if not Role.objects.filter(
            organization_id=organization_id,
            pk=role_id
    ).exists():
        return Resp(code=BadRequestCode, msg="当前组织没有该角色")

    UserRole.objects.filter(
        role__organization_id=organization_id,
        role_id=role_id,
        user_id__in=user_ids
    ).delete()
    return Resp(data="删除成功")


def user_change_role(organization_id: int, user_id: int, role_ids: list):
    """
    用户变更角色
    :param organization_id:
    :param user_id:
    :param role_ids:
    :return:
    """
    try:
        valid_role_count = Role.objects.filter(id__in=role_ids, organization_id=organization_id).count()
        if not valid_role_count == len(role_ids):
            raise ValueError("参数错误")
        UserRole.objects.filter(
            role__organization_id=organization_id,
            user_id=user_id
        ).delete()

        changed_instance_list = [UserRole(role_id=id_, user_id=user_id) for id_ in role_ids]
        UserRole.objects.bulk_create(changed_instance_list)
        return Resp()
    except Exception as e:
        raise Exception(str(e))
