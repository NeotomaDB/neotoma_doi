import psycopg2
import psycopg2.extras
from shapely import wkt

def neo_location(con:psycopg2.connect, self)->object:

    geolocation = {'geoLocationPlace': None}
    # Using 0.01 as the precision to give less precise coordinate box.
    loc_query = """
        SELECT
            ST_AsText(ST_extent(st_buffer(st.geog::geometry, 0.01))) AS polygon
        from ndb.sites as st
        inner join ndb.collectionunits as cu on cu.siteid = st.siteid
        inner join ndb.datasets as ds on ds.collectionunitid = cu.collectionunitid
        where ds.datasetid = %(datasetid)s;"""
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(loc_query, {'datasetid': self.datasetid})
        response = cur.fetchone()
    polygon = wkt.loads(response[0])
    coordinates = list(polygon.exterior.coords)

    geolocation['geoLocationBox'] = {'westBoundLongitude': min([i[0] for i in coordinates]),
                                     'eastBoundLongitude': max([i[0] for i in coordinates]),
                                     'southBoundLatitude': min([i[1] for i in coordinates]),
                                     'northBoundLatitude': max([i[1] for i in coordinates])}
    
    place_query = """
        select
            st.sitename,
            gadm.name_0,
            gadm.name_1,
            gadm.name_2,
            gadm.name_3,
            gadm.name_4,
            gadm.name_5
            from ndb.sites as st
            inner join ndb.collectionunits as cu on cu.siteid = st.siteid
            inner join ndb.datasets as ds on ds.collectionunitid = cu.collectionunitid
            inner join ap.gadm as gadm on st_contains(gadm.shape, st.geog::geometry)
            where ds.datasetid = %(datasetid)s;"""

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(place_query, {'datasetid': self.datasetid})
        response = cur.fetchone()
    
    if response is None:
        place_query = """
        with dsset as (
            SELECT
            st.geog, st.sitename
            from ndb.sites as st
            inner join ndb.collectionunits as cu on cu.siteid = st.siteid
            inner join ndb.datasets as ds on ds.collectionunitid = cu.collectionunitid
            where ds.datasetid = %(datasetid)s
            LIMIT 1
        )
        select
        st.sitename,
            gadm.name_0,
            gadm.name_1,
            gadm.name_2,
            gadm.name_3,
            gadm.name_4,
            gadm.name_5
        from dsset as st
        cross join lateral (
        select  gadm.name_0,
                gadm.name_1,
                gadm.name_2,
                gadm.name_3,
                gadm.name_4,
                gadm.name_5,
                gadm.shape::geometry <-> st.geog::geometry as dist
        from ap.gadm as gadm
        order by dist
        limit 1) gadm;"""

        with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(place_query, {'datasetid': self.datasetid})
            response = cur.fetchone()
        if response is None:
            raise ValueError("This site cannot return a close neighbour.")
            
    response_loc = 'Site name: ' + response[0] + '; ' + '; '.join(reversed([i for i in response[1:] if i]))
    geolocation['geoLocationPlace'] = response_loc
    return [ geolocation ]
