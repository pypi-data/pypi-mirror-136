import json
import snowflake.connector
import pandas as pd
import calendar
import os
import datetime
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from snowflake.connector.pandas_tools import write_pandas
import snowflake


def get_credentials_snowflake(path='/Users/intelcom/Desktop/config_snowflake.json'):
	"""return json file with credentials"""
	with open(path) as json_file:
		credentials = json.load(json_file)

	#credentials['sf_role'] = 'ANALYST_OPS'
	#credentials['sf_warehouse'] = 'DEV_COMPUTE'
	credentials['sf_database'] = 'DATASTORE_SIMULATOR'
	credentials['sf_schema'] = 'RAW'
	
	return credentials


def get_data_snowflake(sql_query, credentials):
	"""return dataframe with data"""

	ctx = snowflake.connector.connect(
	    user = credentials.get('sf_user'),
	    password = credentials.get('sf_password'),
	    account = credentials.get('sf_account')
	    )

	print('Loading dataset...')
	cur = ctx.cursor()

	try:
		cur.execute(sql_query)
		# Get data as a pandas dataframe
		data = cur.fetch_pandas_all()
		data.columns = data.columns.str.lower()
		print('Dataset shape {} loaded'.format(data.shape))
	finally:
	    cur.close()
	    
	ctx.close()

	return data


def create_table_snowflake(dataframe, sf_config, sf_table_name):
    """ upload dataframe into snowflake
    inspiration https://calogica.com/sql/snowflake/python/2019/06/12/snowflake-pandas.html
    """
    
    # Create Snowflake engine 
    engine = create_engine(URL(
        user = sf_config.get('sf_user'),
        account = sf_config.get('sf_account'),
        password = sf_config.get('sf_password'),
        role = sf_config.get('sf_role'),
        warehouse = sf_config.get('sf_warehouse'),
        database = sf_config.get('sf_database'),
        schema = sf_config.get('sf_schema')))
    
    print('Snowflake engine created')
    
    # Create Snowflake Connection
    with engine.connect() as connection:
        
        try:
            # Save dataframe locally
            print('Uploading dataset to Snowflake...')
            filename = f"{sf_table_name}.csv"
            file_path = os.path.abspath(filename)
            dataframe.to_csv(file_path, header=False, index=False)
            
            # Create table in Snowflake
            dataframe.head(0).to_sql(name=sf_table_name, con=connection, if_exists="replace", index=False)    
            
            # Put file in S3 stage and copy file to table
            connection.execute(f"put file://{file_path}* @%{sf_table_name}")
            connection.execute(f"copy into {sf_table_name}")
            print('Sucessufully uploaded {} rows into : {}.{}.{}'.format(dataframe.shape[0], sf_config.get('sf_database'), sf_config.get('sf_schema'), sf_table_name.upper()))
        
        except Exception as error:
            print(error)
            
        finally:
            os.remove(file_path)


def upload_dataframe_snowflake(dataframe, sf_config, sf_table_name = 'ACTUALS'):
    
    cnx = snowflake.connector.connect(
    user = sf_config.get('sf_user'),
    account = sf_config.get('sf_account'),
    password = sf_config.get('sf_password'),
    role = sf_config.get('sf_role'),
    warehouse = sf_config.get('sf_warehouse'),
    database = sf_config.get('sf_database'),
    schema = sf_config.get('sf_schema'))
    
    
    try: 
        print('Uploading dataset to Snowflake...')
        dataframe.columns = dataframe.columns.str.upper()
        success, nchunks, nrows, _ = write_pandas(cnx, 
                                                  dataframe, 
                                                  table_name = sf_table_name,)
        if success:
            print('Sucessufully uploaded {} rows into : {}.{}.{}'.format(nrows, sf_config.get('sf_database'), sf_config.get('sf_schema'), sf_table_name.upper()))
    
    except Exception as error:
        print('error :', error)
        



def get_parcels_delivered(start_date, end_date, credentials):
	"""return dataframe with parcels_delivered"""

	sql_query = f"""
	SELECT
	 D.TRACKING_ID
	 , DATE(D.DELIVERED_DATE) AS RUN
	 , IFF(C.TRACKING_ID IS NULL, I.CLIENT_CODE, C.CLIENT_CODE) AS CLIENT
	 , IFF(C.TRACKING_ID IS NULL, I.STATION_CODE, REGEXP_SUBSTR(C.DELIV_SHIPSORT_LNH_ROUTE, '[A-Z]+$')) AS DELIVERY_STATION
	 , IFF(C.TRACKING_ID IS NULL, I.INVOICED_PRICE_CODE, C.COMPENSATION_PRICE_CODE) AS COMP_ZONE
	 , I.INVOICED_PRICE_CODE as INV_ZONE
	 , C.VENDOR_ID as VENDOR_ID
	 , CASE WHEN D.SIGNATURE_STATUS = 'NOT SIGNED' THEN 0 WHEN D.SIGNATURE_STATUS = 'SIGNED' THEN 1 ELSE 'Error' END AS HAS_SIGNATURE
	 , I.ACTUAL_WEIGHT_LB AS WEIGHT_LB -- QUEL POID CHOISIR ?
	 , A.PACKAGE_VOLUME_FT3 AS VOLUME_FT3
	 , CAST(I.DISTRIBUTION_ALLOCATION_AMOUNT AS FLOAT) as DISTRIBUTION_PRICE
	 , CAST(I.CALCULATED_UNIT_PRICE as FLOAT) as UNIT_PRICE
	 , CAST(IFF (C.TRACKING_ID IS NULL, I.NATURAL_PAYOUT_COST_PRECALCULATED,C.NATURAL_PAYOUT_COST) as FLOAT) as DRIVER_PAYOUT
	 --, IFF (C.TRACKING_ID IS NULL,1,0) AS PRECAL_COMPENSATION_FLAG
	FROM
	  "ANALYTICS_OPS"."ANALYTICS"."DELIV_PACKAGE_DELIVERED_STAT" AS D
	LEFT JOIN
	  "ANALYTICS_FINANCE_OPS"."ANALYTICS"."COMPENSATION" AS C
	ON
	  D.TRACKING_ID = C.TRACKING_ID
	INNER JOIN
	  "ANALYTICS_FINANCE_OPS"."ANALYTICS"."INVOICING" AS I
	 ON
	  D.TRACKING_ID = I.TRACKING_ID
	INNER JOIN
	  "ANALYTICS_OPS"."ANALYTICS"."DELIV_PACKAGE_INFO" AS A
	ON
	  D.TRACKING_ID = A.TRACKING_ID
	WHERE
	  (DATE(D.DELIVERED_DATE) BETWEEN '{start_date}' AND '{end_date}')
	"""

	delivered_parcels = get_data_snowflake(sql_query, credentials)

	try:
		delivered_parcels['weight_lb'] = delivered_parcels['weight_lb'].str.replace(',','.')
	except: 
		pass

	delivered_parcels['sorting_price'] = 0
	delivered_parcels['linehaul_price'] = 0

	#Reduce memory footprint 
	dtypes = {
	    'tracking_id': 'object',
	    'run':'category',
	    'client': 'category',
	    'delivery_station': 'category',
	    'comp_zone': 'category',
	    'inv_zone':'category',
	    'vendor_id':'category',
	    'has_signature':'int8',
	    'weight_lb': 'float32',
	    'volume_ft3': 'float32',
	    'distribution_price':'float32',
	    'unit_price':'float32',
	    'driver_payout':'float32',
	    'sorting_price': 'float32', 
	    'linehaul_price': 'float32'}

	columns = list(dtypes.keys())

	for column in columns:
	    delivered_parcels[column] = delivered_parcels[column].astype(dtypes[column])

	return delivered_parcels

