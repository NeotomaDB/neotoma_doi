from neotomadoi import neotomaDOI, neo_connect
from dotenv import load_dotenv
from pytest import raises, warns
import psycopg2
import psycopg2.extras
from random import choice


def test_freeze_data():
    load_dotenv()
    con = neo_connect()
    unfrozen_query = """
        SELECT ds.datasetid
        FROM ndb.datasets AS ds
        LEFT OUTER JOIN doi.frozen AS fz ON fz.datasetid = ds.datasetid
        WHERE fz.datasetid IS null
		  AND ds.datasettypeid > 1;"""
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(unfrozen_query)
                    frozen_result = cur.fetchall()
    dsid = choice(frozen_result)[0]
    new_doi = neotomaDOI(datasetid = dsid, defaults = 'neotomadoi.yaml')
    with raises(Exception, match="missing critical metadata"):
        new_doi.update()
    new_doi.freeze_data(con)
    new_doi.update()
    # This is the one that really depends on there being a data object.
    assert isinstance(new_doi.data.get('sizes'), list)
    with warns(UserWarning):
            new_doi.freeze_data(con)

def test_unfreeze_freeze():
    load_dotenv()
    con = neo_connect()
    delete_frozen = """
    DELETE FROM doi.frozen
    WHERE datasetid = 16;"""
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(delete_frozen)
    con.commit()
    new_doi = neotomaDOI(datasetid = 16, defaults = 'neotomadoi.yaml')
    with raises(ValueError, match= 'missing critical'):
        new_doi.update()
    new_doi.freeze_data(con)
    new_doi.update()
