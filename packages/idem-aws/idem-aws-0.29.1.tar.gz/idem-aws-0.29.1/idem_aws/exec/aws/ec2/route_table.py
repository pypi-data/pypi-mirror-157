from typing import List


async def update_routes(
    hub,
    ctx,
    route_table_id: str,
    old_routes: List = None,
    new_routes: List = None,
):
    """
    Update routes of a route table. This function compares the existing(old) routes of route table with new routes.
    routes that are in the new route table but not in the old
    route table will be associated to route table. routes that are in the
    old route table  but not in the new route table will be disassociated from transit route table.

    Args:
        hub:
        ctx:
        route_table_id(Text): The AWS resource id of the existing route table
        old_routes(List):  routes of existing route table
        new_routes(List): new routes to update

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)

    # compare old_routes if routes are modified
    if new_routes is []:
        result["result"] = False
        result["comment"] = (
            "Route Table routes cannot be None. There should be at least one route in Route Table",
        )
        return result
    elif new_routes is not None:
        routes_to_modify = (
            hub.tool.aws.ec2.route_table_utils.get_route_table_routes_modifications(
                old_routes, new_routes
            )
        )
        if not routes_to_modify["result"]:
            result["comment"] = routes_to_modify["comment"]
            result["result"] = False
            return result
        routes_to_add = routes_to_modify["routes_to_add"]
        routes_to_delete = routes_to_modify["routes_to_delete"]
        routes_to_replace = routes_to_modify["routes_to_replace"]

        if not ctx.get("test", False):
            if routes_to_delete:
                for route_to_delete in routes_to_delete:
                    ret = await hub.exec.boto3.client.ec2.delete_route(
                        ctx, RouteTableId=route_table_id, **route_to_delete
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Deleted Routes: {routes_to_delete}, ",
                )
            if routes_to_replace:
                for route_to_replace in routes_to_replace:
                    ret = await hub.exec.boto3.client.ec2.replace_route(
                        ctx, RouteTableId=route_table_id, **route_to_replace
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Replace Routes: {routes_to_replace}, ",
                )
            if routes_to_add:
                for route_to_add in routes_to_add:
                    ret = await hub.exec.boto3.client.ec2.create_route(
                        ctx, RouteTableId=route_table_id, **route_to_add
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Added Routes: {routes_to_add}, ",
                )
    if result["comment"]:
        result["comment"] = result["comment"] + (
            f"Updated route table {route_table_id}",
        )
    result["ret"] = {
        "routes": new_routes,
    }
    return result
