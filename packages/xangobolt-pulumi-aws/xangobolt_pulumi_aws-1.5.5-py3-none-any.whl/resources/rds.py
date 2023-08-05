from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import jsons
import pulumi_aws.rds as rds
import pulumi_aws_native.rds as rds_native

def Instance(stem, props, username=None, password=None, instance_class=None, apply_immediately=None, snetgrp_name=None, secgrp_ids=None, optgrp_name=None, provider=None, parent=None, depends_on=None):
    db_instance = rds.Instance(
        f'rds-inst-{stem}',
        # name='db-{stem}',
        identifier=f'rds-{stem}',
        instance_class=instance_class,
        engine='sqlserver-se',
        engine_version="15.00.4073.23.v1",
        apply_immediately=apply_immediately,
        username=username,
        password=password,
        storage_type='io1',
        iops=3000,
        allocated_storage=1500,
        max_allocated_storage=2000,
        # iam_database_authentication_enabled="true",
        publicly_accessible="true",
        license_model="license-included",
        skip_final_snapshot="True",
        performance_insights_enabled="True",
        vpc_security_group_ids=secgrp_ids,
        db_subnet_group_name=snetgrp_name,
        option_group_name=optgrp_name,
        backup_retention_period=7,
        backup_window="09:46-10:16",
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_instance

def Cluster(stem, props, username=None, password=None, engine=None, engine_version=None, apply_immediately=None, snetgrp_name=None, optgrp_name=None, secgrp_ids=None, provider=None, parent=None, depends_on=None):
    db_cluster = rds.Cluster(
        f'rds-clst-{stem}',
        cluster_identifier=f'rds-clst-{stem}',
        engine=engine,
        engine_version=engine_version,
        master_username=username,
        master_password=password,
        skip_final_snapshot="True",
        storage_encrypted="True",
        vpc_security_group_ids=secgrp_ids,
        db_subnet_group_name=snetgrp_name,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster

def ClusterInstance(stem, props, cluster_id=None, instance_class=None, engine=None, engine_version=None, apply_immediately=None, snetgrp_name=None, paramgrp_name=None, secgrp_ids=None, provider=None, parent=None, depends_on=None):
    db_cluster_instance = rds.ClusterInstance(
        f'rds-inst-{stem}',
        identifier=f'rds-inst-{stem}',
        cluster_identifier=cluster_id,
        instance_class=instance_class,
        apply_immediately=apply_immediately,
        engine=engine,
        engine_version=engine_version,
        publicly_accessible="true",
        # db_subnet_group_name=snetgrp_name,
        # db_parameter_group_name=paramgrp_name,
        performance_insights_enabled="True",
        preferred_backup_window="09:46-10:16",
        preferred_maintenance_window="Fri:22:00-Sat:05:00",
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster_instance

def SubnetGroup(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    sn_grp =rds.SubnetGroup(
        f'sngrp-{stem}',
        name=f'sngrp-{stem}',
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp

def OptionGroup(stem, props, provider=None, parent=None, depends_on=None):
    db_instance = rds.OptionGroup(
        f'optgrp-{stem}',
        name=f'optgrp-{stem}',
        option_group_description="Option Group",
        engine_name="sqlserver-se",
        major_engine_version="15.00",
        options=[
            rds.OptionGroupOptionArgs(
                option_name="SQLSERVER_BACKUP_RESTORE",
                option_settings=[rds.OptionGroupOptionOptionSettingArgs(
                    name="IAM_ROLE_ARN",
                    value="arn:aws:iam::917340184633:role/service-role/SET-SQL-BACKUP-RESTORE",
                )],
            )
        ],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_instance
