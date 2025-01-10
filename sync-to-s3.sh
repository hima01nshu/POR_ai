#!/bin/bash
/usr/local/bin/aws s3 sync /home/hprajap2 s3://s3sthprajap2/hprajap2 --exact-timestamps
/usr/local/bin/aws s3 sync /home/ec2-user s3://s3sthprajap2/Ec2-User --exact-timestamps
