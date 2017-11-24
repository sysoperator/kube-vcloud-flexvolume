from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.client import VCLOUD_STATUS_MAP
from pyvcloud.vcd.utils import extract_id
from vcloud.vapp import find_vm_in_vapp

def create_disk(ctx, name, size, storage_profile_name):
    try:
        disk_resource = ctx.vca.add_disk(
                ctx.config['vdc'],
                name,
                size=size,
                storage_profile_name=storage_profile_name
        )
        tasks = disk_resource[1].get_Tasks()

        if tasks:
           ctx.vca.block_until_completed(tasks[0])
    except Exception as e:
        return False
    return True

def delete_disk(ctx, name):
    result = []
    try:
        disks = get_disks(ctx)
        for disk in disks:
            if disk['name'] == name:
                ctx.vca.delete_disk(
                        ctx.config['vdc'],
                        name,
                        disk['id']
                )
                result.append(disk['id'])
    except Exception as e:
        pass
    return result

def attach_disk(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    vapp.attach_disk_to_vm(vm['vm_name'], disk_ref)
                    return True
    except Exception as e:
        raise
    return False

def detach_disk(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    vapp.detach_disk_from_vm(vm['vm_name'], disk_ref)
                    return True
    except Exception as e:
        raise
    return False

def get_disks(ctx):
    result = []
    attached_vm = \
        lambda x, disk: next((i['vm'] for i in x if i['disk'] == disk), None)

    try:
        disks = ctx.vdc.get_disks()
        disks_relation = get_vm_disk_relation(ctx)
        for disk in disks:
            disk_id = extract_id(disk.get('id'))
            result.append(
                {
                    'name': disk.get('name'),
                    'id': disk_id,
                    'size_bytes': disk.get('size'),
                    'status': VCLOUD_STATUS_MAP.get(int(disk.get('status'))),
                    'attached_vm': attached_vm(disks_relation, disk_id)
                }

            )
    except Exception as e:
        pass
    return result

def get_vm_disk_relation(ctx):
    result = []
    resource_type = 'vmDiskRelation'
    try:
        query = ctx.client.get_typed_query(
                resource_type,
                query_result_format=QueryResultFormat.ID_RECORDS)
        records = list(query.execute())
        for curr_disk in records:
            result.append(
                {
                    'disk': extract_id(curr_disk.get('disk')),
                    'vdc': extract_id(curr_disk.get('vdc')),
                    'vm': extract_id(curr_disk.get('vm'))
                }
            )
    except Exception as e:
        pass
    return result
