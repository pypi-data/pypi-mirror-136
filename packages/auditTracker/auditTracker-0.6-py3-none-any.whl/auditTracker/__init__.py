from fastavro import writer, reader, parse_schema
import os, datetime, ast, urllib
import pandas as pd
import pyrebase



class Tracker:
  VALUE_CREATED = '@inserted'
  VALUE_UPDATED = '@updated'
  VALUE_DELETED = '@deleted'
  SEPARATOR = '.'
  AVRO_EXTENSION = 'avro'
  JSON_EXTENSION = 'json'
  OLD_SNAP_CALLED = 'snap'
  FROM_KEY_NAME = '-from'
  TO_KEY_NAME = '+to'
  INSERTED_KEY_NAME = '+inserted_data'
  DELETED_KEY_NAME = '-data_was'
  pk_name  = 'id'
 
  def __init__(self, BASE_DIR, audit_filename, table_pk_name):
    """ Creates empty audit file, and define avro schema on Creating Tracker instance """
    self.BASE_DIR = BASE_DIR
    self.table_pk_name = table_pk_name
    self.audit_filename = f"{''.join(audit_filename.split('.')[0])}"
    self.AUDIT_FILE_PATH = os.path.join(self.BASE_DIR, f'{self.audit_filename}.{self.AVRO_EXTENSION}')
    self.__create_empty_audit_file(self.AUDIT_FILE_PATH)
    self.__create_avro_schema()

  @staticmethod
  def initialize_firebase_storage(firebaseConfig):
    """ Connection established with Firebase """
    Tracker.firebase = pyrebase.initialize_app(firebaseConfig)
    Tracker.storage = Tracker.firebase.storage()
  
  def __create_empty_audit_file(self, audit_file):
    if not os.path.isfile(audit_file):
      with open(audit_file, 'w') as f:
        pass

    """ If avro file is not already present in cloud the add the empty avro file to cloud """
    path = Tracker.storage.child(audit_file).get_url(None)
    try:
      urllib.request.urlopen(path)
    except:
      self.__push_to_cloud(audit_file)
  
  def __remove_from_local(self, file):
    os.remove(file)
  
  def __create_avro_schema(self):
    self.avro_schema = {
      'doc': f"{self.audit_filename} db",
      'name': f"{self.audit_filename}",
      'namespace': f'{self.audit_filename}',
      'type': 'record',
      'fields':[
        {'name': 'updated_on', 'type': 'string'},
        {'name': 'timestamp', 'type': 'string'},
        {'name': f'{self.pk_name}', 'type': 'string'},
        {'name': f'{self.VALUE_UPDATED}', 'type': 'string'},
        {'name': f'{self.VALUE_DELETED}', 'type': 'string'},
        {'name': f'{self.VALUE_CREATED}', 'type': 'string'},
        {'name': f'{self.OLD_SNAP_CALLED}', 'type': 'string'}
      ]
    }
    self.parsed_schema = parse_schema(self.avro_schema)
    
  def __create_or_return_obj(self, obj, key):
    if key not in obj:
      obj[key] = {}
    return obj[key]
  
  def __flatten(self, dictionary, parent_key = '', sep = SEPARATOR):
    items = []
    for key, val in dictionary.items():
      new_key = parent_key + sep + key if parent_key else key
      if isinstance(val, dict):
        items.extend(self.__flatten(val, new_key, sep).items())
      else:
        items.append((new_key, val))
    return dict(items)

  def __deflatten(self, dictionary, sep = SEPARATOR):
    obj = {}
    for k, v in dictionary.items():
      if sep not in k:
        obj[k] = v
      else:
        key_splitted = k.split('.')
        def reconstruct_flat_keys(obj, key, val):
          if len(key) == 1:
            obj[key[0]] = val
            return
          reconstruct_flat_keys(self.__create_or_return_obj(obj, key[0]), key[1:], val)
        reconstruct_flat_keys(self.__create_or_return_obj(obj, key_splitted[0]), key_splitted[1:], v)
    return obj

  def __push_to_cloud(self, file):
    """ Push the avro file to cloud """
    cloudfilename = file
    Tracker.storage.child(cloudfilename).put(file)

  def __download_from_cloud(self, path):
    """ Download the avro file from the cloud """
    cloudfilename = path
    Tracker.storage.child(cloudfilename).download(cloudfilename, cloudfilename)

  def __dump_into_avro(self, delta_changes):
    """ 
      Download the avro file from cloud, 
      append the delta changes to avro file, 
      push the avro file back to cloud,
      and then delete the avro file from local storage 
    """
    self.__download_from_cloud(self.AUDIT_FILE_PATH)
    
    df = pd.DataFrame(delta_changes)
    records = df.to_dict('records')
    
    with open(self.AUDIT_FILE_PATH, 'a+b') as outfile:
      writer(outfile, self.parsed_schema, records)
    
    self.__push_to_cloud(self.AUDIT_FILE_PATH)
    self.__remove_from_local(self.AUDIT_FILE_PATH)


  def __generate_delta_obj(self, old_obj, new_obj):
    now = datetime.datetime.now()
    """ Define the structure od delta object """
    delta_obj = {
      'updated_on': now.strftime('%c'),
      'timestamp': now.timestamp()
    }
    delta_obj[self.pk_name] = old_obj.get(self.table_pk_name, None)
    delta_obj[self.VALUE_UPDATED] = dict()
    delta_obj[self.VALUE_DELETED] = dict()
    delta_obj[self.VALUE_CREATED] = dict()

    """ Fetch keys of old and new objects """
    attrs_of_old_obj = old_obj.keys()
    attrs_of_new_obj = new_obj.keys()

    """ Convert them to set to perform set operations """
    old_obj_keys = set(attrs_of_old_obj)
    new_obj_keys = set(attrs_of_new_obj)

    """
      setA.difference(setB) ==> Present in setA but not in setB
      setA.intersection(setB) ==> Present both in setA and setB
    """
    inserted_keys= new_obj_keys.difference(old_obj_keys) # Keys Present only in new object => keys are inserted
    deleted_keys = old_obj_keys.difference(new_obj_keys) # Keys Present only in old object => keys are deleted
    updated_keys= old_obj_keys.intersection(new_obj_keys) # Keys Present only in both objects => keys are updated

    """ UPDATED """
    """ Add updated key/value pair to delta_obj under @updated """
    for keys in updated_keys:
      if old_obj[keys]!=new_obj[keys]:
        delta_obj[self.VALUE_UPDATED][keys] = {'-from': old_obj[keys], '+to': new_obj[keys]}

    """ INSERTED """
    """ Add inserted key/value pair to delta_obj under @inserted """
    for key in inserted_keys:
      delta_obj[self.VALUE_CREATED][key] = {'+inserted_data': new_obj[key]}

    """ DELETED """
    """ Add deleted key/value pair to delta_obj under @deleted """
    for key in deleted_keys:
      delta_obj[self.VALUE_DELETED][key] = {'-data_was': old_obj[key]}

    return delta_obj
  

  def __extract_from_dataframe(self, value):
    """ evaluate a string back to dictionary """
    """
      "{'name': 'Mohit Kumar', 'age': 21}" --> string
      {'name': 'Mohit Kumar', 'age': 21} --> dictionary
    """
    evaluated_value = ast.literal_eval(value)
    """ call deflatten if dictionary is not empty otherwise simply return dictionary """
    return self.__deflatten(evaluated_value) if bool(value) else evaluated_value
  

  def __fetch_audit_as_json(self, old_snap = False):
    """ Converts avro back to json """
    avro_records = []
    """ Download avro file from cloud """
    self.__download_from_cloud(self.AUDIT_FILE_PATH)
    
    """ Read avro file and convert it to DataFrame """
    with open(self.AUDIT_FILE_PATH, 'rb') as file:
      avro_reader = reader(file)
      avro_records.extend(avro_reader)
    df_avro = pd.DataFrame(avro_records)
    
    field_name = f'{self.audit_filename}_audit'
    delta_obj_json = {field_name: []}
    
    """ Loop over the avro records and built delta_obj (json) back """
    for entry in df_avro.iloc[:,:].values:
      delta_obj = dict()
      delta_obj['updated_on'] = entry[0]
      delta_obj['timestamp'] = entry[1]
      delta_obj[self.pk_name] = entry[2]

      if old_snap:
        """ Attach old snapshot to delta_obj if old_snap == True """
        delta_obj[self.OLD_SNAP_CALLED] = ast.literal_eval(entry[6])
      
      delta_obj[self.VALUE_UPDATED] = self.__extract_from_dataframe(entry[3])
      delta_obj[self.VALUE_DELETED] = self.__extract_from_dataframe(entry[4])
      delta_obj[self.VALUE_CREATED] = self.__extract_from_dataframe(entry[5])

      delta_obj_json[field_name].append(delta_obj)

    """ Remove avro file from local storage """
    self.__remove_from_local(self.AUDIT_FILE_PATH)
    return delta_obj_json
  

  def __filter_by_date_range(self, records, sd, sm, sy, ed, em, ey):
    """ Filter the records by the dates passed """

    """ Build start date and end date """
    start_date = datetime.datetime(sy, sm, sd)
    start_date_timestamp = start_date.timestamp()
    end_date = datetime.datetime(ey, em, ed)
    end_date_timestamp = end_date.timestamp()
    
    """ Filter the records """
    filtered_records = list(filter(lambda audit: float(audit['timestamp']) >= start_date_timestamp and float(audit['timestamp']) <= end_date_timestamp, records[f'{self.audit_filename}_audit']))
    return filtered_records


  def __remove_keys(self, obj, keys):
    """ Remove the list of keys from given object """
    for key in keys:
      if key in obj: 
        del obj[key]


  def __construct_obj_from_delta(self, obj, delta):
    """ Construct the new object from delta object """

    """
      obj = {
        "name": "Mohit",
        "age": 21,
        "hobbies": ["cricket", "travelling"],
        "address": {
          "state": "Odisha"
        }
      }

      delta_obj = {
        "@updated": {
          "name": {"-from": "Mohit", "+to": "Mohit Kumar"}
        },
        "@inserted": {
          "address.city": {"+inserted_data": "Bbsr"}
        },
        "@deleted": {
          "hobbies": {"-data_was": ["cricket", "travelling"]}
        }
      }

      After calling __construct_obj_from_delta(obj, delta_obj)

      obj = {
        "name": "Mohit Kumar",
        "age": 21,
        "address": {
          "state": "Odisha",
          "city": "Bbsr"
        }
      } 

    """

    """ Flatten @updated, @inserted, and @deleted object """
    update_delta_flat = self.__flatten(delta[self.VALUE_UPDATED])
    insert_delta_flat = self.__flatten(delta[self.VALUE_CREATED])
    delete_delta_flat = self.__flatten(delta[self.VALUE_UPDATED])

    """ Length of seperator """
    seperator_len = len(self.SEPARATOR)

    """
      NOTE:

      str = "address.city.+from"
      
      str[-5:]  -->  +from
      str[:-6]  -->  address.city
    """


    """ CONSTRUCT OBJECT FROM DELTA UPDATE """
    for k, v in update_delta_flat.items():
      key_len = len(self.TO_KEY_NAME)
      if self.TO_KEY_NAME in k:
        obj[k[:-(key_len + seperator_len)]] = v
    
    """ CONSTRUCT OBJECT FROM DELTA INSERT """
    for k, v in insert_delta_flat.items():
      key_len = len(self.INSERTED_KEY_NAME)
      if self.INSERTED_KEY_NAME in k:
        obj[k[:-(key_len + seperator_len)]] = v

    """ CONSTRUCT OBJECT FROM DELTA DELETE """
    for k in delete_delta_flat.keys():
      key_len = len(self.DELETED_KEY_NAME)
      if self.DELETED_KEY_NAME in k:
        del obj[k[:-(key_len + seperator_len)]]

    return obj


  def __calc_endpoints_delta(self, records):
    """ For calculating endpoints delta """
    _list = []
    buffer = dict()
    
    for record in records:
      record_id = record[self.pk_name]
      
      if record_id in buffer.keys():
        """
          if record_id is already present in buffer means there are more than one audit records for the given record_id,
          so doing this will give us the final snapshot for the given record_id  
        """
        buffer[record_id]["end"] = record[self.OLD_SNAP_CALLED]
        buffer[record_id]["delta"] = record
        buffer[record_id]["has_atleast_one_change"] = 1
      else:
        """ 
          if record_id is not present in buffer means the records appear for the first time in audit history,
          so this is the initial snapshot for the given record_id
        """
        buffer[record_id] = {"start": record[self.OLD_SNAP_CALLED], "end": None, "delta": record, "has_atleast_one_change": 0}

    """
      Structure of buffer object
      --------------------------

      buffer = {
        "some_random_id_1": {
          "start": "Initial_snapshot record object",
          "end": "Final_snapshot record object",
          "delta": "Delta factor for the record",
          "has_atleast_one_change": 0/1,
        },
        "some_random_id_2": {},
        ....
        "some_random_id_n": {} 
      }
    """

    """
     has_atleast_one_change = 0 --> specifies that there is only one record history for the given id, 
      so no need to calculate the delta between inital and final snapshot, just return the delta
     has_atleast_one_change = 1 --> specifies that there is more than one record history for the given id, 
      and we need to calculate the delta between inital and final snapshot
    """

    for key in buffer.keys():
      """ Loop over the buffer object """
      current_obj = buffer[key]
      delta = None    
      if current_obj["has_atleast_one_change"]:
        """ Construct the final snapshot obj from current_obj["end"] and delta object  """
        new_obj = self.__construct_obj_from_delta(current_obj["end"], current_obj["delta"])

        """ Generate delta between initial and final snapshot """
        delta = self.__generate_delta_obj(current_obj["start"], new_obj)

        """ OPTIONAL (NOT REQUIRED) """
        # delta = self.__deflatten(self.__flatten(delta))
      else:
        """ Here has_atleast_one_change = 0, so simply return delta """
        delta = current_obj["delta"]
      
      """ Remove updated_on, timestamp and snap from final delta object """
      self.__remove_keys(delta, ['snap', 'updated_on', 'timestamp'])
      _list.append(delta) 
    return _list
    

  def track(self, old_obj, new_obj):
    """ Finds delta between old and new object and append the delta_change object to avro """
    
    """ Flattens old and new object """
    flattened_old_obj = self.__flatten(old_obj)
    flattened_new_obj = self.__flatten(new_obj)

    """ Generates delta from flattened old and new object """
    delta_change_obj = self.__generate_delta_obj(flattened_old_obj, flattened_new_obj)

    """ ATTACH OLD SNAPSHOT to delta change object """
    delta_change_obj[self.OLD_SNAP_CALLED] = flattened_old_obj

    # converting the values of the dictionary(json) to string so as to store in avro
    for change in delta_change_obj.keys():
      delta_change_obj[change] = [str(delta_change_obj[change])]
    
    """ Append the delta_change object to avro """
    self.__dump_into_avro(delta_change_obj)


  def get_all_audits(self):
    """ This method is available to users to fetch all audits """
    return self.__fetch_audit_as_json(old_snap = False)


  def audit_of_today(self):
    """ Fetch todays audit """
    today = datetime.datetime.today()
    d, m, y = int(today.strftime('%d')), int(today.strftime('%m')), int(today.strftime('%Y'))
    return self.audit_of_date(d, m, y)
  

  def audit_of_date(self, d, m, y):
    """ Fetch audit of a given date """
    start_date = datetime.datetime(y, m, d)

    """ As this function will give the audit for a given date so end_date will be (start_date + 1 day) """
    end_date = start_date + datetime.timedelta(days = 1)
    ed, em, ey = int(end_date.strftime('%d')), int(end_date.strftime('%m')), int(end_date.strftime('%Y')) 
    return self.audit_between_date(d, m, y, ed, em, ey)


  def audit_from_date(self, d, m, y):
    """ Fetch audit from a given date """
    end_date = datetime.date.today()

    """ 
      As end_date is excluded while filtering records so todays audit will not be included,
      So 1 day is added to end_Date to include todays audit as well
    """
    end_date = end_date + datetime.timedelta(days = 1)
    ed, em, ey = int(end_date.strftime('%d')), int(end_date.strftime('%m')), int(end_date.strftime('%Y'))
    return self.audit_between_date(d, m, y, ed, em, ey, endpoints = False)


  def audit_between_date(self, sd, sm, sy, ed, em, ey, endpoints = False):
    """
      Filters the records present in a specific date_range
      endpoints = False --> Show all the delta_change audit records in a specific date_range
      endpoints = True --> Just show the delta_change from initial and final snapshot
    """
    record_field = f'{self.audit_filename}-{sd}-{sm}-{sy}__{ed}-{em}-{ey}'
    records = {record_field: []}
    data_audits = self.__fetch_audit_as_json(old_snap = endpoints)

    filtered_records = self.__filter_by_date_range(data_audits, sd, sm, sy, ed, em, ey)
    delta_of_filtered_records = filtered_records if not endpoints else self.__calc_endpoints_delta(filtered_records)

    records[record_field].extend(delta_of_filtered_records)
    return records
  
  
  def audit_by_id(self, id, sd = None, sm = None, sy = None, ed = None, em = None, ey = None):
    """ Filters the audit records matching the given id in parameter """
    dates = [sd, sm, sy, ed, em, ey]

    record_field = f'{self.audit_filename}-id-{id}'
    records = {record_field: []}
    data_audits = self.__fetch_audit_as_json(old_snap = False)

    if None not in dates:
      """ If all the date parameters are given then first filter the records by date_range """
      filtered_records = self.__filter_by_date_range(data_audits, sd, sm, sy, ed, em, ey)
      data_audits[f'{self.audit_filename}_audit'] = filtered_records

    """ Now filter the records matching the given id """
    filtered_records = list(filter(lambda audit: audit[self.pk_name] == id, data_audits[f'{self.audit_filename}_audit']))
    records[record_field].extend(filtered_records)
    return records
  

  def audit_by_operation(self, operation, sd = None, sm = None, sy = None, ed = None, em = None, ey = None):
    """ Filters the audit records by operation performed i.e. inserted, updated, and deleted """
    dates = [sd, sm, sy, ed, em, ey]
    operations_available = ['inserted', 'updated', 'deleted']

    if operation not in operations_available:
      return
    operation = f'@{operation}'
    
    """ Only add that operation to resultant object which mentioned in the parameter and ignore the rest """
    def fetch_operation_obj(audit, _list):
      if audit.get(operation, None):
        _list.append({
          'updated_on': audit['updated_on'],
          'timestamp': audit['timestamp'],
          'id': audit[self.pk_name],
          operation: audit[operation]
        })
    
    record_field = f'{self.audit_filename}--{operation}'
    records = {record_field: []}
    data_audits = self.__fetch_audit_as_json(old_snap = False)

    if None not in dates:
      """ If all the date parameters are given then first filter the records by date_range """
      filtered_records = self.__filter_by_date_range(data_audits, sd, sm, sy, ed, em, ey)
      data_audits[f'{self.audit_filename}_audit'] = filtered_records

    """ Now filter the object by operation """
    list(map(lambda audit: fetch_operation_obj(audit, records[record_field]), data_audits[f'{self.audit_filename}_audit']))
    return records
