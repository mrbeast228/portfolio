select i.itemid as item_id,
       i.name as item_name,
       i.hostid as host_id,
       h.host,
       g.groupid as host_group_id,
       hg.name as host_group
       from items i
       join hosts h on i.hostid = h.hostid
       join hosts_groups g on h.hostid = g.hostid
       join hstgrp hg on hg.groupid = g.groupid
       where exists (select * from item_rtdata r
                                              where i.itemid = r.itemid
                                              and r.state = 1);
