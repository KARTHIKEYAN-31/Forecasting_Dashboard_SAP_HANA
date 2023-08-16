# US ELECTRICITY DEMAND FORECAST AND ANALYTICS USING SAP HANA CLOUD AND PYTHON #

The goal of the project is to forecast the realtime data of US electricity demand per hour for next 3 months, using SAP HANA, SAP BTP, Visualization tools, Python.

The Project divided into two parts, 
One is to develop, deploy, shedule a python task file in SAP BTP CF, which need to extract the data from SAP HANA Cloud, forecast the data and save it in another table fo HANA cloud. 
Second is to create a dashboard to display the forecasted data and stat of the data to the user. 


## Architecture ##

![alt text](https://github.com/KARTHIKEYAN-31/Forecasting_Dashboard_SAP_HANA/blob/main/Images/hana-forecast.PNG)
<img src="[image URL](https://github.com/KARTHIKEYAN-31/Forecasting_Dashboard_SAP_HANA/blob/main/Images/hana-forecast.PNG" width="100" height="100">

## Forecasting Task ##

### 1. The plan is to create a python file, which need to forecast the data and store back to HANA Cloud DB ###

> Steps:

>> * Connect with HANA DB using hana_ml library
>> * Extract Training data from HANA DB
>> * Pre process the data
>> * Train the model and Forecast the data for next 3 months
>> * Save the stat of model and forecasted data into the HANA DB

### 2. Create the required Files to deploy the python file as task into the SAP BTP Floudry ###

> Steps:

>> * Create runtime.txt file by mention the runtime environment
>> * Create requirements.txt file by mention the python libraries used
>> * Create a manifest.yml file to mention the features of application to deploy in the Cloud Foundry

### 3. Deploy the Python file as Task into the Cloud Foundry ###

> Steps:

>> * install cloud foundry in the system you are running the fiel
>> * use 'cf login' to login into the Cloud Foundry. Use SAP BTP mail and password.
>> * If you have multiple space selecte the space where you want to deploy the task.
>> * use 'cf push task' to deploy the python file as task into the Cloud Foundry.

### 4. Schedule the Python Task to run for every hour ###

> Steps:

>> * Create SheduleJob and xsaa instance in SAP BTP
>> * Create a shedule job for the task you deploy in previous step
>> * Click on Task and create new task
>> * Click on shedule and create new shedule by mention in start and end data with frequent interval




## App - Dashboard ##

The idea is to ceate a Dashboard using streamlit to visulize the forecasted data and stat of Demand to the user. As in this project i didn't used the live data connection, I had created a data entry UI to update the data into the HANA DB manually.

### 1. Connect with HANA DB and access the Tables ###

> Steps:
>> * Connect to the table using hana_ml library
>> * Extract the data from Training table, Prediction table and Stat Table

### 2. Updata the data to the training table if entered ###

> Steps:
>> * If user choose to enter the data, check the last data of training table and get the next data from the user
>> * Updata the value to the training table

### 3. Visualize the data ###

> Steps:
>> * Create two columns
>> * Join training data and predicted data and plot it using plotly libray in first column
>> * Then process the data to get the detailed data from timestamp
>> * Plot the box plot in alternate column to show the stat of the data
>> * Write the predicted data and stat of trained model

### 4. Deploy the Application ###

> Steps:
>> * Push the code to git repo
>> * Deploy the streamlit app 






















