from typing import Any
from typing import Dict


async def modify(
    hub, name: str, raw_profile: Dict[str, Any], new_profile: Dict[str, Any]
):
    """
    Get some profile information from hub.OPT.acct.extras if it is not already in the profile
    """
    opt = getattr(hub, "OPT") or {}
    acct = opt.get("acct") or {}
    idem = opt.get("idem") or {}
    extras = acct.get("extras") or {}
    aws_opts = extras.get("aws") or {}

    # Make sure that the new_profile has a region name, get it from acct.extras.aws if needed
    if not new_profile.get("region_name"):
        hub.log.debug(f"No region named defined in profile")

        esm_opts = aws_opts.get("esm") or {}
        is_esm_profile = ("esm" in raw_profile) or (name == idem.get("esm_profile"))
        if is_esm_profile and "region_name" in esm_opts:
            hub.log.debug(
                "Getting region_name from hub.OPT.acct.extras.aws.esm.region_name"
            )

            # If this is an ESM profile then get the region name from acct.extras.aws.esm.region_name
            # Fall back to getting the region_name from acct.extras.aws.region_name
            new_profile["region_name"] = esm_opts.get("region_name")
        else:
            hub.log.debug(
                "Getting region_name from hub.OPT.acct.extras.aws.region_name"
            )
            # Fall back to getting the region_name from acct.extras.aws.region_name
            new_profile["region_name"] = aws_opts.get("region_name")

    if not new_profile["region_name"]:
        hub.log.error(f"No region_name defined for profile")
