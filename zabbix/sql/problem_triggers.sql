select distinct on (t.triggerid)
       t.triggerid as trigger_id,
       t.description as trigger,
       e.severity,
       f.itemid as item_id,
       i.name as item,
       i.hostid as host_id,
       h.host,
       g.groupid as host_group_id,
       hg.name as host_group
       from triggers t
       join functions f on f.triggerid = t.triggerid
       join items i on f.itemid = i.itemid
       join hosts h on h.hostid = i.hostid
       join hosts_groups g on g.hostid = h.hostid
       join hstgrp hg on hg.groupid = g.groupid
       join events e on e.objectid = t.triggerid
       where t.value = 1 and e.source = 0;
