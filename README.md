[![](doc/neurrolab_logo.png)](https://neurro-lab.engin.umich.edu/)

# Breaking the Barriers to Designing Online Experiments: A Novel Open-Source Platform for Supporting Procedural Skill Learning Experiments<!-- omit in toc -->

This repository contains a web application that provides researchers in the motor learning field with a way of creating and monitoring sequential finger-tapping experiments very easily, without any coding experience required. Researchers can create a new user profile, set up an experiment by selecting from a set of options, and then distribute the experiment as needed by just sending a link. Participants will be able to do the experiments from their own personal computers. Researchers can then track an experiment responses and download the participants data in a processing-friendly format. We hope that this tool allows researchers in the motor learning field to quickly test hypotheses without the hassle of having to bring subjects into a laboratory.

The web app is accessible at https://experiments.neurro-lab.engin.umich.edu/, and an example experiment is available [here](https://experiments.neurro-lab.engin.umich.edu/experiment/5FYA/). Go to [How to use](#how-to-use) for a guide on how to use the platform.

![app_gif](doc/webapp.gif)

## Citation<!-- omit in toc -->

If you use this software, please cite it as below.

## Table of contents<!-- omit in toc -->

- [How to use](#how-to-use)
  - [General Usage](#general-usage)
  - [Result files](#result-files)
    - [Raw data](#raw-data)
    - [Processed data](#processed-data)
    - [End survey](#end-survey)
- [Run locally](#run-locally)
  - [Dependencies](#dependencies)
    - [Set up dependencies and environment](#set-up-dependencies-and-environment)
    - [Set up database](#set-up-database)
    - [Set up Google Cloud Storage](#set-up-google-cloud-storage)
    - [Set up email account (optional)](#set-up-email-account-optional)
  - [Usage](#usage)
- [Contributing](#contributing)
  - [Understanding the code](#understanding-the-code)
    - [Django](#django)
    - [Javascript](#javascript)
    - [Vue](#vue)
- [Known issues and future work](#known-issues-and-future-work)
- [Contact](#contact)
- [License](#license)

## How to use

### General Usage

Here, we will cover basic usage of the web application, starting from user registration to experiment distribution and data download.

The first step when interacting with the web app is creating a new user. A user in the platform represents a researcher, and it has permissions to create, edit, and delete studies and experiments. To create a new user, please go to https://experiments.neurro-lab.engin.umich.edu/register and fill out the required fields.

Once you are correctly registered, the platform will automatically redirect you to your Profile page, which is one of the most important pages in the application. A screenshot of a sample profile page of a subject with two studies is shown below. The view is split in two: first, it shows the unpublished studies, i.e., those studies that are not yet ready for distribution. Below, it shows the published studies, i.e., those studies that are ready for distribution. When registering a new user, no studies will be available; you will first need to create a new study.

![](doc/profile.png)

To create a new study, click on the `Create Study` button, or go to https://experiments.neurro-lab.engin.umich.edu/profile/create_study (you have to be logged in to create a new study). Then, a form will be shown that will ask for a study name and an optional description. Fill those out and then click `Submit`. You will be redirected to the Profile page, and will notice a 4 character code next to the study name. That is the study ID and it is a unique key that will allow users to access your study (same as with groups and experiments, as we will see later).

After creating a study, you can create a new group (or plenty, if your study needs to have more than one group). You can use the form available in the study card; it only requires a name. After getting a group (or groups) and the study created, you can create a new experiment. Click on the `Create Experiment` button in the Profile page or go to https://experiments.neurro-lab.engin.umich.edu/profile/create_experiment for that.

An experiment requires an existing unpublished study and group to be created. You can select the recently created study and group from the dropdowns in the experiment form. Fill out the other required fields, such as the name, instructions video (max size 32MB), consent form, and some specific properties. Then, you can start customizing the experiment by adding blocks to it. A sample experiment block that will repeat 36 times is shown below. When you are ready, click on the `Submit` button to finalize the experiment creation. You will be redirected to the Profile page, where you will be able to see your experiment.

![](doc/block_form.png)

Now, you are ready to test your experiment and see if it needs any modifications. Find the newly created experiment in the Profile page and click on `Test Experiment`. Note that the experiment is not yet public, and people who go to the link at which you can access it won't be able to see it.

![](doc/test_experiment.png)

Once all experiments in your study are ready to go, then you can go on and publish the study by clicking on the `Publish` link in the "Study actions" section of a study. When you publish a study, all the data you collected from testing the experiment will be discarded, so that it doesn't mix with the actual participants' data. Once the study is published, it will appear on a new section of the Profile page which will show all published studies.

Now, you are ready to distribute your study and recruit online participants. To allow a participant access to an experiment, you have two options: you can give them a link that sends them straight to the experiment (will have the form https://experiments.neurro-lab.engin.umich.edu/experiment/CODE/, where CODE is the experiment identifier 4-character code), or you can give them study, group, and/or experiment codes, and ask them to enter them in the homepage (https://experiments.neurro-lab.engin.umich.edu/). If participants only have the study code, then they would be randomly assigned to a group inside the study, and will be redirected to the first experiment of the group. If a subject already participated in an experiment of the group they were assigned to, then they are redirected to the next experiment in the group. Note that the order of the experiment is, for now, determined by the date at which they were created. This is subject to change in the future.

Once participants start doing the experiments, you will be able to see the number of responses next to the experiment actions in the Profile page. An example is shown below: 52 participants have completed the shown experiment.

![](doc/track_responses.png)

Once you are happy with the number of responses, and want to stop people from participating, you can disable the experiment by clicking on `Disable` next to the experiment. You can also download the participants' data for further processing. Three different files per experiment are available: `Raw data`, which contains the timestamp for each keypress in the experiment and could be used for fine detail analysis; `Processed data` aggregates data per trials and gives information about tapping speed and execution time for each one; `Survey data` contains the end survey information across all subjects, which can be used for demographic analyses. A subset of an example resulting `csv` file for the `Processed data` is shown below. The description for each table header, for all three files, can be found in section [Result files](#result-files).

| experiment_code | subject_code     | block_id | block_sequence | trial_id | correct_trial | accumulated_correct_trials | execution_time_ms | tapping_speed_mean | tapping_speed_extra_keypress |
| --------------- | ---------------- | -------- | -------------- | -------- | ------------- | -------------------------- | ----------------- | ------------------ | ---------------------------- |
| DHXY            | bCvf6ST6AZ5QOD2G | 1        | 70897          | 1        | True          | 1                          | 2191              | 1.82565038795071   | 1.82565038795071             |
| DHXY            | bCvf6ST6AZ5QOD2G | 1        | 70897          | 2        | False         | 1                          |                   |                    |                              |
| DHXY            | bCvf6ST6AZ5QOD2G | 1        | 70897          | 3        | False         | 1                          |                   |                    |                              |
| DHXY            | bCvf6ST6AZ5QOD2G | 2        | 70897          | 1        | True          | 1                          | 1409              | 2.8388928317956    | 2.8388928317956              |
| DHXY            | bCvf6ST6AZ5QOD2G | 2        | 70897          | 2        | False         | 1                          |                   |                    |                              |
| DHXY            | bCvf6ST6AZ5QOD2G | 2        | 70897          | 3        | True          | 2                          | 1117              | 3.5810205908684    | 2.90528762347472             |
| DHXY            | bCvf6ST6AZ5QOD2G | 2        | 70897          | 4        | True          | 3                          | 1008              | 3.96825396825397   | 3.24044069993519             |

Table explaining each of the file headers

### Result files

#### Raw data

|         **Header**         | **Type** |                                                                                       **Description**                                                                                        |
| :------------------------: | :------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|      experiment_code       |  string  |                                                                       4-character code that represents the experiment                                                                        |
|        subject_code        |  string  |                                                                        16-character code that represents the subject                                                                         |
|          block_id          | integer  |                                                                             Block number that this row refers to                                                                             |
|       block_sequence       |  string  |                                                         Sequence of the current block. Resets to one when there is a subject change                                                          |
|          trial_id          | integer  |                                                           Number of the current trial. Resets to one when there is a block change                                                            |
|     was_trial_correct      | boolean  |                                                          Whether the current trial as a whole was correctly inputted by the subject                                                          |
| was_partial_trial_correct  | boolean  | Whether the current trial as a whole was partially correct. It can be partially correct when the subject runs out of time in a given block but the inputted sequence so far had been correct |
|     keypress_timestamp     | datetime |                                                         YYYY-MM-DD HH:MM:SS.MS format for the timestamp at which the key was pressed                                                         |
|       keypress_value       |  string  |                                                                                 The value of the key pressed                                                                                 |
|    was_keypress_correct    | boolean  |                                            Whether the keypress was correct in the context of the current sequence and location in that sequence                                             |
| diff_between_keypresses_ms | integer  |                                                         How many milliseconds were there between the last keypress and this keypress                                                         |

#### Processed data

|          **Header**          | **Type** |                                                     **Description**                                                      |
| :--------------------------: | :------: | :----------------------------------------------------------------------------------------------------------------------: |
|       experiment_code        |  string  |                                     4-character code that represents the experiment                                      |
|         subject_code         |  string  |                                      16-character code that represents the subject                                       |
|           block_id           | integer  |                                           Block number that this row refers to                                           |
|        block_sequence        |  string  |                       Sequence of the current block. Resets to one when there is a subject change                        |
|           trial_id           | integer  |                         Number of the current trial. Resets to one when there is a block change                          |
|        correct_trial         | boolean  |                             Whether the current trial was correctly inputted by the subject                              |
|  accumulated_correct_trials  | integer  |  Accumulated number of correct trials in a given block. If all trials are correct, this number would match the trial_id  |
|      execution_time_ms       | integer  |                          Time in milliseconds between the first and last keypress of the trial                           |
|      tapping_speed_mean      |  float   |                         One over the mean time in milliseconds between keypresses in this trial                          |
| tapping_speed_extra_keypress |  float   | One over the mean time in milliseconds between keypresses, including the time between trial start and the first keypress |

#### End survey

|           **Header**            | **Type** |                                                                                         **Description**                                                                                         |
| :-----------------------------: | :------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|         experiment_code         |  string  |                                                                         4-character code that represents the experiment                                                                         |
|          subject_code           |  string  |                                                                          16-character code that represents the subject                                                                          |
|      started_experiment_at      | datetime |                                                         Datetime in UTC at which the subject started the first trial of the experiment                                                          |
|               Age               | integer  |                                                                                         Age of subject                                                                                          |
|             Gender              |  string  |                                                                     Gender of subject. Can be "male", "female", or "other"                                                                      |
|          Computer Type          |  string  |                                                          Type of computer used for experiment. Can be "laptop", "desktop", or "other"                                                           |
|        Medical condition        | boolean  |     Answer to the question "Do you have any medical conditions (e.g., recent surgery, fracture, vision problem, stroke) that could have potentially affected your performance on the task?"     |
|   Hours of Sleep night before   | integer  |                                                                        How many hours the subject slept the night before                                                                        |
|       Excercise Regularly       | boolean  |                                                                        Answer to question: "Do you exercise regularly?"                                                                         |
|       Level of Education        |  string  | Level of education completed. Can be "kindergarten_or_below", "first_to_sixth", "seventh_to_ninth", "tenth_to_twelfth", "community_college_or_associate_degree", "bachelor", or "master_or_phd" |
| Done keypress experiment before | boolean  |                                                                      Whether they have done keypressing experiments before                                                                      |
|      Followed instructions      | boolean  |                                                              Answer to the question: "Did you follow the experiment instructions?"                                                              |
|    Hand used for experiment     |  string  |                                                             Hand subject used for the experiment. Can be "left", "right", or "both"                                                             |
|          Dominant Hand          |  string  |                                                                                   Self-reported dominant hand                                                                                   |
|            Comments             |   text   |                                                                       Any comments they had on the experiment experience                                                                        |

## Run locally

Some researchers may need to customize the web application to their specific needs. To do that, the application can run locally in a lab computer, where they would be able to clone this repository and do the modifications needed for their studies.

The application was extensively tested in a computer running Ubuntu 20.10 and Python 3.9 through [Anaconda](https://www.anaconda.com/). The evironment was chosen due to how easy it makes installing new packages and configuring the development conditions in general. Most of the application should run as is in Windows. However, it has not been tested, which should be taken into account.

### Dependencies

The core of the application was built using two different tools: Django and Vue. Django is a web framework based in Python that has become popular in the past few years because of how easy it is to create applications from scratch. We used [Django](https://www.djangoproject.com/) to develop the full backend of the application: all connections to the database and all url-to-view requests are handled by the Django backend. [Vue](https://vuejs.org/), on the other hand, is a Javascript framework, and we used it to manage most of the frontend behavior of the web app: any interactive behavior (e.g., the actual experiment) is managed by Vue.

One important caveat is that, as of now, the application is intimately linked with Google Cloud. Even when running the application locally, we use Google Cloud Storage to manage the uploading and downloading of the instructions videos and consent forms, and the downloading of experiments' data. In this instructions, we will cover how to connect to the Cloud Storage account, assuming users have created a Google Cloud account and have billing enabled. It is also possible to run it completely offline, but some modifications would have to be made to the code:

1. Every method in [views.py](gestureApp/views.py) that uploads to Cloud Storage would have to be changed so that it saves the files locally.
2. The links to the processed experiment files in [views.py](gestureApp/views.py) would also need to be changed to the local paths.
3. The [Experiment.vue](static/gestureApp/js/components/Experiment.vue) component would have to be updated with the local path at which the instructions video and consent form are to be saved.

Now, we will go over each step necessary to set up the local environment and run a version of the application locally (though still connected to Google Cloud Storage).

#### Set up dependencies and environment

The first step (though optional) is to install Anaconda, following the instructions [here](https://www.anaconda.com/) to install it for Linux. Then, we can create the environment, download the repository, and install all the dependencies.

```bash
# Open terminal after having anaconda added to path
conda create -n motorlearningapp python=3.9
conda activate motorlearningapp
# Clone repository
git clone <REPO_URL>
# Install python dependencies
cd motorlearningapp
pip install -r requirements.txt
```

The next part is setting up the Google Cloud CLI (command line interface), which will allow the local application to upload the files to Google Cloud Storage. The instructions for installing the CLI are available [here](https://cloud.google.com/sdk/gcloud).

Finally, we will create an environment file that will contain all relevant passwords and keys to make the application work. Note that it is very important to keep this file a secret, as others could use these passwords to disrupt the application and maybe even incur in additional charges with the Google Cloud account. The environment file will be called `.env`, and should contain the following:

```bash
DATABASE_URL=<URL>
SECRET_KEY=<DJANGO_SECRET_KEY>
DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=<ABSOLUTE_PATH_TO_SERVICE_ACCOUNT_KEY>.json
# Following two are optional
MAILJET_API_KEY=<API_KEY>
MAILJET_SECRET_KEY=<SECRET_KEY>
```

The Django secret key may be generated using the following command:

```bash
conda activate motorlearningapp
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### Set up database

For this app we have used PostgreSQL as the database provider, since it allows specific queries that are useful when analyzing the experiment data. To install PostgreSQL in Ubuntu, follow the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart).

Once the setup is complete, we can create our database:

```bash
sudo -u postgres createdb motorlearningapp
```

Once the database is setup, we need to update the `.env` file with the proper URL to access it. The structure should be as follows:

```bash
DATABASE_URL=postgres://<USER>:<PASSWORD>@<HOST ADDRESS>/<DATABASE NAME>
```

For example, if the user for the database is `postgres`, the password is `12345678`, the host address is `127.0.0.1` (running locally) and the database is called `motorlearningapp`, then the URL would be:

```bash
DATABASE_URL=postgres://postgres:12345678@127.0.0.1/motorlearningapp
```

Finally, we need to create the database structure that our application expects. For that, we can use Django:

```bash
conda activate motorlearningapp
cd motorlearningapp
python manage.py migrate
```

#### Set up Google Cloud Storage

Here we will go over how to setup Google Cloud Storage to be able to upload and then download the instructions videos and consent forms for each experiment created. Note that this could be done with other storage services (such as AWS S3), or even locally, but the instructions would vary a little on those cases.

The first part is to create a new bucket in Google Cloud Storage. To do that, you can follow the instructions [here](https://cloud.google.com/storage/docs/creating-buckets). A bucket allows you to store and download content. Remember the name you gave to the bucket, as it is important for the next steps. Finally, to allow Javascript to extract the files from the buckets without any extra permissions, we need to configure the bucket to serve the files publicly. To do that, you can follow the instructions [here](https://cloud.google.com/storage/docs/access-control/making-data-public).

After the bucket in Google Cloud Storage is set up, we need to reference it from the necessary parts of the code. The bucket name should be modified at the top of [views.py](gestureApp/views.py) with the new bucket name. The URL for both the consent form and instruction video should be updated to the bucket URL in [Experiment.vue](static/gestureApp/js/components/Experiment.vue), on the lines where `video_url` and `pdf_url` are defined.

Then, to be able to upload files to the Cloud Storage from the local application, we will need to set up a new service account with permissions to Cloud Storage. A tutorial to do that can be found [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys). Make sure that the service account has access to the bucket you created in the previous step.

The service account key you just created should be put inside the folder `config` in the local copy of the repository. Note that by default all the content inside config gets ignored by git. This is important: you do not want to upload the service account key to the remote repository, as it could be used to create unwanted Google resources, depending on how many permissions that service key has.

#### Set up email account (optional)

The application allows first-time participants to email their user code to themselves, so that they have it available the next time they participate. The application is currently set up with a free account of Mailjet. If you want to enable the same feature for your application, you will need to set up a Mailjet account.

To do that, sign up [here](https://app.mailjet.com/signup) and choose the plan most suitable to your needs. Then, you will need to copy the API key and secret key they provide, and put it into the `.env` file. It should have the following structure:

```bash
# .env
...
MAILJET_API_KEY=<API_KEY>
MAILJET_SECRET_KEY=<SECRET_KEY>
...
```

### Usage

Finally, to actually run the application, you need to run the following:

```bash
conda activate motorlearningapp
cd motorlearningapp

python manage.py runserver
```

Make sure that the database is running (either remotely or locally), or the application will fail to run.

Then, you can access the application by going to http://127.0.0.1:8000/ in a browser.

## Contributing

### Understanding the code

In this section, we will go over the most important files that the application has, and explain a little what their role is. We can separate our application into three distinct frameworks and languages: Django, Javascript, and Vue. Django manages the backend of the application, connecting to the database and handling requests. Javascript handles the connection between Django and Vue, making the necessary API connections to the backend and giving information to the frontend about the experiment or the current user. Vue manages the frontend, and adds interactivity to the webpage: the experiments run through Vue code.

#### Django

A complete Django tutorial can be found [here](https://www.djangoproject.com/start/). It is recommended to complete it before modifying anything, as it is important to understand the general structure of the webpage. Django constitutes the basic building block of the webpage, and without it, it would not be possible to run the application.

Some of the most important files and folders from the Django side of the application are explained here:

1. [gestureApp/views.py](gestureApp/views.py): contains all the methods that handle the different requests to the web app. For example, the method `experiment` is run when a participant (or a researcher, when testing) accesses a new experiment. It takes an experiment ID as argument, and then renders the template [experiment.html](gestureApp/templates/gestureApp/experiment.html). It passes along the experiment information, all blocks that it contains, and the subject code that was assigned to the current user.
2. [gestureApp/urls.py](gestureApp/urls.py): this file links URL addresses to a specific method in [views.py](gestureApp/views.py). It can also stablish some conditions on the URL, to make sure that it is being accessed correctly. For example, for the experiment URL, it expects an address with the following structure `^experiment/(?P<pk>[A-Z0-9]{4})/$`, which means that the PK needs to be a 4 character code containing only uppercase letters and numbers. It also links the `experiment` method described before to this URL, by passing `views.experiment` as the second argument.
3. [templates/experiment.html](gestureApp/templates/gestureApp/experiment.html): the templates in Django are pseudo HTML files that allow Django python code to pass variables from the backend to the frontend. [experiment.html](gestureApp/templates/gestureApp/experiment.html) is the template that renders the experiment. It also passes the information about the experiment and all its blocks to the frontend. Then, the corresponding Javascript file reads from it and passes it to the Vue component.

#### Javascript

Multiple Javascript tutorial exist, but one that has great reviews is [this one](https://javascript.info/). It is recommended to do a Javascript tutorial before working on the project, as it is necessary to understand certain nuances in the code.

The general workflow of the Javascript file is as follows: it reads some properties from the HTML template it is loaded on, and then renders a Vue component that makes use of those properties. The Vue component may do some actions that require interaction with the database: the Javascript file is the one that contains all the actual calls to the Backend.

As an example, the file [experiment.js](static/gestureApp/js/experiment.js) reads the experiment and blocks information from the Django template, and then renders the [Experiment](static/gestureApp/js/components/Experiment.vue) Vue component, passing all the information. After the experiment is done, the Javascript file is the one that does the internal API requests to save the experiment response and the end survey if applicable.

#### Vue

Finally, Vue is a Javascript framework on which most of the frontend interactivity is based in the app. A very thorough tutorial can be found [here](https://vuejs.org/tutorial/#step-1).

A Vue file is generally split in three parts: the HTML, the code, and the style. As an example, the [Experiment.vue](static/gestureApp/js/components/Experiment.vue) component is the one that handles the experiment interaction with the participant: it first shows the instructions video and consent form, and then shows the experiment to the user, capturing the keypresses when appropriate. When the experiment is done, it emits an event to the parent Javascript script ([experiment.js](static/gestureApp/js/experiment.js)), which then does the necessary requests to the Django API.

## Known issues and future work

The current application is intimately linked to Google Cloud, which is a limitation in case there is interest in migrating to another platform, or when trying to run it completely local.

## Contact

If you have any issues, please create a new issue in the repository, or contact Luis Cubillos at lhcubill@umich.edu.

## License

See the [License.md](License.md) file for license rights and limitations (MIT).
