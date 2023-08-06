ns = [{
    "key":"xmlns:osm",
    "val": "www.osm.com"
}]
ft = "osm:events"
ps = [{
    "key": "event_id",
    "val": 1001
},{
    "key": "event_type",
    "val": "slogan"
}]
p = (-3.5, -1)

import trx 

trx.insert_point(
    namespaces=ns,
    featureType=ft,
    props=ps,
    point=p)


import schema_builder as builder

print(trx.delete(
    fid="events.57",
    typeName='osm:events',
    namespaces=ns,
))