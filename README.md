[![](doc/neurrolab_logo.png)](https://neurro-lab.engin.umich.edu/)

# Breaking the Barriers to Designing Online Experiments: A Novel Open-Source Platform for Supporting Procedural Skill Learning Experiments<!-- omit in toc -->

This repository contains a web application that provides researchers in the motor learning field with a way of creating and monitoring sequential finger-tapping experiments very easily. Researchers can create a new user profile, set up an experiment by selecting from a set of options, and then distribute the experiment as needed by just sending a link. Participants will be able to do the experiments from their own personal computers. Researchers can then track an experiment responses and download the participants data in a processing-friendly format. We hope that this tool allows researchers in the motor learning field to quickly test hypotheses without the hassle of having to bring subjects into a laboratory.

The web app is accessible at https://experiments.neurro-lab.engin.umich.edu/, and an example experiment is available [here](TODO). Go to [How to use](#how-to-use) for a guide on how to use the platform.

<!-- TODO: example experiment -->

![app_gif](doc/webapp.gif)

## Citation<!-- omit in toc -->

If you use this software, please cite it as below.

## Table of contents<!-- omit in toc -->

- [How to use](#how-to-use)
- [Run locally](#run-locally)
  - [Dependencies](#dependencies)
  - [Usage](#usage)
- [Contributing](#contributing)
  - [Understanding the code](#understanding-the-code)
- [Known issues and future work](#known-issues-and-future-work)
- [Contact](#contact)
- [License](#license)

## How to use

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

Once you are happy with the number of responses, and want to stop people from participating, you can disable the experiment by clicking on `Disable` next to the experiment. You can also download the participants' data for further processing. Three different files per experiment are available: `Raw data`, which contains the timestamp for each keypress in the experiment and could be used for fine detail analysis; `Processed data` aggregates data per trials and gives information about tapping speed and execution time for each one; `Survey data` contains the end survey information across all subjects, which can be used for demographic analyses. A subset of the resulting `csv` file for the `Processed data` is shown below, and a description for each column on each file can be seen below as well.

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

## Run locally

### Dependencies

**Google Cloud Storage**

To upload videos and consent forms

### Usage

## Contributing

### Understanding the code

**Django**

**Javascript**

**Vue**

## Known issues and future work

## Contact

If you have any issues, please create a new issue in the repository, or contact Luis Cubillos at lhcubill@umich.edu.

## License

See the [License.md](License.md) file for license rights and limitations (MIT).
