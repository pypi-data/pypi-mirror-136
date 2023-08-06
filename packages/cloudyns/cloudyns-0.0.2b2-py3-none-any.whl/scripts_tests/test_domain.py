import time

from cloudyns.base.dataclasses import CloudynsConf
from cloudyns.base.exceptions import ProviderManagerMissingDomain
# from cloudyns.managers.providers import DigitalOceanManager
from cloudyns.builder import build_provider_manager

if __name__ == "__main__":
    cloudyns_conf = CloudynsConf(
        provider="digitalocean",
        token="46fc9a9130d653448c5777974bd783e3d89a954e00ae68d7a0484cfa867c074f"
    )

    do_manager = build_provider_manager(conf=cloudyns_conf)

    print(f"do_manager: {do_manager}")
    print(f"do_manager.get_zones(): {do_manager.get_zones()}")

    print()

    computer_apes = do_manager.get_domain(domain_name="computerapes.com")
    print(f"do_manager.get_domain(domain_name=\"computerapes.com\"): {computer_apes}")

    print()

    print(f"exception do_manager.get_domain(domain_name=\"fake-dom.com\"): ")
    try:
        do_manager.get_domain(domain_name='fake-dom.com')
    except ProviderManagerMissingDomain as ex:
        print(f"\tProviderManagerMissingDomain: {ex}")

    print()

    print(f"Print records of ComputerApes: computer_apes.get_records()")
    [print(f"\t{dom}") for dom in computer_apes.get_records()]
    print(f"\tcomputer_apes.quantity_record: {computer_apes.quantity_record}")

    # print()
    # print(f"Records map computer_apes._records_map: {computer_apes._records_map}")

    print()

    # Add new record type A
    print(f"Print computer_apes.add_a_record(name='test-record', data='127.0.0.1'):")
    new_record = computer_apes.add_a_record(name='test-record', data='127.0.0.1')
    print(f"\n\t{new_record}")

    print()

    time.sleep(30)

    # Delete new record
    print(f"Print new_record.delete_record():")
    print(f"\n\t{new_record.delete_record()}")

    print()

    # Get records with the new record
    print(f"Print records of ComputerApes with new record added: computer_apes.get_records()")
    [print(f"\t{dom}") for dom in computer_apes.get_records()]

    print()
    print(
        f"computer_apes.get_record(record_name='@', record_type='NS', data='ns1.digitalocean.com'):"
        f"\n\t{computer_apes.get_record(record_name='@', record_type='NS', data='ns1.digitalocean.com')}"
    )

    """print()
    print(
        f"computer_apes.get_record(record_name='@', record_type='NS'):"
        f"\n\t{computer_apes.get_record(record_name='@', record_type='NS')}"
    )"""
