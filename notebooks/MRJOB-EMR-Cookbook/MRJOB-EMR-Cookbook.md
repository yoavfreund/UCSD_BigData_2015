### Finding an available flow

- To get a list of dataflows and their status `utils/find_waiting_flow.py`.  This script will print out a list of currently available job-flows, and will also return that information as a list of dictionaries. Each dictionary consists of:
  - **node:** u'ec2-54-161-53-198.compute-1.amazonaws.com', 
              Use this to ssh into the head node and to read from a file on HDFS
  - **flow_state:** u'WAITING', Start flows only on job flows that are WAITING 
  - **flow_id**: u'j-2YTN78MP8WQG9', the ID of the job flow.

- The job flows are sorted so that the WAITING job-flows appear before those that are RUNNING.

### Sending files into and out of your job
#### Input files
###### stdin
`stdin` represents the large files that are fed into the mappers. The input file is defined by the (non-flag) parameter when running the mrjob program.

There are three possibilities for the location on the input file. In general, the recommendation is to use S3.

- **local file**: simply give the local path to the file. You can also pipe it as standard input. Use only for debugging using small files, as the upload time from your computer to the cloud will otherwise be prohibitive.
- **S3**: Provide the s3 file or directory as a parameter to the the mrjob script. If you provide a directory it will use as input all of the files in the directory (recall that in map-reduce the order of the input does not matter). Examples: 
  - `s3://yoavfreunddefault/simple_mrjob/` for a directory.
  - `s3://yoavfreunddefault/simple_mrjob/part-00000` for a single file
- **HDFS**: If a file has been mounted on hdfs for you (this is done by the TAs) then you can access it by specifying `hdfs://'+node+':9000/weather.raw_data/ALL.csv` where "node" is the DNS name of the namenode for the job-flow you are using (provided by the script `find_waiting_flow` above.)

###### Other input files
- If you want to upload files to the directory in which the task is executed you can use the `--file` option on the command line.
- If you want to provide you tasks with data files whose name will be determined at run time (for example: centroid locations in kmeans). You do that by defining a  new parameter using the `add_file_option` in mrjob. For example:
```python
def configure_options(self):
  super(SqliteJob, self).configure_options()
  self.add_file_option('--database')
```
You can then give the parameter `--database` on the command line. This file can be local or on S3. Mrjob will do the work involved in making this file available to the tasks on EMR.  

Inside the task you access the file usin the command

```python
file=open(self.options.database)
```

- You cannot write to a file in hdfs. Any file that you want to maintain between runs

### Work Environment
- Pandas, scikit-learn, numpy etc are now pre installed in the clusters. You can manually install any new package that you might require by sshing into the namenode as explained [here](HadoopClusterAccess)
  You can manually import files to hdfs after sshing into the namenode as well.
- Entire s3 directory can be read as input by giving the s3 directory path as input alongwith the forward slash i.e $input = s3://dse-sachin/inp_directory/ - Thanks Jennifer
- Its generally helpful to profile your code to optimize execution time. Kevin has explained it in HipChat and you can read more on profilers here - Profilers - Thanks Kevin
