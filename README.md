![](https://i.imgur.com/kN6uOZN.png)


# ChaosXploit

###### tags: `Security Chaos Engineering`, `Chaos Engineering`, `Cybersecurity` 

 
ChaosXploit is a Security Chaos Engineering powered framework composed of different modules that support the application of Chaos Engineering methodology to test security in different kinds of information systems.

## QuickStart

To perform the complete Chaosxploit actions and experiments, it is necessary to prepare the environment using Python 3.7. 
Once the environment is configured, there are two ways to run Chaosxploit experiments: 1) using Chaostoolkit to automate all the desired actions, and 2) manually running the actions.

### 1) Installation using ChaosToolkit
To get started with this process, it is important to install Chaos Toolkit by following the instructions provided in their [documentation](https://chaostoolkit.org/reference/usage/install/). This installation involves:
 Installing the required Python environments
 ```sh
sudo apt-get install python3.7 python3.7-venv
```
Creating an environment, 
 ```sh
python3 -m venv ~/.venvs/chaostk
```
Activating the environment,
```sh
source  ~/.venvs/chaostk/bin/activate
```
And finally, installing the CLI for ChaosToolkit:
```sh
pip install -U chaostoolkit
```
Now, it is time to install ChaosXploit. First, clone this repository inside the python libraries folder:

```sh
cd ~/.venvs/chaostk/lib64/python3.7/site-packages
git clone https://github.com/SaraPalaciosCh/ChaosXploit.git
```
Once cloned, install all requirements:
```sh
cd ChaosXploit
python3.7 -m pip install -r requirements.txt
```
#### 1.1) Execution with ChaosToolkit
After the installation, it is possible to perform automated Chaosxploit experiments. One such experiment currently available involves performing a scan on a list of AWS buckets to determine if they are well-configured or not. 

To get started, navigate to the folder where the experiment statement is located.
```sh
cd Examples/Scaning_buckets/
```
There you will find the experiment statement, which is named `find_collectable.json`, as well as a test listing file named `selected.json`. The `selected.json` file has a specific format that helps us to define the steady state of the experiment:
```json
{
    <bucket_name>:{"SS_Collectable": true, "SS_ACL_Collectable": true}
}
```
In order to ensure the accuracy of the experiment, it is essential that both tags, "SS_Collectable" and "SS_ACL_Collectable," are initially set to true. This will allow us to assume that our configurations are correct. When running the experiment, it will be possible to identify if any of them have been misconfigured by the change in the truth value of these parameters.

