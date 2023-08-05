import teradataml as tdml
import re
from tdstone.code import create_code_repository
from tdstone.model import create_model_repository, create_code_model_view
from tdstone.trained_model import create_trained_model_repository, create_code_model_trained_model_view

from tdstone.mapper.feature import create_mapper_feature, create_mapper_feature_description
from tdstone.mapper.training import create_mapper_training, create_mapper_training_description
from tdstone.mapper.scoring import create_mapper_scoring, create_mapper_scoring_description
from tdstone.utils import execute_querydictionary
from tdstone.feature_store import insert_new_process, feature_store
import os



file_list = ['feature_engineering','feature_engineering_reducer','training','scoring']
this_dir, this_filename = os.path.split(__file__)


def mapper_get_dataset_(id_mapper, sto_mapper_description):
    # get the dataset related to a specific mapper
    #
    # id_mapper : int. id of the mapper
    # sto_mapper_description : str. the mapper table nam.

    con = tdml.get_connection()

    # get the dataset table
    return con.execute(f'SEL DATASET_OBJECT FROM {sto_mapper_description}').fetchall()[0][0]

def create_view_on_clause(on_clause_view_name, prepared_dataset_name, mapper_table, mapper_id, model_code_view,
                                   selected_fold, **kwargs):


    # create the "on clause" view for the script table operator query
    #
    # on_clause : name of the "on clause" view to be created
    # prepared_dataset : name of the prepared dataset view or table. a prepared dataset is a view or table that contains
    # the columns STO_ROW_ID (VARCHAR), STO_PARTITION_ID (VARCHAR), STO_FOLD_ID (VARCHAR) at the end in this order.
    # mapper_table : the name of the mapper table that will be used with the script table operator query
    # mapper_id : the id of the mapper to apply for this operation
    # model_code_view : the name of the view containing the code, the parameters and eventually the trained models
    # selected_fold : the fold to be selected, for example

    if type(selected_fold) == 'str':
        filter_ = f"WHERE STO_FOLD_ID = '{selected_fold}'"
    elif type(selected_fold) == 'list':
        tmpstr = "','".join(selected_fold)
        filter_ = f"WHERE STO_FOLD_ID IN ('{tmpstr}')"
    else:
        filter_ = ''

    sql_query = f"""
        REPLACE VIEW {on_clause_view_name} AS
        WITH LEFT_MAPPED_TABLE AS (
            SEL 
                A.*
            ,	ROW_NUMBER() OVER (PARTITION BY A.STO_PARTITION_ID, A.STO_FOLD_ID, MAPPER.ID_MODEL ORDER BY A.STO_ROW_ID) AS STO_FAKE_ROW
            ,	MAPPER.ID_MODEL AS STO_MODEL_ID
            FROM (SEL * FROM {prepared_dataset_name} {filter_}) A
            ,	(CURRENT VALIDTIME SEL * FROM {mapper_table}) MAPPER
            WHERE A.STO_PARTITION_ID = MAPPER.ID_PARTITION
            AND MAPPER.ID = {mapper_id} AND MAPPER.STATUS = 'enabled'
        )
        SEL
            LEFT_MAPPED_TABLE.*
        ,	CASE WHEN LEFT_MAPPED_TABLE.STO_FAKE_ROW = 1 THEN CURRENT_MODELS.CODE_TYPE END AS STO_CODE_TYPE
        ,	CASE WHEN LEFT_MAPPED_TABLE.STO_FAKE_ROW = 1 THEN TRANSLATE(FROM_BYTES(CURRENT_MODELS.CODE, 'base64m') USING UNICODE_TO_LATIN) END AS STO_CODE
        ,	CASE WHEN LEFT_MAPPED_TABLE.STO_FAKE_ROW = 1 THEN REGEXP_REPLACE(REGEXP_REPLACE(CAST(CURRENT_MODELS.ARGUMENTS AS VARCHAR(32000)),'([\r|\t])', ''),'[\s+]', ' ') END AS ARGUMENTS
        FROM
            LEFT_MAPPED_TABLE
        LEFT JOIN (
            CURRENT VALIDTIME SEL
              ID_MODEL as ID
            , CODE_TYPE
            , CODE
            , ARGUMENTS
            FROM
            {model_code_view}
            WHERE CODE_TYPE = 'python class MyModel'
        ) CURRENT_MODELS
        ON LEFT_MAPPED_TABLE.STO_MODEL_ID = CURRENT_MODELS.ID;    
    """

    con = tdml.get_connection()

    con.execute(sql_query)
    print(f'view {on_clause_view_name} successfully created')
    return sql_query

class sto_framework():

    def __init__(self,database,
                 SEARCHUIFDBPATH=re.findall(string=str(tdml.get_context().url),pattern=r'DATABASE=(\w+)')[0],
                 rootname='STO'):
        self.database = database
        self.SEARCHUIFDBPATH = SEARCHUIFDBPATH
        self.code_repository = f'{database}.{rootname}_CODES'
        self.model_repository = f'{database}.{rootname}_MODELS'
        self.code_model_view = f'{database}.{rootname}_MODELS_WITH_CODE'

        self.trained_model_repository = f'{database}.{rootname}_TRAINED_MODELS'
        self.code_model_trained_model_view = f'{database}.{rootname}_TRAINED_MODELS_WITH_MODELS_WITH_CODE'

        self.mapper_feature = f'{database}.{rootname}_MAPPER_FEATURE'
        self.mapper_feature_description = f'{database}.{rootname}_MAPPER_FEATURE_DESCRIPTION'
        self.mapper_training = f'{database}.{rootname}_MAPPER_TRAINING'
        self.mapper_training_description = f'{database}.{rootname}_MAPPER_TRAINING_DESCRIPTION'
        self.mapper_scoring = f'{database}.{rootname}_MAPPER_SCORING'
        self.mapper_scoring_description = f'{database}.{rootname}_MAPPER_SCORING_DESCRIPTION'

    def setup(self):
        sql_queries = {}
        sql_queries['code_repository'] = create_code_repository(self.code_repository)
        sql_queries['model_repository'] = create_model_repository(self.model_repository)
        sql_queries['code_model_view'] = create_code_model_view(self.code_model_view,
                                                                self.code_repository,
                                                                self.model_repository)



        sql_queries['mapper_feature'] = create_mapper_feature(self.mapper_feature)
        sql_queries['mapper_feature_secondary_index'] = f'CREATE INDEX (ID_PARTITION) ON {self.mapper_feature};'
        sql_queries['mapper_feature_description'] = create_mapper_feature_description(self.mapper_feature_description)
        sql_queries['mapper_training'] = create_mapper_training(self.mapper_training)
        sql_queries['mapper_training_description'] = create_mapper_training_description(self.mapper_training_description)
        sql_queries['mapper_scoring'] = create_mapper_scoring(self.mapper_scoring)
        sql_queries['mapper_scoring_description'] = create_mapper_scoring_description(self.mapper_scoring_description)

        sql_queries['trained_model_repository'] = create_trained_model_repository(self.trained_model_repository)
        sql_queries['code_model_trained_model_view'] = create_code_model_trained_model_view(self.code_model_trained_model_view,
                                                                                            self.code_model_view,
                                                                                            self.trained_model_repository)

        execute_querydictionary(sql_queries)

        return

    def clean(self):
        tdml.db_drop_view(self.code_model_trained_model_view.split('.')[1])
        tdml.db_drop_view(self.code_model_view.split('.')[1])
        tdml.db_drop_table(self.code_repository.split('.')[1])
        tdml.db_drop_table(self.model_repository.split('.')[1])
        tdml.db_drop_table(self.mapper_feature.split('.')[1])
        tdml.db_drop_table(self.mapper_feature_description.split('.')[1])
        tdml.db_drop_table(self.mapper_training.split('.')[1])
        tdml.db_drop_table(self.mapper_training_description.split('.')[1])
        tdml.db_drop_table(self.mapper_scoring.split('.')[1])
        tdml.db_drop_table(self.mapper_scoring_description.split('.')[1])


        tdml.db_drop_table(self.trained_model_repository.split('.')[1])
        return

    def install_sto_files(self):

        for filename in file_list:
              tdml.install_file(file_identifier=filename,
                              file_path=os.path.join(this_dir, "data", filename+".py"),
                              file_on_client = True, is_binary = False)

        return

    def remove_sto_file(self):

        for filename in file_list:
            tdml.remove_file(file_identifier=filename,force_remove=True)

        return

    def insert_mapper_feature(self,id_mapper, dataset_object, metadata):
        # insert a new mapper for feature engineering
        #
        # id_mapper : int.
        # dataset_object : str. name of the dataset table or view the mapper applies for.
        # metadata : dict. e.g. '{"author": "Denis Molin", "description": "computation of the "}'

        sql_query = f"""
            INSERT INTO {self.mapper_feature_description}
            (ID, DATASET_OBJECT, METADATA) VALUES
            ({id_mapper}, '{dataset_object}', '{str(metadata).replace("'", '"')}');
            """

        con = tdml.get_connection()

        con.execute(sql_query)

        return

    def PushFile(self):

        con = tdml.get_connection()

        import os
        # set the searchuifdbpath

        query_1 = 'SET SESSION SEARCHUIFDBPATH = "{}"'.format(self.SEARCHUIFDBPATH)
        query_2 = 'DATABASE {}'.format(self.database)
        con.execute(query_1)
        con.execute(query_2)

        # print(queries)
        for filename in file_list:
            try:
                query = "CALL SYSUIF.REMOVE_FILE('{}',1);".format(filename)
                # print(query)
                con.execute(query)
                print(f'File {filename}.py removed in Vantage')
                queries += '\n'
                queries += query
                # print(query)
            except:
                print("the file did not exist")

            if os.name == 'nt':
                # print('windows')
                query = "CALL SYSUIF.INSTALL_FILE('{}','{}','cz!{}')".format(filename,
                                                                             filename+'.py',
                                                                             os.path.join(this_dir, "data", filename+".py").replace("\\", "/").split(
                                                                                 ':')[1])

            else:
                # print('linux')
                query = "CALL SYSUIF.INSTALL_FILE('{}','{}','cz!{}')".format(filename,
                                                                             filename+'.py',
                                                                             os.path.join(this_dir, "data", filename+".py"))

            # print(query)
            con.execute(query)
            print(f'File {filename}.py installed in Vantage')

        return

    def remove_mapper_feature(id_mapper, **kwargs):
        # remove an existing mapper for feature enginieering

        sql_query = f"""
            DELETE {self.mapper_feature_description} 
            WHERE ID = {id_mapper};
            DELETE {self.mapper_feature} 
            WHERE ID = {id_mapper};    
            """

        con = tdml.get_connection()

        con.execute(sql_query, code)

        return

    def mapper_feature_get_dataset(id_mapper,  **kwargs):
        return mapper_get_dataset_(id_mapper, self.mapper_feature_description)

    def map_mapper_feature_insert_all(self,id_mapper, id_model, metadata):
        # attribute the same model corresponding the the id_model to all partitions of the dataset object.
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # id_model : int. id of the model
        # metadata : dict. e.g. {"author" :  "Denis Molin"}

        # get the prepared dataset table/view name
        dataset_object = mapper_feature_get_dataset(id_mapper, self.mapper_feature_description)

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = f"""
        -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
        CURRENT VALIDTIME INSERT INTO {self.mapper_feature}
        (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
        SELECT
            {id_mapper} AS ID
        ,	{id_model} AS ID_MODEL
        ,	ID_PARTITION
        ,	'enabled' AS STATUS
        ,   '{str(metadata).replace("'", '"')}'
        FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
        WHERE ID_PARTITION NOT IN (
            SEL DISTINCT ID_PARTITION FROM {self.mapper_feature}
            WHERE ID = {id_mapper}
            AND ID_MODEL = {id_model}
        )
        ;    
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return

    def map_mapper_feature_insert_some(id_mapper, mapper_dictionary, metadata):
        # map the partitions to the models as described in the mapper dictrionary {sto_partition_id : model_id}
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # mapper_dictionary : dict. {sto_partition_id : model_id}
        # metadata : dict. e.g. {"author" :  "Denis Molin"}

        # get the prepared dataset table/view name
        dataset_object = mapper_feature_get_dataset(id_mapper, self.mapper_feature_description)

        con = tdml.get_connection()

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = []
        for k, v in mapper_dictionary.items():
            sql_insert_query.append(f"""
            -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
            CURRENT VALIDTIME INSERT INTO {self.mapper_feature}
            (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
            SELECT
                {id_mapper} AS ID
            ,	{v} AS ID_MODEL
            ,	{k} AS ID_PARTITION
            ,	'enabled' AS STATUS
            ,   '{str(metadata).replace("'", '"')}'
            FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
            WHERE ID_PARTITION NOT IN (
                SEL DISTINCT ID_PARTITION FROM {self.mapper_feature}
                WHERE ID = {id_mapper}
                AND ID_MODEL = {v}
            )
            AND ID_PARTITION = {k}
            ;    
            """)

        con.execute(''.join(sql_insert_query))

        return

    def insert_code(self, code_id, filename, metadata, model_type='python class MyModel'):
        # insert the code in the sto_code_repository table
        #
        # code_id : int. the unique ID of the repo.
        # sto_code_repository : str. the name of the sto code repository table
        # filename : the filename of the python file containing the code
        # metadata : json format. e.g.'{"author": "Denis Molin"}'
        # model_type : str. default is 'python class MyModel'

        sql_query = f"""
        CURRENT VALIDTIME INSERT INTO {self.code_repository}
        (ID, CODE_TYPE, CODE, METADATA)
         VALUES
        ({code_id}, '{model_type}', ?, '{str(metadata).replace("'", '"')}');
        """

        with open(filename, 'r') as file:
            code = file.read()

        con = tdml.get_connection()

        con.execute(sql_query, code)

        return sql_query

    def remove_code(self,code_id, **kwargs):
        # remove a deployed code

        sql_query = f"""
        DELETE {self.code_repository} WHERE ID = {code_id};
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return sql_query

    def update_code(self,code_id,  filename, **kwargs):
        # update an existing code

        sql_query = f"""
        CURRENT VALIDTIME UPDATE {self.code_repository}
        SET CODE   = ?
        WHERE ID = {code_id};
        """

        with open(filename, 'r') as file:
            code = file.read()

        con = tdml.get_connection()

        con.execute(sql_query, code.encode())

        return sql_query

    def insert_model(self,model_id, code_id, arguments, metadata):
        # insert a new model
        #
        # model_id : int. id of the new model
        # code_id : id of an existing code
        # arguments : json. two fields: sto_parameters and model_parameters
        # metadata : json. e.g. {"author": "Denis Molin"}

        sql_insert_query = f"""
        CURRENT VALIDTIME INSERT INTO {self.model_repository}
        (ID, ID_CODE, ARGUMENTS, METADATA) VALUES
        ({model_id}, {code_id}, '{str(arguments).replace("'", '"')}', '{str(metadata).replace("'", '"')}');    
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return sql_insert_query

    def remove_model(self,model_id,  **kwargs):
        # remove a model

        sql_query = f"""
        DELETE {self.model_repository} WHERE ID = {model_id};
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return sql_query

    def update_model_arguments(self,model_id, arguments,  **kwargs):
        # update the arguements of an existing model

        sql_query = f"""
        CURRENT VALIDTIME UPDATE {self.model_repository}
        SET ARGUMENTS = '{str(arguments).replace("'", '"')}'
        WHERE ID = {model_id};
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return sql_query

    def get_codes(self):
        return tdml.DataFrame(tdml.in_schema(self.code_repository.split('.')[0],
                                             self.code_repository.split('.')[1]))

    def get_models(self):
        return tdml.DataFrame(tdml.in_schema(self.code_model_view.split('.')[0],
                                             self.code_model_view.split('.')[1]))

    def get_current_codes(self):
        query = f"""
        CURRENT VALIDTIME
        SELECT * FROM {self.code_repository}
        """
        return tdml.DataFrame.from_query(query)

    def get_current_models(self):
        query = f"""
        CURRENT VALIDTIME
        SELECT * FROM {self.code_model_view}
        """
        return tdml.DataFrame.from_query(query)

    #################################### MAPPER FEATURE ENGINEERING ###################################
    def insert_mapper_feature(self,id_mapper, dataset_object, metadata,  **kwargs):
        # insert a new mapper for feature engineering
        #
        # id_mapper : int.
        # dataset_object : str. name of the dataset table or view the mapper applies for.
        # metadata : dict. e.g. '{"author": "Denis Molin", "description": "computation of the "}'

        sql_query = f"""
        INSERT INTO {self.mapper_feature_description}
        (ID, DATASET_OBJECT, METADATA) VALUES
        ({id_mapper}, '{dataset_object}', '{str(metadata).replace("'", '"')}');
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return sql_query

    def remove_mapper_feature(self,id_mapper, **kwargs):
        # remove an existing mapper for feature enginieering

        sql_query = f"""
        DELETE {self.mapper_feature_description} 
        WHERE ID = {id_mapper};
        DELETE {self.mapper_feature} 
        WHERE ID = {id_mapper};    
        """

        con = tdml.get_connection()

        con.execute(sql_query, code)

        return sql_query

    def mapper_get_dataset_(id_mapper, mapper_description):
        # get the dataset related to a specific mapper
        #
        # id_mapper : int. id of the mapper
        # sto_mapper_description : str. the mapper table nam.

        con = tdml.get_connection()

        # get the dataset table
        return con.execute(f'SEL DATASET_OBJECT FROM {mapper_description}').fetchall()[0][0]

    def mapper_feature_get_dataset(self,id_mapper, **kwargs):

        return mapper_get_dataset_(id_mapper, self.mapper_feature_description)

    def map_mapper_feature_insert_all(self, id_mapper, id_model, metadata):
        # attribute the same model corresponding the the id_model to all partitions of the dataset object.
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # id_model : int. id of the model
        # sto_mapper_feature : str. name of the mapper feature table
        # metadata : dict. e.g. {"author" :  "Denis Molin"}
        # sto_mapper_feature_description : str. name of the mapper feature description table

        # get the prepared dataset table/view name
        dataset_object = self.mapper_feature_get_dataset(id_mapper)

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = f"""
        -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
        CURRENT VALIDTIME INSERT INTO {self.mapper_feature}
        (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
        SELECT
            {id_mapper} AS ID
        ,	{id_model} AS ID_MODEL
        ,	ID_PARTITION
        ,	'enabled' AS STATUS
        ,   '{str(metadata).replace("'", '"')}'
        FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
        WHERE ID_PARTITION NOT IN (
            SEL DISTINCT ID_PARTITION FROM {self.mapper_feature}
            WHERE ID = {id_mapper}
            AND ID_MODEL = {id_model}
        )
        ;    
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return sql_insert_query

    def map_mapper_feature_insert_some(self, id_mapper, mapper_dictionary, metadata):
        # map the partitions to the models as described in the mapper dictrionary {sto_partition_id : model_id}
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # mapper_dictionary : dict. {sto_partition_id : model_id}
        # sto_mapper_feature : str. name of the mapper feature table
        # metadata : dict. e.g. {"author" :  "Denis Molin"}
        # sto_mapper_feature_description : str. name of the mapper feature description table

        # get the prepared dataset table/view name
        dataset_object = self.mapper_feature_get_dataset(id_mapper)

        con = tdml.get_connection()

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = []
        for k, v in mapper_dictionary.items():
            sql_insert_query.append(f"""
            -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
            CURRENT VALIDTIME INSERT INTO {self.mapper_feature}
            (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
            SELECT
                {id_mapper} AS ID
            ,	{v} AS ID_MODEL
            ,	{k} AS ID_PARTITION
            ,	'enabled' AS STATUS
            ,   '{str(metadata).replace("'", '"')}'
            FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
            WHERE ID_PARTITION NOT IN (
                SEL DISTINCT ID_PARTITION FROM {self.mapper_feature}
                WHERE ID = {id_mapper}
                AND ID_MODEL = {v}
            )
            AND ID_PARTITION = {k}
            ;    
            """
                                    )

        con.execute(''.join(sql_insert_query))

        return sql_insert_query

    def get_mapper_feature(self):
        return tdml.DataFrame(tdml.in_schema(self.mapper_feature.split('.')[0],
                                             self.mapper_feature.split('.')[1]))

    def get_current_mapper_feature(self):
        query = f"""
         CURRENT VALIDTIME
         SELECT * FROM {self.mapper_feature}
         """
        return tdml.DataFrame.from_query(query)

    def get_current_models(self):
        query = f"""
         CURRENT VALIDTIME
         SELECT * FROM {self.code_model_view}
         """
        return tdml.DataFrame.from_query(query)
    #################################### MAPPER TRAINING ###################################
    def insert_mapper_training(self,id_mapper, dataset_object, metadata,  **kwargs):
        # insert a new mapper for training engineering
        #
        # id_mapper : int.
        # dataset_object : str. name of the dataset table or view the mapper applies for.
        # metadata : dict. e.g. '{"author": "Denis Molin", "description": "computation of the "}'

        sql_query = f"""
        INSERT INTO {self.mapper_training_description}
        (ID, DATASET_OBJECT, METADATA) VALUES
        ({id_mapper}, '{dataset_object}', '{str(metadata).replace("'", '"')}');
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return

    def remove_mapper_training(self,id_mapper, **kwargs):
        # remove an existing mapper for training enginieering

        sql_query = f"""
        DELETE {self.mapper_training_description} 
        WHERE ID = {id_mapper};
        DELETE {self.mapper_training} 
        WHERE ID = {id_mapper};    
        """

        con = tdml.get_connection()

        con.execute(sql_query)

        return

    def mapper_training_get_dataset(self,id_mapper, **kwargs):

        return mapper_get_dataset_(id_mapper, self.mapper_training_description)

    def map_mapper_training_insert_all(self, id_mapper, id_model, metadata):
        # attribute the same model corresponding the the id_model to all partitions of the dataset object.
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # id_model : int. id of the model
        # sto_mapper_training : str. name of the mapper training table
        # metadata : dict. e.g. {"author" :  "Denis Molin"}
        # sto_mapper_training_description : str. name of the mapper training description table

        # get the prepared dataset table/view name
        dataset_object = self.mapper_training_get_dataset(id_mapper)

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = f"""
        -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
        CURRENT VALIDTIME INSERT INTO {self.mapper_training}
        (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
        SELECT
            {id_mapper} AS ID
        ,	{id_model} AS ID_MODEL
        ,	ID_PARTITION
        ,	'enabled' AS STATUS
        ,   '{str(metadata).replace("'", '"')}'
        FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
        WHERE ID_PARTITION NOT IN (
            SEL DISTINCT ID_PARTITION FROM {self.mapper_training}
            WHERE ID = {id_mapper}
            AND ID_MODEL = {id_model}
        )
        ;    
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return

    def map_mapper_training_insert_some(self, id_mapper, mapper_dictionary, metadata):
        # map the partitions to the models as described in the mapper dictrionary {sto_partition_id : model_id}
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # mapper_dictionary : dict. {sto_partition_id : model_id}
        # sto_mapper_training : str. name of the mapper training table
        # metadata : dict. e.g. {"author" :  "Denis Molin"}
        # sto_mapper_training_description : str. name of the mapper training description table

        # get the prepared dataset table/view name
        dataset_object = self.mapper_training_get_dataset(id_mapper)

        con = tdml.get_connection()

        # insert query of partition that are not attributed yet to this model
        sql_insert_query = []
        for k, v in mapper_dictionary.items():
            sql_insert_query.append(f"""
            -- ADD A NEW MAPPER ON ALL CURVES APPLY MODEL 
            CURRENT VALIDTIME INSERT INTO {self.mapper_training}
            (ID, ID_MODEL, ID_PARTITION, STATUS, METADATA)
            SELECT
                {id_mapper} AS ID
            ,	{v} AS ID_MODEL
            ,	'{k}' AS ID_PARTITION
            ,	'enabled' AS STATUS
            ,   '{str(metadata).replace("'", '"')}'
            FROM (SEL DISTINCT STO_PARTITION_ID AS ID_PARTITION FROM {dataset_object}) A
            WHERE ID_PARTITION NOT IN (
                SEL DISTINCT ID_PARTITION FROM {self.mapper_training}
                WHERE ID = {id_mapper}
                AND ID_MODEL = {v}
            )
            AND ID_PARTITION = '{k}'
            ;    
            """
                                    )

        con.execute(''.join(sql_insert_query))

        return


    def get_mapper_training(self):
        return tdml.DataFrame(tdml.in_schema(self.mapper_training.split('.')[0],
                                             self.mapper_training.split('.')[1]))

    def get_current_mapper_training(self):
        query = f"""
          CURRENT VALIDTIME
          SELECT * FROM {self.mapper_training}
          """
        return tdml.DataFrame.from_query(query)

    def map_mapper_training_update_status_all(self, id_mapper, new_status):
        # attribute the same model corresponding the the id_model to all partitions of the dataset object.
        # Note that the dataset object is already linked to the mapper.
        #
        # id_mapper : int. id of the mapper
        # id_model : int. id of the model
        # sto_mapper_training : str. name of the mapper training table
        # metadata : dict. e.g. {"author" :  "Denis Molin"}
        # sto_mapper_training_description : str. name of the mapper training description table

        sql_query = f"""
         CURRENT VALIDTIME UPDATE {self.mapper_training}
         SET STATUS   = '{new_status}'
         WHERE ID = {id_mapper}
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return

    def insert_new_training_process(self,id_process, final_view, on_clause,
                                    prepared_dataset, id_mapper, feature_store, **kwargs):


        process_type = 'sto_training'
        mapper_table = self.mapper_training
        model_code_view = self.code_model_view
        process_catalog = feature_store.process_catalog
        sto_database = self.SEARCHUIFDBPATH

        insert_new_process(id_process, process_type, final_view, on_clause,
                           prepared_dataset, mapper_table, id_mapper, model_code_view,
                           process_catalog, sto_database)

        return

    def create_training_process(self, id_process, prepared_dataset_name,  id_mapper, feature_store,
                              selected_fold='train', **kwargs):

        on_clause_view_name = f"{self.database}.V_STO_TRAINING_{prepared_dataset_name.split('.')[1]}"
        mapper_table = self.mapper_training
        code_model_view = self.code_model_view

        create_view_on_clause(on_clause_view_name, prepared_dataset_name, mapper_table, id_mapper, code_model_view,
                                  selected_fold, **kwargs)

        new_training_process = {
            'id_process': id_process,
            'final_view': '',
            'on_clause': on_clause_view_name,
            'prepared_dataset': prepared_dataset_name,
            'id_mapper': id_mapper,
            'feature_store': feature_store
        }
        self.insert_new_training_process(**new_training_process)

        return

    def run_training_process(self, id_process, feature_store):

        process_param = feature_store.get_process_parameters(id_process)

        on_clause = process_param['on_clause']

        temporary_table = f'{self.database}.TEMPORARY_MODEL_TRAINING_RESULTS'

        sql_queries = {}

        sql_queries['session'] = f'SET SESSION SEARCHUIFDBPATH = "{self.SEARCHUIFDBPATH}";'

        sql_queries['create_temporary_table'] = f"""
                    -- CREATE VOLATILE TABLE
                    CREATE TABLE {temporary_table}
                    (
                        ID_PROCESS BIGINT
                    ,   ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
                    ,   ID_MODEL BIGINT
                    ,   ID_TRAINED_MODEL VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
                    ,   MODEL_TYPE VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
                    ,   STATUS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
                    ,   TRAINED_MODEL CLOB
                    )
                    PRIMARY INDEX (ID_PARTITION);
                    """

        sql_queries['insert_results'] = f"""
                    -- INSERT THE RESULTS
                    INSERT INTO {temporary_table}
                    SELECT 
                        {id_process} as ID_PROCESS
                    ,   ID_PARTITION
                    ,   ID_MODEL
                    ,   ID_TRAINED_MODEL
                    ,   MODEL_TYPE
                    ,   STATUS
                    ,   TRAINED_MODEL
                    FROM Script(
                        ON {on_clause}
                        PARTITION BY
                            STO_PARTITION_ID
                        ,	STO_MODEL_ID
                        ORDER BY STO_FAKE_ROW
                        SCRIPT_COMMAND(
                            'tdpython3 ./{self.SEARCHUIFDBPATH}/training.py;'
                        )
                        RETURNS(
                                    'ID_PARTITION VARCHAR(2000)'
                                ,	'ID_MODEL BIGINT'
                                ,	'ID_TRAINED_MODEL VARCHAR(2000)'
                                ,	'MODEL_TYPE VARCHAR(2000)'
                                ,	'STATUS VARCHAR(20000)'
                                ,	'TRAINED_MODEL CLOB'
                        )
                        CHARSET('LATIN')
                    ) AS d;
                    """

        sql_queries['insert_new_trained_models'] = f"""
                    -- INSERT NEW MODELS
                    CURRENT VALIDTIME INSERT INTO {self.trained_model_repository}
                    (ID_PROCESS, ID_PARTITION, ID_MODEL, ID_TRAINED_MODEL, MODEL_TYPE, STATUS, TRAINED_MODEL)
                    SELECT
                          RESULTS.ID_PROCESS
                        , RESULTS.ID_PARTITION
                        , RESULTS.ID_MODEL
                        , RESULTS.ID_TRAINED_MODEL
                        , RESULTS.MODEL_TYPE
                        , RESULTS.STATUS
                        , RESULTS.TRAINED_MODEL
                    FROM {temporary_table} RESULTS
                    LEFT JOIN {self.trained_model_repository} STORED_RESULTS
                    ON RESULTS.ID_PROCESS = STORED_RESULTS.ID_PROCESS AND RESULTS.ID_PARTITION = STORED_RESULTS.ID_PARTITION
                    AND RESULTS.ID_MODEL = STORED_RESULTS.ID_MODEL
                    WHERE STORED_RESULTS.ID_PROCESS IS NULL
                    AND RESULTS.ID_TRAINED_MODEL <> 'STO error';
                    """

        sql_queries['update_existing_trained_models'] = f"""
                    -- UPDATE EXISTING MODELS
                    CURRENT VALIDTIME UPDATE {self.trained_model_repository} 
                    FROM
                    (
                    CURRENT VALIDTIME SELECT
                          RESULTS.ID_PROCESS
                        , RESULTS.ID_PARTITION
                        , RESULTS.ID_MODEL
                        , RESULTS.ID_TRAINED_MODEL
                        , RESULTS.MODEL_TYPE
                        , RESULTS.STATUS
                        , RESULTS.TRAINED_MODEL
                    FROM {temporary_table} RESULTS
                    LEFT JOIN {self.trained_model_repository} STORED_RESULTS
                    ON RESULTS.ID_PROCESS = STORED_RESULTS.ID_PROCESS AND RESULTS.ID_PARTITION = STORED_RESULTS.ID_PARTITION
                    AND RESULTS.ID_MODEL = STORED_RESULTS.ID_MODEL
                    WHERE STORED_RESULTS.ID_PROCESS IS NOT NULL
                    AND RESULTS.ID_TRAINED_MODEL <> 'STO error'
                    ) UPDATED_MODELS
                    SET 
                        ID_TRAINED_MODEL   = UPDATED_MODELS.ID_TRAINED_MODEL,
                        MODEL_TYPE         = UPDATED_MODELS.MODEL_TYPE,
                        STATUS             = UPDATED_MODELS.STATUS,
                        TRAINED_MODEL      = UPDATED_MODELS.TRAINED_MODEL                    
                    WHERE
                        {self.trained_model_repository}.ID_PROCESS = UPDATED_MODELS.ID_PROCESS
                    AND
                        {self.trained_model_repository}.ID_PARTITION = UPDATED_MODELS.ID_PARTITION
                    AND
                        {self.trained_model_repository}.ID_MODEL = UPDATED_MODELS.ID_MODEL;
                    """

        sql_queries['drop_temporary_table'] = f'DROP TABLE {temporary_table};'

        con = tdml.get_connection()

        if True:
            try:
                con.execute(sql_queries['drop_temporary_table'])
                con.execute(sql_queries['create_temporary_table'])
            except Exception as e:
                con.execute(sql_queries['create_temporary_table'])
            con.execute(sql_queries['session'])
            con.execute(sql_queries['insert_results'])
        if True:
            con.execute(sql_queries['insert_new_trained_models'])
            con.execute(sql_queries['update_existing_trained_models'])
            con.execute(sql_queries['drop_temporary_table'])

        return

    def list_trained_models(self,with_models = False, with_arguments = False):

        df = tdml.DataFrame(tdml.in_schema(self.trained_model_repository.split('.')[0],
                                           self.trained_model_repository.split('.')[1]))

        columns = df.columns
        columns = [x for x in columns if x != 'ValidPeriod']
        if with_models == False:
            columns = [x for x in columns if x != 'TRAINED_MODEL']
        if with_arguments == False:
            columns = [x for x in columns if x != 'STATUS']

        return df.select(columns)

    def list_current_trained_models(self,with_models = False, with_arguments = False):

        df = tdml.DataFrame(tdml.in_schema(self.trained_model_repository.split('.')[0],
                                           self.trained_model_repository.split('.')[1]))

        columns = df.columns
        columns = [x for x in columns if x != 'ValidPeriod']
        if with_models == False:
            columns = [x for x in columns if x != 'TRAINED_MODEL']
        if with_arguments == False:
            columns = [x for x in columns if x != 'STATUS']

        return tdml.DataFrame.from_query(f"""
                        CURRENT VALIDTIME
                        SELECT
                            {','.join(columns)}
                        FROM {self.trained_model_repository}
                    """)
