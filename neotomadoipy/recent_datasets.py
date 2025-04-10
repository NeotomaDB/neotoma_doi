from psycopg2 import connect

def recent_datasets(conn:connect, interval:str = '2 days')->list:
  """_Obtain all datasets without DOIs that have been minted over a defined period_

  Args:
      conn (connect): _A valid connection to the Neotoma Database server_
      interval (str, optional): _A valid interval period used in Postgres._. Defaults to '2 days'.

  Returns:
      list: _An array of unique datasetids from Neotoma for datasets without DOIs._
  """  
  query = '''
    SELECT DISTINCT ds.datasetid
	FROM ndb.datasets as ds
	  LEFT OUTER JOIN       ndb.datasetdoi AS dsdoi ON  ds.datasetid = dsdoi.datasetid
	  INNER JOIN    ndb.datasetsubmissions AS dss   ON dss.datasetid = ds.datasetid
    WHERE ds.datasetid NOT IN (SELECT datasetid FROM doi.frozen) AND
      	  ds.recdatecreated < NOW() - INTERVAL %(interval)s AND
		  dss.submissiondate < NOW() - INTERVAL %(interval)s AND
          ds.datasettypeid > 1;
    '''
  with conn.cursor() as cur:
    try:
      records = cur.execute(query, {'interval': interval})
      datasets = list(set([res[0] for res in cur]))
    except Exception as e:
      conn.rollback()
      print(e)
  return datasets
