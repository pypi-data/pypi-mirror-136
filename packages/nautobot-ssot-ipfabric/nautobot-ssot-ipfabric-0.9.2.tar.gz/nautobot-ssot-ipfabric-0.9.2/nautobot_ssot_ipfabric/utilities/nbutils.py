"""Utility functions for Nautobot ORM."""
import datetime
from typing import Any, Optional

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.utils.text import slugify
from nautobot.dcim.models import DeviceRole, DeviceType, Manufacturer, Site
from nautobot.extras.models import Tag
from nautobot.extras.models.statuses import Status
from nautobot.ipam.models import IPAddress
from netutils.ip import netmask_to_cidr

CONFIG = settings.PLUGINS_CONFIG.get("nautobot_ssot_ipfabric", {})
ALLOW_DUPLICATE_IPS = CONFIG.get("ALLOW_DUPLICATE_ADDRESSES", True)


def create_site(site_name, site_id=None):
    """Creates a specified site in Nautobot.

    Args:
        site_name (str): Name of the site.
        site_id (str): ID of the site.
    """
    site_obj, _ = Site.objects.get_or_create(name=site_name)
    site_obj.slug = slugify(site_name)
    site_obj.status = Status.objects.get(name="Active")
    if site_id:
        site_obj.cf["ipfabric-site-id"] = site_id
    tag_object(nautobot_object=site_obj, custom_field="ssot-synced-from-ipfabric")
    return site_obj


def create_manufacturer(vendor_name):
    """Create specified manufacturer in Nautobot."""
    mf_name, _ = Manufacturer.objects.get_or_create(name=vendor_name)
    tag_object(nautobot_object=mf_name, custom_field="ssot-synced-from-ipfabric")
    return mf_name


def create_device_type_object(device_type, vendor_name):
    """Create a specified device type in Nautobot.

    Args:
        device_type (str): Device model gathered from DiffSync model.
        vendor_name (str): Vendor Name
    """
    mf_name = create_manufacturer(vendor_name)
    device_type_obj, _ = DeviceType.objects.get_or_create(
        manufacturer=mf_name, model=device_type, slug=slugify(device_type)
    )
    tag_object(nautobot_object=device_type_obj, custom_field="ssot-synced-from-ipfabric")
    return device_type_obj


def create_device_role_object(role_name, role_color):
    """Create specified device role in Nautobot.

    Args:
        role_name (str): Role name.
        role_color (str): Role color.
    """
    role_obj, _ = DeviceRole.objects.get_or_create(name=role_name, slug=slugify(role_name), color=role_color)
    tag_object(nautobot_object=role_obj, custom_field="ssot-synced-from-ipfabric")
    return role_obj


def create_status(status_name, status_color, description="", app_label="dcim", model="device"):
    """Verifies status object exists in Nautobot. If not, creates specified status. Defaults to dcim | device.

    Args:
        status_name (str): Status name.
        status_color (str): Status color.
        description (str): Description
        app_label (str): App Label ("DCIM")
        model (str): Django Model ("DEVICE")
    """
    try:
        status_obj = Status.objects.get(name=status_name)
    except Status.DoesNotExist:
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        status_obj = Status.objects.create(
            name=status_name,
            slug=slugify(status_name),
            color=status_color,
            description=description,
        )
        status_obj.content_types.set([content_type])
    return status_obj


def create_ip(ip_address, subnet_mask, status="Active", object_pk=None):
    """Verifies ip address exists in Nautobot. If not, creates specified ip.

    Utility behvariour is manipulated by `settings` if duplicate ip's are allowed.

    Args:
        ip_address (str): IP address.
        subnet_mask (str): Subnet mask used for IP Address.
        status (str): Status to assign to IP Address.
        object_pk: Object primary key
    """
    status_obj = Status.objects.get_for_model(IPAddress).get(slug=slugify(status))
    cidr = netmask_to_cidr(subnet_mask)
    if ALLOW_DUPLICATE_IPS:
        try:
            addr = IPAddress.objects.filter(host=ip_address)
            if addr.exists():
                if addr.first().assigned_object:  # If one is assigned, assume the rest are for now.
                    ip_obj = IPAddress.objects.create(
                        address=f"{ip_address}/{cidr}", status=status_obj, description="Duplicate by IPFabric SSoT"
                    )
            else:
                ip_obj = IPAddress.objects.get(address=f"{ip_address}/{cidr}", status=status_obj)
        except IPAddress.DoesNotExist:
            ip_obj = IPAddress.objects.create(address=f"{ip_address}/{cidr}", status=status_obj)
    else:
        ip_obj, _ = IPAddress.objects.get_or_create(address=f"{ip_address}/{cidr}", status=status_obj)

    if object_pk:
        ip_obj.assigned_object_id = object_pk.pk
    # Tag Interface
    tag_object(nautobot_object=object_pk, custom_field="ssot-synced-from-ipfabric")
    # Tag IP Addr
    tag_object(nautobot_object=ip_obj, custom_field="ssot-synced-from-ipfabric")
    return ip_obj


def create_interface(device_obj, interface_details):
    """Verifies interface exists on specified device. If not, creates interface.

    Args:
        device_obj (Device): Device object to check interface against.
        interface_details (dict): interface details.
    """
    interface_fields = (
        "name",
        "description",
        "enabled",
        "mac_address",
        "mtu",
        "type",
        "mgmt_only",
    )
    fields = {k: v for k, v in interface_details.items() if k in interface_fields and v}
    try:
        interface_obj, _ = device_obj.interfaces.get_or_create(**fields)
    except IntegrityError:
        interface_obj, _ = device_obj.interfaces.get_or_create(name=fields["name"])
        interface_obj.description = fields.get("description")
        interface_obj.enabled = fields.get("enabled")
        interface_obj.mac_address = fields.get("mac_address")
        interface_obj.mtu = fields.get("mtu")
        interface_obj.type = fields.get("type")
        interface_obj.mgmt_only = fields.get("mgmt_only", False)
        interface_obj.validated_save()
    tag_object(nautobot_object=interface_obj, custom_field="ssot-synced-from-ipfabric")
    return interface_obj


def create_vlan(vlan_name: str, vlan_id: int, vlan_status: str, site_obj: Site, description: str):
    """Creates or obtains VLAN object.

    Args:
        vlan_name (str): VLAN Name
        vlan_id (int): VLAN ID
        vlan_status (str): VLAN Status
        site_obj (Site): Site Django Model
        description (str): VLAN Description

    Returns:
        (VLAN): Returns created or obtained VLAN object.
    """
    vlan_obj, _ = site_obj.vlans.get_or_create(
        name=vlan_name, vid=vlan_id, status=Status.objects.get(name=vlan_status), description=description
    )
    tag_object(nautobot_object=vlan_obj, custom_field="ssot-synced-from-ipfabric")
    return vlan_obj


def tag_object(nautobot_object: Any, custom_field: str, tag_slug: Optional[str] = "ssot-synced-from-ipfabric"):
    """Apply the given tag and custom field to the identified object.

    Args:
        nautobot_object (Any): Nautobot ORM Object
        custom_field (str): Name of custom field to update
        tag_slug (Optional[str], optional): Tag slug to use as tag. Defaults to "ssot-synced-from-ipfabric".
    """
    tag = Tag.objects.get(slug=tag_slug)
    today = datetime.date.today().isoformat()

    def _tag_object(nautobot_object):
        """Apply custom field and tag to object, if applicable."""
        if hasattr(nautobot_object, "tags"):
            nautobot_object.tags.add(tag)
        if hasattr(nautobot_object, "cf"):
            nautobot_object.cf[custom_field] = today

    _tag_object(nautobot_object)
    # This does have a performance cost, but it's necessary to avoid many failure
    # scenarios and, tagging/custom fields. We could further revaluate.
    nautobot_object.validated_save()
