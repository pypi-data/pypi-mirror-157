import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.blocklist import Blocklist
from RhcsQeSdk.core.cli.ceph.crush import Crush
from RhcsQeSdk.core.cli.ceph.erasurecodeprofile import ErasureCodeProfile
from RhcsQeSdk.core.cli.ceph.pool import Pool
from RhcsQeSdk.core.cli.ceph.tier import Tier
from RhcsQeSdk.core.utilities import core_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Osd:
    """This module provides CLI interface to manage OSD configuration and administration via ceph osd."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " osd"
        self.pool = Pool(self.base_cmd)
        self.crush = Crush(self.base_cmd)
        self.blocklist = Blocklist(self.base_cmd)
        self.erasure_code_profile = ErasureCodeProfile(self.base_cmd)
        self.tier = Tier(self.base_cmd)

    def blocked_by(self, **kw):
        """
        Subcommand blocked-by prints a histogram of which OSDs are blocking their peers

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} blocked-by"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def create(self, **kw):
        """
        Create the OSD. If no UUID is given, it will be set automatically when the OSD starts up.
        The following command will output the OSD number, which you will need for subsequent steps.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              UUID(str) : new OSD will have the specified uuid (optional)
              ID(str)   : auth entity client.osd.<id> (optional)
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        UUID = kw.get("UUID")
        ID = kw.get("ID")
        cmd = f"{self.base_cmd} create"
        if UUID:
            cmd = cmd + f" {UUID}"
        if ID:
            cmd = cmd + f" {ID}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def new(self, **kw):
        """
        Subcommand new can be used to create a new OSD or to recreate a previously destroyed OSD with a specific id.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              UUID(str)        : new OSD will have the specified uuid
              ID(str)          : auth entity client.osd.<id>
              params_file(str) : JSON file containing the base64 cephx key for auth entity client.osd.<id>,
                                 as well as optional base64 cepx key for dm-crypt lockbox access
                                 and a dm-crypt key (optional)

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        UUID = kw.get("UUID", "")
        ID = kw.get("ID", "")
        params_file = kw.get("params_file")
        cmd = f"{self.base_cmd} new {UUID} {ID} -i {params_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def deep_scrub(self, **kw):
        """
        Subcommand deep-scrub initiates deep scrub on specified osd.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              who(str)  :  entity

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who")
        cmd = f"{self.base_cmd} deep-scrub {who}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def df(self, **kw):
        """
        Subcommand df shows OSD utilization

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              option(str)  :  values are plain/tree

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option")
        cmd = f"{self.base_cmd} df {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def down(self, **kw):
        """
        Subcommand down sets osd(s) <id> [<id>…] down.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(list)  :  list of osd id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} down {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump(self, **kw):
        """
        Subcommand dump prints summary of OSD map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  OSD id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} dump {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def find(self, **kw):
        """
        Subcommand find finds osd <id> in the CRUSH map and shows its location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  OSD id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} find {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getcrushmap(self, **kw):
        """
        Subcommand getcrushmap gets CRUSH map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  OSD id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} getcrushmap {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getmap(self, **kw):
        """
        Subcommand getmap gets OSD map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              epoch(int): epoch
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("epoch", "")
        cmd = f"{self.base_cmd} getmap {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getmaxosd(self, **kw):
        """
        Subcommand getmaxosd shows largest OSD id.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} getmaxosd"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def in_(self, **kw):
        """
        Subcommand in sets osd(s) <id> [<id>…] in.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(list)  :  list of osd id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} in {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def lost(self, **kw):
        """
        Subcommand lost marks osd as permanently lost. THIS DESTROYS DATA IF NO MORE REPLICAS EXIST, BE CAREFUL.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  OSD id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} lost {osd_id} --yes-i-really-mean-it"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Subcommand ls shows all OSD ids.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def lspools(self, **kw):
        """
        The lspools command will display the list of all pools in the cluster.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " lspools"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def map_(self, **kw):
        """
        Subcommand map finds pg for <object> in <pool>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              pool_name(str)  :  pool name
              object_name(str)  :  object name

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name")
        object_name = kw.get("object_name")
        cmd = f"{self.base_cmd} map {pool_name} {object_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def metadata(self, **kw):
        """
        Subcommand metadata fetches metadata for osd <id>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  osd id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} metadata {osd_id} (default all)"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def out(self, **kw):
        """
        Subcommand out sets osd(s) <id> [<id>…] out.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(list)  :  list of osd id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} out {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ok_to_stop(self, **kw):
        """
        Subcommand ok-to-stop checks whether the list of OSD(s) can be stopped
        without immediately making data unavailable.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(str)  :  list of osd id's
              max(int)      :  maximum number up to <num> OSDs IDs will return (including the provided OSDs)
                               that can all be stopped simultaneously (optional)

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        id_list = kw_copy.pop("id_list", "")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} ok-to-stop {id_str}"
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = cmd + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def pause(self, **kw):
        """
        Subcommand pause pauses osd.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} pause"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def perf(self, **kw):
        """
        Subcommand perf prints dump of OSD perf summary stats.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        cmd = f"{self.base_cmd} perf"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def pg_temp(self, **kw):
        """
        Subcommand pg-temp set pg_temp mapping pgid:[<id> [<id>…]] (developers only).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              pgid(str)        :  id of pg
              id_list(list)  :  list of id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pgid = kw.get("pgid")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} pg-temp {pgid} {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def force_create_pg(self, **kw):
        """
        Subcommand force-create-pg forces creation of pg <pgid>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              pgid(str)  :  id of pg

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pgid = kw.get("pgid")
        cmd = f"{self.base_cmd} force-create-pg {pgid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def primary_affinity(self, **kw):
        """
        Subcommand primary-affinity adjust osd primary-affinity from 0.0 <=<weight> <= 1.0

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_name(str)  :  name of osd
              osd_id(str)    :  osd id (alternate to osd_name)
              weight(float)  :  0.0 < weight < 1.0

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name")
        osd_id = kw.get("osd_id")
        weight = kw.get("weight")
        cmd = f"{self.base_cmd} primary-affinity {osd_name or osd_id} {weight}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def primary_temp(self, **kw):
        """
        Subcommand primary-temp sets primary_temp mapping pgid:<id>|-1 (developers only).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              pgid(str)  :  id of pg
              osd_id(str)  :  id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pgid = kw.get("pgid")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} primary-temp {pgid} {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def repair(self, **kw):
        """
        Subcommand repair initiates repair on a specified osd.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              who(str)  :  osd

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who")
        cmd = f"{self.base_cmd} repair {who}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight(self, **kw):
        """
        Subcommand reweight reweights osd to 0.0 < <weight> < 1.0.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  id of osd
              weight(float)  :  0.0 < weight < 1.0

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        weight = kw.get("weight")
        cmd = f"{self.base_cmd} reweight {osd_id} {weight}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight_by_pg(self, **kw):
        """
        Subcommand reweight-by-pg reweight OSDs by PG distribution [overload-percentage-for-consideration, default 120].

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)   :  osd id
              poolname_list(str)  :  list of pool names

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        poolname_list = kw.get("poolname_list")
        poolname_str = " ".join(poolname_list)
        cmd = f"{self.base_cmd} reweight-by-pg {osd_id} {poolname_str} --no-increasing"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight_by_utilization(self, **kw):
        """
        Subcommand reweight-by-utilization reweights OSDs by utilization.
        It only reweights outlier OSDs whose utilization exceeds the average

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)   :  osd id
              overload_threshold(int)  :  default 120
              max_weight_change(float) :  default 0.05
              max_osds_to_adjust(int)  :  default 4

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        overload_threshold = kw.get("overload_threshold", 120)
        max_weight_change = kw.get("max_weight_change", 0.05)
        max_osds_to_adjust = kw.get("max_osds_to_adjust", 4)
        cmd = (
            f"{self.base_cmd} reweight-by-utilization {osd_id}"
            f" {overload_threshold} {max_weight_change} {max_osds_to_adjust} --no-increasing"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Subcommand rm removes osd(s) <id> [<id>…] from the OSD map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(list)  :  list of osd id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} rm {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def destroy(self, **kw):
        """
        Subcommand destroy marks OSD id as destroyed, removing its cephx entity’s keys
        and all of its dm-crypt and daemon-private config key entries.
        This command will not remove the OSD from crush, nor will it remove the OSD from the OSD map.
        Instead, once the command successfully completes, the OSD will show marked as destroyed.
        In order to mark an OSD as destroyed, the OSD must first be marked as lost.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  osd id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} destroy {osd_id} --yes-i-really-mean-it"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def purge(self, **kw):
        """
        Subcommand purge performs a combination of osd destroy, osd rm and osd crush remove.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  osd id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} purge {osd_id} --yes-i-really-mean-it"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def safe_to_destroy(self, **kw):
        """
        Subcommand safe-to-destroy checks whether it is safe to remove or destroy an OSD
        without reducing overall data redundancy or durability.
        It will return a success code if it is definitely safe, or an error code and informative message if it is not or
        if no conclusion can be drawn at the current time.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              id_list(list)  :  list of osd id's

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        id_list = kw.get("id_list")
        id_str = " ".join(id_list)
        cmd = f"{self.base_cmd} safe-to-destory {id_str}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def scrub(self, **kw):
        """
        Subcommand scrub initiates scrub on specified osd.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              who(str)  :  entity

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who")
        cmd = f"{self.base_cmd} scrub {who}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Subcommand set sets cluster-wide <flag> by updating OSD map.
        The full flag is not honored anymore since the Mimic release,
        and ceph osd set full is not supported in the Octopus release.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              option(str)  :  pause|noup|nodown|noout|noin|nobackfill|norebalance|
                              norecover|noscrub|nodeep-scrub|notieragent

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option")
        cmd = f"{self.base_cmd} set {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def setcrushmap(self, **kw):
        """
        Subcommand setcrushmap sets crush map from input file.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} setcrushmap"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def setmaxosd(self, **kw):
        """
        Subcommand setmaxosd sets new maximum osd value.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              max_osd_val(int)  :  new maximum osd value.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        max_osd_val = kw.get("max_osd_val")
        cmd = f"{self.base_cmd} setmaxosd {max_osd_val}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_require_min_compat_client(self, **kw):
        """
        Subcommand set-require-min-compat-client enforces the cluster to be backward compatible
        with the specified client version

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              version(str)  :  version of the client

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        version = kw.get("version")
        cmd = f"{self.base_cmd} set-require-min-compat-client {version}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """
        Subcommand stat prints summary of OSD map.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} stat"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def tree(self, **kw):
        """
        Subcommand tree prints OSD tree.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              osd_id(str)  :  osd_id

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_id = kw.get("osd_id")
        cmd = f"{self.base_cmd} tree {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unpause(self, **kw):
        """
        Subcommand unpause unpauses osd.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} unpause"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unset(self, **kw):
        """
        Subcommand unset unsets cluster-wide <flag> by updating OSD map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              option(str)  :  pause|noup|nodown|noout|noin|nobackfill|
                              norebalance|norecover|noscrub|nodeep-scrub|notieragent

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option")
        cmd = f"{self.base_cmd} unset {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
