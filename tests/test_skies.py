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