
###Hadoop Cluster Access###

I am attaching herewith my ec2keyPair file which should give you all access to the hadoop clusters. sachin_student_sachinAspireE5571P_1426883088.pem. this file will only give you access to plug into the created clusters, but creating new clusters still require my logins :p
 
You can ssh into the cluster as follows

``` 
   ssh -i /pathToFile/sachin_student_sachin-Aspire-E5-571P_1426883088.pem hadoop@nodeName
```

nodeName is the job.masterPublicDnsName of the cluster i.e. `ec2-52-5-188-73.compute-1.amazonaws.com`


Once you are logged into the namenode you can access the HDFS file file system using commands of the form

```
 hadoop fs -(shell code)
```

for example:

```
 hadoop fs -mkdir /student_folder/
 hadoop fs -ls /student_folder/
 hadoop fs -chmod -R 777 /student_folder/*
```

To get help on the file system commands use

 ``` 
 hadoop fs --help 
 ```

Note that these files exist only as long as the node survives. We suggest that you keep a copy of the files locally or on s3.
 
To upload files to the cluster you can use `scp` from local system or use `wget` from your s3 folder after uploading there.
