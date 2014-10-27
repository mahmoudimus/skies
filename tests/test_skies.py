import json
import troposphere
import skies

"""


"Mappings" : {
    "AWSInstanceType2Arch" : {
      "m1.small"   : { "Arch" : "64" },
      "m1.medium"  : { "Arch" : "64" },
      "m1.large"   : { "Arch" : "64" },
      "m1.xlarge"  : { "Arch" : "64" },
      "m2.xlarge"  : { "Arch" : "64" },
      "m2.2xlarge" : { "Arch" : "64" },
      "m2.4xlarge" : { "Arch" : "64" },
      "c1.medium"  : { "Arch" : "64" },
      "c1.xlarge"  : { "Arch" : "64" }
    },
    "AWSRegionArch2AMI" : {
      "us-east-1"      : {"64" : "ami-7614ac1e"},
      "us-west-1"      : {"64" : "ami-2f43566a"},
      "us-west-2"      : {"64" : "ami-e5f7bbd5"},
      "eu-west-1"      : {"64" : "ami-32228e45"},
      "ap-southeast-1" : {"64" : "ami-c6634294"},
      "ap-southeast-2" : {"64" : "ami-995c31a3"},
      "ap-northeast-1" : {"64" : "ami-73d0e672"},
      "sa-eas-1"       : {"64" : "ami-77a1156a"}
   }
}

"Parameters": {
   "Tag": {
       "Default": "bcmdr",
       "Type": "String",
       "Description": "Stack tag"
   },
   "ChefRole": {
       "Default": "balanced-commander",
       "Type": "String",
       "Description": "Configuration role name"
   },
   "DesiredCapacity": {
       "Default": "1",
       "Type": "Number",
       "Description": "Desired instance count"
   },
   "AppEnv": {
       "Default": "integration",
       "Type": "String",
       "Description": "Application environment",
       "AllowedValues": [
           "integration",
           "live",
           "dev"
       ]
   }
}

"ImageId" : {"Fn::FindInMap" : [ "AWSRegionArch2AMI", { "Ref" :
                                 "AWS::Region" }, { "Fn::FindInMap" :
                                 [ "AWSInstanceType2Arch", { "Ref" :
                                 "InstanceType" }, "Arch" ] ]}}

architecture = AWSInstanceType2Arch[Ref("InstanceType")]["Arch"]
AWSRegionArch2AMI[Ref("AWS::Region")][architecture]


class AWSRegion(AWSProvided):
   __name__ = 'AWS::Region'


class InstanceType(Parameter):
    Type = 'String'
    Description = 'Instance type'


class AWSInstanceType2Arch(Mapping):
    m1_small = Item('m1.small', {'Arch': '64'})


mapping:
  AWSInstanceType2Arch:
    - m1.small:

AWSRegionArch2AMI[AWSRegion][AWSInstanceType2Arch[InstanceType]['Arch']]

AWSRegionArch2AMI(AWSRegion)[AWSInstanceType2Arch(InstanceType)['Arch']]


class If_InUSEast1(Condition):
    expr = (AWSRegion == 'us-east'1)


"""


# Parameter(
#         'InstanceType',
#         Description='Instance type',
#         Type='String',
#         AllowedValues=['t1.micro', 'm1.medium', 'm1.large', 'c1.medium'],
#         Default='m1.large',
#     )

#
#
# class AWSRegion(skies.AWSProvided):
#    __name__ = 'AWS::Region'



#
#
# class AWSInstanceType2Arch(skies.Mapping):
#     m1_small = Item('m1.small', {'Arch': '64'})

import troposphere as ts
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb

atlas = None


@skies.common_parameters  # <- can modify Template.Parameters below
@skies.configurations
class PypiStack(skies.Template):
    """pypi"""  # <- this is the template description


    @skies.config_params   # <- Operates directly on the Parameter class
    class Parameters(skies.Parameter):

        prefix = skies.fields.StringParameter(Description='naming prefix',
                                              Default='pypi')

    @skies.conditions
    class Conditions(object):

        HasConf = ts.Not(ts.Equals(ts.Ref('ConfVer'), ''))

    #: CloudFormation - Mapping
    Mappings = skies.Mapping  # can do a cls var assignment of a template part

    # resources

    class PypiSecurityGroup(skies.resources.SecGrp):
        ALLOW_IN = [
            # by deafult, all SG fields have their cidrs bound to vpc_cidr
            # TODO: is Bound a good name? Supposed to signal that a variable
            #       will bet set later when the template is bound
            skies.fields.TCP(from_='80', to_='80', cidrs=skies.fields.Bound('vpc_cidr')),
            # can also accept a troposphere security group
            ts.ec2.SecurityGroupRule('Pypi',
                                     IpProtocol='tcp',
                                     FromPort='80',
                                     ToPort='80',
                                     CidrIp=atlas.vpc_cidr), # CidrIP must be explicitly declared (can not be bound)
        ]

        ALLOW_OUT = skies.fields.ALL  # by default, it's ALL


    # the name of the class can be set by __name__ or it is translated from
    # CamelCase to snake_case, so: PypiLaunchConfig -> pypi_launch_config
    class PypiLaunchConfig(skies.resources.LaunchConfig):
        SECURITY_GROUPS = [PypiSecurityGroup] # <- relationship with Pypi SG has auto references


    # you can use method invocation to create direct relationships
    # PypiScaleGroup has a reference to PypiLaunchConfig
    PypiScaleGroup = PypiLaunchConfig.scaling_group('PypiScaleGroup')

    # if PypiScaleGroup above, was created via inheritance, you can use
    # the scaling group params decorator below.
    #
    #  @Parameters.parameterize(MinSize='MIN_SIZE')
    #  class PypiScaleGroup(skies.resources.ScaleGroup):
    #      LAUNCH_CONFIGURATION = PypiLaunchConfig
    #      MIN_SIZE = 1
    #      MAX_SIZE = 1
    # You have to remember to add the reference parameters that aren't found
    # in Parameters first.
    Parameters.parameterize(MinSize='MIN_SIZE')(PypiScaleGroup)


    class PypiElb(skies.resources.EXTERNAL_HTTPS_ELB):
        EXPOSED_PORT = '443'  # default
        ALLOW_IN = [ ] # same as before
        # extracts attribute 'ssl_cert_id' from the atlas that binds to this
        # template
        SSL_CERT = skies.fields.Bound('ssl_cert_id')

        # TS health check
        HEALTH_CHECK = elb.HealthCheck(Target='TCP:443',
                                       HealthyThreshold='3',
                                       UnhealthyThreshold='5',
                                       Interval='30',
                                       Timeout='5')



    




class Pypi(Template):  # template = tsp.Template()
    # template.add_description('Pypi')
    """
    a cloudformation template that provisions a high performance devpi
    service.
    """

    # template.add_parameter([
    #     tsp.Parameter(
    #         'Prefix',
    #         Description='Naming prefix.',
    #         Type='String',
    #         Default='pypi',
    #     ),
    # ])
    @skies.parameter(name='Prefix', param_type='String')
    def prefix(self):
        """Naming prefix."""
        return {'Default': 'pypi'}

    # TODO:
    # atlas.infra_params(template)  # ssh_key, Env, Silo
    # atlas.conf_params(template)   # Conf Name, Conf Version, Conf tarball bucket
    # atlas.conditions(template)
    # atlas.instance_params(template, roles_default=['pypi'], iam_default='pypi')
    # atlas.scaling_params(template)
    # atlas.mappings(template, accounts=[atlas.poundpay, atlas.balanced_vault])


    # pypi_secgrp = atlas.instance_secgrp(
    #     template,
    #     name='Pypi',
    #     SecurityGroupIngress=[
    #         tsp.ec2.SecurityGroupRule(
    #             'Pypi',
    #             IpProtocol='tcp',
    #             FromPort='80',
    #             ToPort='80',
    #             CidrIp=atlas.vpc_cidr,
    #         ),
    #     ]
    # )
    @skies.secgrp_ingress(protocol='tcp', from_port='80', to_port='80')
    def pypi_secgrp(self):
        """pypi"""

    # atlas.cfn_auth_metadata(i_meta_data)
    @skies.auth_metadata()
    def auth_metadata(self):
        return 'pass'

    # atlas.cfn_init_metadata(i_meta_data)
    @skies.init_metadata()
    def init_metadata(self):
        return 'pass'

    # i_user_data = tsp.Join(
    #     '',
    #     atlas.user_data('PypiLaunchConfiguration') +
    #     atlas.user_data_signal_on_scaling_failure(),
    # )
    @skies.user_data()
    def user_data(self):
        return tsp.Join(
            '',
            user_data('PypiLaunchConfiguration') +
            user_data_signal_on_scaling_failure(),
        )

    @skies.launch_config()
    def pypi_launch_config(self):



# launch configuration

i_launchconf = atlas.instance_launchconf(
    template,
    name='Pypi',
    UserData=tsp.Base64(i_user_data),
    Metadata=i_meta_data,
    SecurityGroups=[tsp.Ref(pypi_secgrp)],
)


atlas.external_lb(template,
    name='PypiHTTP',
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            'HTTPS',
            IpProtocol='tcp',
            FromPort='443',
            ToPort='443',
            CidrIp='0.0.0.0/0'
        )
    ],
    Listeners=[
        elb.Listener(
            LoadBalancerPort='443',
            InstancePort='443',
            Protocol='HTTPS',
            InstanceProtocol='HTTPS',
            SSLCertificateId=tsp.Join('', [
                'arn:aws:iam::',
                tsp.Ref('AWS::AccountId'),
                ':server-certificate/',
                atlas.ssl_cert_id,
            ]),
        ),
    ],
    HealthCheck=elb.HealthCheck(
        Target='TCP:443',
        HealthyThreshold='3',
        UnhealthyThreshold='5',
        Interval='30',
        Timeout='5',
    )
)

# scale group
scaling_group = atlas.instance_scalegrp(
    template,
    name='Pypi',
    LaunchConfigurationName=tsp.Ref(i_launchconf),
    MinSize=tsp.Ref('MinSize'),
    MaxSize=tsp.Ref('MaxSize'),
    DesiredCapacity=tsp.Ref('DesiredCapacity'),
)


def test_string_parameters():
    class InstanceType(skies.StringParameter):
        """Instance type"""
        AllowedValues = [
            't1.micro',
            'm1.medium',
            'm1.large',
            'c1.medium'
        ]

        Default = 'm1.large'

    x = troposphere.Parameter(
            'InstanceType',
            Description='Instance type',
            Type='String',
            AllowedValues=['t1.micro', 'm1.medium', 'm1.large', 'c1.medium'],
            Default='m1.large',
        )
    print x.JSONrepr()
    assert InstanceType().JSONrepr() == x.JSONrepr()


def test_template_construction():
    class T(object):

        @skies.parameter(name='InstanceType')
        def instance_type(self):
            pass

        @skies.condition()
        def InUSEast1(self):
            pass

        InstanceType = skies.parameter()(lambda x: x)