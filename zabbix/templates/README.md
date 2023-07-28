# Zabbix templates
This directory contains my self-developed Zabbix templates for real cases

## Zabbix monitoring template for Juniper E1
This Zabbix template can help you to work with Juniper E1

### Requirments
+ Zabbix Server 6.4+ with SNMP support

### Usage
1. Deploy your Zabbix server
2. Import template `OSPF-SNMP` from `juniper_ospf_neighbours_discovery_template.xml` file
3. Create host with any name, connect `OSPF-SNMP` to it, and add SNMP interface with IP address and port where Juniper E1 is accessible
4. Wait until `SNMP` box become green and LLD finishes his work
5. Now you can monitor your network neighbours and their states via Juniper E1
