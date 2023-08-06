import copy
from typing import Any
from typing import Dict


async def update_tags(
    hub,
    ctx,
    resource_arn: str,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
):
    """
    Update tags of AWS Dynamo DB resources

    Args:
        resource_arn: Identifies the Amazon DynamoDB resource to which tags should be added.
            This value is an Amazon Resource Name (ARN).
        old_tags: Dict of existing tags
        new_tags: Dict of new tags

    Returns:
        {"result": True|False, "comment": ("A tuple",), "ret": dict of updated tags}

    """

    tags_to_add = {}
    tags_to_remove = []
    for key, value in new_tags.items():
        if key in old_tags and old_tags[key] != value or (key not in old_tags):
            tags_to_add[key] = value
    for key in old_tags:
        if key not in new_tags:
            tags_to_remove.append(key)
    result = dict(comment=(), result=True, ret={})
    if (not tags_to_remove) and (not tags_to_add):
        result["ret"] = copy.deepcopy(old_tags if old_tags else {})
        return result
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_error_message = f"Could not delete tags {tags_to_remove} for DynamoDB table with ARN {resource_arn}"
            delete_ret = await hub.exec.boto3.client.dynamodb.untag_resource(
                ctx, ResourceArn=resource_arn, TagKeys=tags_to_remove
            )
            if not delete_ret["result"]:
                hub.log.debug(delete_error_message)
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
    if tags_to_add:
        if not ctx.get("test", False):
            add_error_message = f"Could not create tags {tags_to_remove} for DynamoDB table with ARN {resource_arn}"
            create_tag_resp = await hub.exec.boto3.client.dynamodb.tag_resource(
                ctx,
                ResourceArn=resource_arn,
                Tags=hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags_to_add),
            )
            if not create_tag_resp:
                hub.log.debug(add_error_message)
                result["comment"] = result["comment"] + (
                    f"Could not update tags {tags_to_add}",
                )
                result["result"] = False
                return result

    result["ret"] = new_tags
    result["comment"] = (
        f"Updated tags: Added [{tags_to_add}] Removed [{tags_to_remove}]",
    )
    return result
