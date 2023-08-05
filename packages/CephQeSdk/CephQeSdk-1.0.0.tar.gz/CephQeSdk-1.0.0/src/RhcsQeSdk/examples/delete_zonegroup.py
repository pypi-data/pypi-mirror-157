from RhcsQeSdk.core.cli.ceph.ceph import Ceph
from RhcsQeSdk.core.cli.radosgw_admin.radosgw_admin import Radosgw_admin

kw = {
    "rgw-realm": "realm1",
    "rgw-zonegroup": "zonegroup1",
    "rgw-zone": "zone1",
    "access-key": None,
    "secret-key": None,
    "endpoints": None,
}

kwargs = {
    "service_type": "rgw",
    "service_name": "test",
    "realm": "realm1",
    "zone": "zone1",
    "placement": "'1 admin'",
}

rgw = Radosgw_admin()
ceph = Ceph()
rgw.realm.create(**kw)
rgw.zonegroup.create({"rgw-zonegroup": "zonegroup1", "default": True, "master": True})
rgw.zone.create(**kw)
rgw.zone.create({"rgw-zonegroup": "zonegroup1", "rgw-zone": "zone2"})
ceph.orch.apply(kwargs)
rgw.period.commit(**kw)
rgw.zonegroup.zonegroup_remove({"rgw-zonegroup": "zonegroup1", "rgw-zone": "zone2"})
rgw.period.commit(**kw)
rgw.zone.delete({"rgw-zone": "zone2"})
rgw.period.commit(**kw)
rgw.zonegroup.zonegroup_remove(**kw)
rgw.period.commit(**kw)
rgw.zonegroup.delete(**kw)
rgw.realm.delete(**kw)
