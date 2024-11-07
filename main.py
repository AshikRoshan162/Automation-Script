import pandas as pd

def CreateScriptMain(table_metadata, table_name, schema):

    '''creates create scripts based on table metadata
    '''

    # standardizing table metadata

    table_meta_data.columns=[x.lower() for x in list(table_meta_data.columns)]

    table_meta_data.rename(columns={"prec":"precision"},inplace=True)

    table_metadata.loc[:,'length']=table_metadata.loc[:,"length"].replace(-1,16777216)

    table_metadata.dropna(how='all',inplace=True)

    data_type_map = {'int':"NUMBER",'smallint':"NUMBER",'char':"VARCHAR","decimal":"NUMBER",'numeric':"NUMBER","bigint":"NUMBER",
                 'datetime':"TIMESTAMP_NTZ","varchar":"VARCHAR","float":"FLOAT",'nvarchar':"VARCHAR","nchar":"VARCHAR",
                 "money":"NUMBER",'tinyint':"NUMBER",'timestamp':"TIMESTAMP_NTZ",
                 'datetime2':"TIMESTAMP_NTZ","smalldatetime":"TIMESTAMP_NTZ",'time':"TIME","sysname":"VARCHAR","varbinary":"VARBINARY"}
    
    table_metadata.type.replace(data_type_map,inplace=True)


    # create script initialization

    create_script = 'create or replace table %s.%s (\n'%(schema,table_name)
    

    for id,row in table_metadata.iterrows():

        column_name = row['column_name']

        data_type = row['type']

        length = row ['length']

        precision = row ['precision']

        scale = row ['scale']

        #nullable_flag = row['nullable']

        if data_type == 'VARCHAR':

            len_conf = '(' + str(int(length) if length.is_integer() else length) + ')'

            #len_conf = '('+str(length)+')'

            #len_conf = ''
        
        elif data_type == 'text':
            
            data_type = 'VARCHAR'
            
            len_conf = ''
        
        elif data_type == 'uniqueidentifier':
            
            data_type = 'VARCHAR'
            
            len_conf = ''
        
        elif data_type == 'bit':
            
            data_type = 'VARBINARY'
            
            len_conf=''
        
        elif data_type == 'VARBINARY':
            
            len_conf=''

        elif data_type == 'NUMBER':
            
            if pd.isnull(precision) and pd.isnull(scale) and pd.notnull(length):
                
                len_conf = '(' + str(int(length)) + ',' + '0' + ')'
            else:
                
                if scale == 0:
                    
                    len_conf = '(' + str(int(precision)) + ',' + str(int(scale)) + ')'
                else:

                    len_conf = '(' + str(precision) + ',' + str(int(scale)) + ')'



        
        elif data_type == 'FLOAT':

            len_conf = ''
        
        elif data_type == 'TIMESTAMP_NTZ':

            len_conf = '(9)'
        
        elif data_type == 'TIME':

            len_conf = '(9)'
        
        else:

            raise Exception('datatype not matching:'+data_type+' for column '+column_name+' table name: '+table_name)
        
        # if nullable_flag == 'no':
        
        #     line_str = '"%s" %s%s NOT NULL,\n'%(column_name,data_type,len_conf)
        
        # else:

        line_str = '%s %s%s,\n'%(column_name.upper(),data_type,len_conf)
        
        create_script+=line_str
    

    create_script = create_script[:-2]+',\nSF_INSERT_TIMESTAMP TIMESTAMP_NTZ(9) \n)'

    return create_script


path_sp_help_workbook = r"D:\eqairestofobjectexcel\Untitled spreadsheet (2).xlsx"

src_name ='EQAIPARTTWO'

df = pd.read_excel(r"D:\eqairestofobjectexcel\Untitled spreadsheet (3).xlsx", sheet_name='Sheet1')

table_mapping_dict = pd.Series(df['STAGING'].values, index=df['Table Name'].str.upper()).to_dict()



df = pd.read_excel(path_sp_help_workbook,engine='openpyxl',sheet_name=None)

count= 0

for table_name, table_meta_data in df.items():

    table_name = table_mapping_dict[table_name.upper()]

    create_script = CreateScriptMain(table_meta_data,table_name,'STAGING')

    script_file = open('scripts/'+src_name+'/'+table_name+'.sql','w')

    script_file.write(create_script)

    script_file.close()

    count+= 1

print(count)