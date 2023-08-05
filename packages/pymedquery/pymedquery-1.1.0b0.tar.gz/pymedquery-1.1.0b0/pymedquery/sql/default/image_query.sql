/*
This is a default quert for extracting SERIES UID only. The query is meant to be used by
beginner users, users that don't have the need for advanced queries and users that don't
want to learn SQL.

The query is designed to fetch all images from a certain project which is why the the project_id
variable is formatted into the query.

parameters
--------------
project_id : str
    This is a user defined variable that will filter patientIDs on a projectID.
limit : Union[int, str]
    This is limiter for how many rows to get back from the query

result : List[Dict[str, List]
    this is the result that you get in python only. Not in the SQL editor.

The view columns:
patient_uid | series_uid |
 */
