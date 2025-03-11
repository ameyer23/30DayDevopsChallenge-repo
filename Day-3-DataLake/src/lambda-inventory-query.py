#TO DO: work on refining and attempting queries from the console. 

import boto3
import json
import time

# Create clients for Lambda, S3, Glue, and Athena
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')
athena_client = boto3.client('athena')

# Specify the S3 bucket name and file names
bucket_name = 'lambda-fn-inventory-120193'  # Change to your desired bucket name
file_name = 'lambda_functions_list.json'
glue_database_name = "lambda_functions_list"
athena_output_location = f"s3://{bucket_name}/athena-results/"

# Create an S3 bucket (if it doesn't exist)
def create_bucket(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except:
        # Bucket does not exist, create it
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created.")

# List all Lambda functions and their runtimes
def list_lambda_functions():
    functions = []
    response = lambda_client.list_functions()

    # Add the function names and runtimes to the list
    functions.extend(response['Functions'])

    # If there are more functions (pagination), retrieve the next set of results
    while 'NextMarker' in response:
        response = lambda_client.list_functions(Marker=response['NextMarker'])
        functions.extend(response['Functions'])

    return [(function['FunctionName'], function['Runtime']) for function in functions]

# Write the Lambda function data to S3
def write_to_s3(data, bucket_name, file_name):
    # Convert the data to JSON
    json_data = json.dumps(data, indent=4)
    
    # Upload the data to S3
    s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)
    print(f"Data successfully written to s3://{bucket_name}/{file_name}")

# Create a Glue table and ensure the database exists
def create_glue_table():
    """Create a Glue table for the data."""
    try:
        # Check if the database exists, and if not, create it
        try:
            glue_client.get_database(Name=glue_database_name)
            print(f"Database {glue_database_name} already exists.")
        except glue_client.exceptions.EntityNotFoundException:
            glue_client.create_database(DatabaseInput={'Name': glue_database_name})
            print(f"Database {glue_database_name} created.")

        # Now create the Glue table
        glue_client.create_table(
            DatabaseName=glue_database_name,
            TableInput={
                "Name": "lambda_functions_glue_table",
                "StorageDescriptor": {
                    "Location": f"s3://{bucket_name}/{file_name}",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe"
                    },
                    "Columns": [
                        {"Name": "FunctionName", "Type": "string"},
                        {"Name": "Runtime", "Type": "string"}
                    ]
                },
                "TableType": "EXTERNAL_TABLE",
            },
        )
        print(f"Glue table 'lambda_functions_glue_table' created successfully.")
    except Exception as e:
        print(f"Error creating Glue table: {e}")

# Set up Athena query output location to S3
def set_athena_output_location(bucket_name):
    output_location = f"s3://{bucket_name}/athena_results/"

    # Set the query results location using Athena
    athena_client.start_query_execution(
        QueryString="SELECT 1;",  # Dummy query to just trigger Athena settings
        QueryExecutionContext={'Database': 'lambda_db'},
        ResultConfiguration={
            'OutputLocation': output_location
        }
    )
    print(f"Athena query output will be saved to: {output_location}")

# Main script
def main():
    
    # Create bucket
    create_bucket(bucket_name)
    
    # Get Lambda function data and write it to S3
    lambda_functions = list_lambda_functions()
    write_to_s3(lambda_functions, bucket_name, file_name)

    # Create Glue table
    create_glue_table()

    # Set Athena output location (without running a query)
    set_athena_output_location(bucket_name)

if __name__ == "__main__":
    main()
