# AB Test Results
This project tracks AB test results and saves the best variants by click-through-rate.

# Local development
To set up the local test environment run
```bash
docker-compose up --build
```
This starts three containers:
 * curl invocations to mimick SNS messages
 * lambda function processing and sending messages to a database
 * mysql database to store results

In the terminal log you can see if the data was received and passed on by the lambda function. To verify data was stored in the database, first connect to the database container with

```bash
docker exec -it local-rds mysql -u testuser -p
```
enter the password *testpassword*, then run 

```sql
USE testdb;
SELECT * FROM ab_test_results;
```
to see all entries in the table.

# Deploy to AWS
To deploy this project to AWS use the terraform templates. Make sure you're in the *provision* directory, are logged in to an AWS account, 

Prerequisites
* Define all inputs (see variables.tf for a list of variables) in a .tfvars file, e.g. *dev.tfvars* 
* Add requirements (see requirements.txt) to the lambda package either by installing directly in the *src* directory or creating a custom lambda layer and adding it to the terraform configuration.
* If you already have an SNS-Topic, replace the "sns_topic" resource at the top of the *main.tf* file.

Then run

```bash
terraform init
terraform apply -var-file="dev.tfvars"
```
to reploy all resources.


# AWS Architecture
The terraform set up creates three main components:
 ### SNS topic
 This is messaging service responsible for broadcasting the AB test results.
 ### Lambda function 
 This subscribes to the SNS topic with an "aws_sns_topic_subscription" and picks up all test results. This means every time a new message is published on the topic, the lambda function is invoked. It then parses the test results and checks if any of the test variants had a 20 % higher click-through-rate than all other variants at that time. If there is a clear winner it sends the data below to the database for permanent storage:
 * clicks (int)
 * views (int)
 * ctr (decimal)
 * id of the variant (int)
 * id of the test run (varchar)

If no clear winner is found in a test run, no data is stored.

### RDS Database
This stores results in a mysql database with the above mentioned schema. 


# TODO
* 20 % rule code improvements
* credential handling
* improve logging
* terraform monitoring
