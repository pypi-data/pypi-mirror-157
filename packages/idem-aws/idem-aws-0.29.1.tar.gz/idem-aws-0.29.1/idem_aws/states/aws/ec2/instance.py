from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource", "soft_fail"]

TREQ = {
    "present": {
        "require": [
            "aws.ec2.vpc.present",
            "aws.ec2.subnet.present",
            "aws.iam.role.present",
        ],
    },
}

"""
run_instances options that aren't yet in the present state params:

    ipv6AddressCount - is this managed from "network_interfaces"?
    Ipv6Addressses - is this managed from "network_interfaces"?
"""


async def present(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    *,
    # From DescribeInstances
    image_id: str = None,
    instance_type: str = None,
    block_device_mappings: List[
        make_dataclass(
            "BlockDeviceMapping",
            [
                ("DeviceName", str, field(default=None)),
                ("VirtualName", str, field(default=None)),
                ("Ebs", Dict, field(default=None)),
                ("NoDevice", str, field(default=None)),
            ],
        )
    ] = None,
    ebs_optimized: bool = None,
    kernel_id: str = None,
    placement: Dict[str, Any] = None,
    subnet_id: str = None,
    network_interfaces: List[
        make_dataclass(
            "InstanceNetworkInterfaceSpecification",
            [
                ("AssociatePublicIpAddress", bool, field(default=None)),
                ("DeleteOnTermination", bool, field(default=None)),
                ("Description", str, field(default=None)),
                ("DeviceIndex", int, field(default=None)),
                ("Groups", List, field(default=None)),
                ("Ipv6AddressCount", int, field(default=None)),
                ("Ipv6Addresses", List, field(default=None)),
                ("NetworkInterfaceId", str, field(default=None)),
                ("PrivateIpAddress", str, field(default=None)),
                ("PrivateIpAddresses", List, field(default=None)),
                ("SecondaryPrivateIpAddressCount", int, field(default=None)),
                ("SubnetId", str, field(default=None)),
                ("AssociateCarrierIpAddress", bool, field(default=None)),
                ("InterfaceType", str, field(default=None)),
                ("NetworkCardIndex", int, field(default=None)),
                ("Ipv4Prefixes", List, field(default=None)),
                ("Ipv4PrefixCount", int, field(default=None)),
                ("Ipv6Prefixes", List, field(default=None)),
                ("Ipv6PrefixCount", int, field(default=None)),
            ],
        )
    ] = None,
    monitoring_enabled: bool = None,
    root_device_name: str = None,
    product_codes: List[Dict[str, str]] = None,
    source_dest_check: bool = None,
    running: bool = None,
    private_ip_address: str = None,
    reservation_id: str = None,
    owner_id: str = None,
    # From launchTemplate
    user_data: str = None,
    disable_api_termination: bool = None,
    instance_initiated_shutdown_behavior: str = None,
    enclave_options_enabled: bool = None,
    ram_disk_id: str = None,
    tags: Dict[str, str] = None,
    elastic_gpu_specifications: List[
        make_dataclass("ElasticGpuSpecification", [("Type", str, field(default=None))])
    ] = None,
    elastic_inference_accelerators: List[
        make_dataclass(
            "ElasticInferenceAccelerator",
            [("Type", str, field(default=None)), ("Count", int, field(default=None))],
        )
    ] = None,
    iam_instance_profile: Dict[str, str] = None,
    key_name: str = None,
    # Can only be changed on initial creation of an instance as far as we know so far
    instance_market_options: Dict[str, Any] = None,
    credit_specification: Dict[str, Any] = None,
    cpu_options: Dict[str, Any] = None,
    capacity_reservation_specification: Dict[str, str] = None,
    license_specifications: List[
        make_dataclass(
            "LicenseConfigurationRequest",
            [("LicenseConfigurationArn", str, field(default=None))],
        )
    ] = None,
    hibernation_enabled: bool = None,
    metadata_options: Dict[str, Any] = None,
    instance_requirements: Dict[str, Any] = None,
    private_dns_name_options: Dict[str, Any] = None,
    maintenance_options: Dict[str, Any] = None,
    sriov_net_support: str = None,
    # idem-heist options
    bootstrap: List[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Launches an instance using an AMI for which you have permissions.
    You can specify a number of options, or leave the default options.
    The following rules apply:
        - [EC2-VPC] If you don't specify a subnet ID, we choose a default subnet from your default VPC for you.
            If you don't have a default VPC, you must specify a subnet ID in the request.
        - [EC2-Classic] If don't specify an Availability Zone, we choose one for you.
            Some instance types must be launched into a VPC.
            If you do not have a default VPC, or if you do not specify a subnet ID, the request fails.
            For more information, see Instance types available only in a VPC.
        - [EC2-VPC] All instances have a network interface with a primary private IPv4 address.
            If you don't specify this address, we choose one from the IPv4 range of your subnet.
            Not all instance types support IPv6 addresses.
            For more information, see Instance types.
        - If you don't specify a security group ID, we use the default security group.
            For more information, see Security groups.
        - If any of the AMIs have a product code attached for which the user has not subscribed, the request fails.
        - You can create a launch template, which is a resource that contains the parameters to launch an instance.
            You can specify the launch template instead of specifying the launch parameters.
            An instance is ready for you to use when it's in the running state.
        - You can tag instances and EBS volumes during launch, after launch, or both.
        - Linux instances have access to the public key of the key pair at boot.
            You can use this key to provide secure access to the instance.
            Amazon EC2 public images use this feature to provide secure access without passwords.
            For more information, see Key pairs.

    Args:
        hub:
        ctx:
        name(Text): An Idem name of the resource.
        resource_id(Text): AWS Ec2 Instance ID
        tags(Dict, optional): The tags to apply to the resource. Defaults to None.
            * (Key, optional): The key of the tag. Constraints: Tag keys are case-sensitive and accept a maximum of 127 Unicode
                characters. May not begin with aws:.
            * (Value, optional): The value of the tag. Constraints: Tag values are case-sensitive and accept a maximum of 256
                Unicode characters.
        image_id(Text): The ID of an AMI
        instance_type(Text): The instance type to use for this instance on creation
        block_device_mappings((List[Dict[Text, Text]]):, optional): The block device mapping, which defines the EBS volumes and instance store volumes to attach to
            the instance at launch. For more information, see Block device mappings in the Amazon EC2 User
            Guide. Defaults to None.
            * (DeviceName, optional): The device name (for example, /dev/sdh or xvdh).
            * (VirtualName, optional): The virtual device name (ephemeralN). Instance store volumes are numbered starting from 0. An
                instance type with 2 available instance store volumes can specify mappings for ephemeral0 and
                ephemeral1. The number of available instance store volumes depends on the instance type. After
                you connect to the instance, you must mount the volume. NVMe instance store volumes are
                automatically enumerated and assigned a device name. Including them in your block device mapping
                has no effect. Constraints: For M3 instances, you must specify instance store volumes in the
                block device mapping for the instance. When you launch an M3 instance, we ignore any instance
                store volumes specified in the block device mapping for the AMI.
            * (Ebs, optional): Parameters used to automatically set up EBS volumes when the instance is launched.
            * (NoDevice, optional): To omit the device from the block device mapping, specify an empty string. When this property is
                specified, the device is removed from the block device mapping regardless of the assigned value.
        ebs_optimized(bool): Indicates whether the instance is optimized ofr Amazon EBS I/O.
        kernel_id(Text): The kernel associated with this instance, if applicable.
        placement(Dict[Text, Any]): The location where the instance launched, if applicable
        subnet_id(Text): The ID of the subnet in which the instance is running
        network_interfaces(List[Dict[Text, Any]], optional): The network interfaces to associate with the instance. If you specify a network interface, you
            must specify any security groups and subnets as part of the network interface. Defaults to None.
            * (AssociatePublicIpAddress, optional): Indicates whether to assign a public IPv4 address to an instance you launch in a VPC. The public
                IP address can only be assigned to a network interface for eth0, and can only be assigned to a
                new network interface, not an existing one. You cannot specify more than one network interface
                in the request. If launching into a default subnet, the default value is true.
            * (DeleteOnTermination, optional): If set to true, the interface is deleted when the instance is terminated. You can specify true
                only if creating a new network interface when launching an instance.
            * (Description, optional): The description of the network interface. Applies only if creating a network interface when
                launching an instance.
            * (DeviceIndex, optional): The position of the network interface in the attachment order. A primary network interface has a
                device index of 0. If you specify a network interface when launching an instance, you must
                specify the device index.
            * (Groups, optional): The IDs of the security groups for the network interface. Applies only if creating a network
                interface when launching an instance.
            * (Ipv6AddressCount, optional): A number of IPv6 addresses to assign to the network interface. Amazon EC2 chooses the IPv6
                addresses from the range of the subnet. You cannot specify this option and the option to assign
                specific IPv6 addresses in the same request. You can specify this option if you've specified a
                minimum number of instances to launch.
            * (Ipv6Addresses, optional): One or more IPv6 addresses to assign to the network interface. You cannot specify this option
                and the option to assign a number of IPv6 addresses in the same request. You cannot specify this
                option if you've specified a minimum number of instances to launch.
            * (NetworkInterfaceId, optional): The ID of the network interface. If you are creating a Spot Fleet, omit this parameter because
                you can’t specify a network interface ID in a launch specification.
            * (PrivateIpAddress, optional): The private IPv4 address of the network interface. Applies only if creating a network interface
                when launching an instance. You cannot specify this option if you're launching more than one
                instance in a RunInstances request.
            * (PrivateIpAddresses, optional): One or more private IPv4 addresses to assign to the network interface. Only one private IPv4
                address can be designated as primary. You cannot specify this option if you're launching more
                than one instance in a RunInstances request.
            * (SecondaryPrivateIpAddressCount, optional): The number of secondary private IPv4 addresses. You can't specify this option and specify more
                than one private IP address using the private IP addresses option. You cannot specify this
                option if you're launching more than one instance in a RunInstances request.
            * (SubnetId, optional): The ID of the subnet associated with the network interface. Applies only if creating a network
                interface when launching an instance.
            * (AssociateCarrierIpAddress, optional): Indicates whether to assign a carrier IP address to the network interface. You can only assign a
                carrier IP address to a network interface that is in a subnet in a Wavelength Zone. For more
                information about carrier IP addresses, see Carrier IP addresses in the Amazon Web Services
                Wavelength Developer Guide.
            * (InterfaceType, optional): The type of network interface. Valid values: interface | efa
            * (NetworkCardIndex, optional): The index of the network card. Some instance types support multiple network cards. The primary
                network interface must be assigned to network card index 0. The default is network card index 0.
                If you are using RequestSpotInstances to create Spot Instances, omit this parameter because you
                can’t specify the network card index when using this API. To specify the network card index, use
                RunInstances.
            * (Ipv4Prefixes, optional): One or more IPv4 delegated prefixes to be assigned to the network interface. You cannot use this
                option if you use the Ipv4PrefixCount option.
            * (Ipv4PrefixCount, optional): The number of IPv4 delegated prefixes to be automatically assigned to the network interface. You
                cannot use this option if you use the Ipv4Prefix option.
            * (Ipv6Prefixes, optional): One or more IPv6 delegated prefixes to be assigned to the network interface. You cannot use this
                option if you use the Ipv6PrefixCount option.
            * (Ipv6PrefixCount, optional): The number of IPv6 delegated prefixes to be automatically assigned to the network interface. You
                cannot use this option if you use the Ipv6Prefix option.
        monitoring_enabled(bool): Indicates whether detailed monitoring is enabled.
        root_device_name(Text): The device name of the root device (for example, /dev/sda1).
        product_codes(List[Dict[Text, Text]]: The product codes attached to the instance, if applicable.
        source_dest_check(bool): Indicates whether source/destination checking is enabled
        running(bool): Indicates whether the instance should be in the "running" state
        private_ip_address(Text): The Ipv4 address of the network interface within the subnet.
        reservation_id(Text): The ID of the reservation
        owner_id(Text): The ID of the AWS account that owns the reservation.
        user_data(Text): The user data for the instance
        disable_api_termination(bool): Indicates that an instance cannot be terminated using the Amazon Ec2 console, command line tool, or API.
        instance_initiated_shutdown_behavior(Text): Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown)
        enclave_options_enabled(bool): Indicates whether the instance is enabled for AWS Nitro Enclaves.
        ram_disk_id(Text): The ID of the RAM disk, if applicable.
        elastic_gpu_specifications(List, optional): An elastic GPU to associate with the instance. An Elastic GPU is a GPU resource that you can
            attach to your Windows instance to accelerate the graphics performance of your applications. For
            more information, see Amazon EC2 Elastic GPUs in the Amazon EC2 User Guide. Defaults to None.
            * (Type): The type of Elastic Graphics accelerator. For more information about the values to specify for
                Type, see Elastic Graphics Basics, specifically the Elastic Graphics accelerator column, in the
                Amazon Elastic Compute Cloud User Guide for Windows Instances.
        elastic_inference_accelerators(List, optional): An elastic inference accelerator to associate with the instance. Elastic inference accelerators
            are a resource you can attach to your Amazon EC2 instances to accelerate your Deep Learning (DL)
            inference workloads. You cannot specify accelerators from different generations in the same
            request. Defaults to None.
            * (Type):  The type of elastic inference accelerator. The possible values are eia1.medium, eia1.large,
                eia1.xlarge, eia2.medium, eia2.large, and eia2.xlarge.
            * (Count, optional):  The number of elastic inference accelerators to attach to the instance.  Default: 1
        iam_instance_profile(Dict[Text, Text]): The IAM instance profile
        key_name(Text): The name of the keypair
        instance_market_options(Dict[Text, Any]): The market (purchasing) option for the instance
        credit_specification(Dict[Text, Any]): The credit option for CPU usage of the instance.
        cpu_options(Dict[Text, Any]): The market (purchasing) option for the instance
        capacity_reservation_specification(Dict[Text, Text]): Information about the Capacity Reservation targeting option
        license_specifications(List[Dict[Text, Text]], optional): The license configurations. Defaults to None.
            * (LicenseConfigurationArn, optional): The Amazon Resource Name (ARN) of the license configuration.
        hibernation_enabled(bool): Indicates whether the instance is configured for hibernation.
        metadata_options(Dict[Text, Any]): The metadata options for the instance
        instance_requirements(Dict[Text, Any]): The attributes for the instance type.
            When you specify instance attributes, Amazon EC2 will identify instance types with these attributes.
        private_dns_name_options(Dict[Text, Any): The options for the instance hostname.
        maintenance_options(Dict[Text, Any]): The maintenance options for the instance.
        sriov_net_support(Text): Specifies whether enhanced networking with the Intel 82599 Virtual Function interface is enabled
        bootstrap(List[Dict[Text, Any]]): BootText options for provisioning an instance with "heist"



    Returns:
        Dict[Text, Any]

    Examples:

        .. code-block:: sls

            resource_is_present:
              aws.ec2.instance.present:
                - name: value
                - image_id: my_ami_id-0000000000000000
                - tags:
                    my_tag_key_1: my_tag_value_1
                    my_tag_key_2: my_tag_value_2
                - bootstrap:
                    - heist_manager: salt.minion
                      artifact_version: 1234

    """
    # Get all the parameters passed to this function as a single dictionary
    desired_state = {
        k: v
        for k, v in locals().items()
        if k not in ("hub", "ctx", "name", "resource_id", "kwargs")
    }

    result = dict(comment=[], old_state=None, new_state=None, name=name, result=True)

    for key in kwargs:
        result["comment"] += [f"Not explicitly supported keyword argument: '{key}'"]

    # Get the resource_id from ESM
    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    # Get the resource_id from the idempotency token
    if not resource_id:
        ret = await hub.tool.aws.ec2.instance.state.get(ctx, client_token=name)
        if ret:
            resource_id = ret["resource_id"]

    if resource_id:
        # Assume that the instance already exists since we have a resource_id
        resource = hub.tool.boto3.resource.create(ctx, "ec2", "Instance", resource_id)
        current_state = result["old_state"] = await hub.tool.aws.ec2.instance.state.get(
            ctx, instance_id=resource_id
        )

        if not result["old_state"]:
            result["comment"] += [
                f"Could not find instance for '{name}' with existing id '{resource_id}'"
            ]
            return result

        result["comment"] += [f"Instance '{name}' already exists"]
    else:
        # Create the instance if it doesn't already exist
        if ctx.test:
            result["new_state"] = hub.tool.aws.ec2.instance.state.test(**desired_state)
            result["comment"] += [f"Would create aws.ec2.instance '{name}'"]
            return result

        # Create a brand new instance with minimal arguments, it will be updated after creation
        create_ret = await hub.exec.boto3.client.ec2.run_instances(
            ctx,
            ClientToken=name,
            MaxCount=1,
            MinCount=1,
            # ramdisk and kernel can only be specified when an instance is stopped or on creation
            KernelId=kernel_id,
            RamDiskId=ram_disk_id,
            # We only need to add options that can ONLY be specified on creation or that are best specified at creation
            # If parameters have to be processed it's better to let them be handled by "update" plugins after creation
            ImageId=image_id,
            Placement=placement,
            SubnetId=subnet_id,
            UserData=user_data,
            EbsOptimized=ebs_optimized,
            PrivateIpAddress=private_ip_address,
            ElasticGpuSpecification=elastic_gpu_specifications,
            ElasticInferenceAccelerators=elastic_inference_accelerators,
            CreditSpecification=credit_specification,
            CpuOptions=cpu_options,
            CapacityReservationSpecification=capacity_reservation_specification,
            LicenseSpecifications=license_specifications,
            MetadataOptions=metadata_options,
            PrivateDnsNameOptions=private_dns_name_options,
            MaintenanceOptions=maintenance_options,
        )

        result["result"] &= create_ret.result
        if not create_ret:
            result["comment"] += [create_ret.comment]
            return result

        result["comment"] += [f"Created '{name}'"]
        resource_id = create_ret.ret["Instances"][0]["InstanceId"]
        # This makes sure the created VPC is saved to esm regardless if the subsequent update call fails or not.
        result["new_state"] = dict(name=name, resource_id=resource_id, **desired_state)
        result["force_save"] = True

        resource = hub.tool.boto3.resource.create(ctx, "ec2", "Instance", resource_id)

        hub.log.debug(f"Waiting for instance '{name}' to be created")

        present_ret = await hub.tool.aws.ec2.instance.state.convert_to_present(
            ctx, {"Reservations": [create_ret.ret]}
        )
        current_state = present_ret[resource_id]

    if not current_state:
        result["comment"] += [
            f"Unable to get the current_state, instance may still be undergoing creation: '{name}'"
        ]
        result["result"] = False
        return result

    changes_made = False
    # Compare the kwargs of this function to the presentized attributes of the instance
    for attribute, new_value in desired_state.items():
        if new_value is None:
            # No value has been explicitly given, leave this parameter alone
            continue

        old_value = current_state.get(attribute)
        if old_value != new_value:
            changes_made = True
            # There is a single file dedicated to updating each attribute of an ec2 instance.
            # Organization is key for managing such a large resource.
            # This "present" function should remain mostly the same, don't bloat it!
            # Add an attribute-specific file in idem_aws/tool/aws/ec2/instance/update to manage specific parameters.
            # Be sure to follow the contracts in idem_aws/tool/aws/ec2/instance/update/contracts
            if attribute not in hub.tool.aws.ec2.instance.update._loaded:
                result["comment"] += [
                    f"Modifying aws.ec2.instance attribute '{attribute}' is not yet supported"
                ]
                continue
            if ctx.test:
                result["comment"] += [
                    f"Would update aws.ec2.instance '{name}': {attribute}"
                ]
                continue
            # Call the appropriate tool to update each parameter that needs updating
            result["result"] &= await hub.tool.aws.ec2.instance.update[attribute].apply(
                ctx,
                resource,
                old_value=old_value,
                new_value=new_value,
                # This list is stored in memory
                # modifying this value in "update.apply" functions will update it in the "result" dictionary
                comments=result["comment"],
            )
            if not result["result"]:
                result["comment"] += [
                    f"Unable to update aws.ec2.instance attribute: {attribute}"
                ]
                return result

    # Get the final state of the resource
    if changes_made:
        if ctx.test:
            result["new_state"] = hub.tool.aws.ec2.instance.state.test(**desired_state)
        else:
            result["new_state"] = await hub.tool.aws.ec2.instance.state.get(
                ctx, instance_id=resource_id
            )
    else:
        result["new_state"] = current_state

    return result


async def absent(
    hub, ctx, name: str, resource_id: str = None, **kwargs
) -> Dict[str, Any]:
    """
    Shuts down the specified instance.
    Terminated instances remain visible after termination (for approximately one hour).

    Args:
        hub:
        ctx:
        name(Text): The name of the state.
        resource_id(Text): An instance id

    Returns:
        Dict[Text, Any]

    Examples:

        .. code-block:: sls

            resource_is_absent:
              aws.ec2.instance.absent:
                - name: value
    """
    result = dict(
        comment=[], old_state=ctx.old_state, new_state=None, name=name, result=True
    )

    # Get the resource_id from ESM
    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    # Get the resource_id from the idempotency token
    if not resource_id:
        ret = await hub.tool.aws.ec2.instance.state.get(ctx, client_token=name)
        if ret:
            resource_id = ret["resource_id"]

    # If there still is no resource_id, the instance is gone
    if not resource_id:
        result["comment"] += [f"'{name}' already terminated"]
        return result

    if ctx.test:
        result["comment"] += [f"Would terminate aws.ec2.instance '{name}'"]
        return result

    ret = await hub.exec.boto3.client.ec2.terminate_instances(
        ctx, InstanceIds=[resource_id]
    )
    result["result"] &= ret["result"]
    if not result["result"]:
        result["comment"].append(ret["comment"])
        return result
    result["comment"] += [
        f"Terminated instance '{name}', it will still be visible for about 60 minutes"
    ]

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    """
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Returns:
        Dict[Text, Any]

    Examples:

        .. code-block:: bash

            $ idem describe aws.ec2.instance
    """
    result = {}
    ret = await hub.exec.boto3.client.ec2.describe_instances(ctx)

    if not ret:
        hub.log.debug(f"Could not describe Instances: {ret.comment}")
        return {}

    instances = await hub.tool.aws.ec2.instance.state.convert_to_present(ctx, ret.ret)

    for instance_id, present_state in instances.items():
        result[instance_id] = {
            "aws.ec2.instance.present": [{k: v} for k, v in present_state.items()]
        }

    return result


async def search(hub, ctx, name: str, filters: List = None, resource_id: str = None):
    """
    Use an un-managed Instance as a data-source. Supply one of the inputs as the filter.

    Args:
        hub:
        ctx:
        name(Text): The name of the Idem state.
        resource_id(Text, optional): AWS Ec2 Instance id to identify the resource.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key.
        A complete list of filters can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances

    Request Syntax:
        [Idem-state-name]:
          aws.ec2.instance.search:
          - resource_id: 'Text'
          - filters:
            - name: 'string'
              values: 'list'
            - name: 'string'
              values: 'list'

        Examples:

            my-unmanaged-instance:
              aws.ec2.instance.search:
                - resource_id: value
    """
    result = dict(
        comment=[], old_state=ctx.old_state, new_state=None, name=name, result=True
    )

    # Get the resource_id from ESM if this resource used to be managed by "present"
    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    # Perform validation on the parameters
    syntax_validation = hub.tool.aws.search_utils.search_filter_syntax_validation(
        filters=filters
    )
    result["result"] &= syntax_validation["result"]
    if not result["result"]:
        result["comment"].append(syntax_validation["comment"])
        return result

    boto3_filter = hub.tool.aws.search_utils.convert_search_filter_to_boto3(
        filters=filters
    )

    # Get all instances that match the given filters
    ret = await hub.exec.boto3.client.ec2.describe_instances(
        ctx,
        Filters=boto3_filter,
        InstanceIds=[resource_id] if resource_id else None,
    )
    result["result"] &= ret.result
    if not ret:
        result["comment"].append(ret.comment)
        return result

    # Convert the described instances to the present state format
    instances = await hub.tool.aws.ec2.instance.state.convert_to_present(ctx, ret.ret)

    # Check for null results
    if not instances:
        result["result"] = False
        result["comment"] += [
            f"Unable to find an aws.ec2.instance for '{name}' that matched the given filters"
        ]
        return result

    # Get the first instance from the results
    instance_id = next(iter(instances.keys()))

    # Add a comment if there were multiple results
    if len(instances) > 1:
        result["comment"] += [
            f"More than one aws.ec2.instance resource was found. Use resource '{instance_id}'"
        ]

    # Return both old_state and new_state together
    result["new_state"] = instances[instance_id]

    return result
